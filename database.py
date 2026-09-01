import hashlib
import json
import os
import base64
import io
import pandas as pd
from datetime import datetime
from PIL import Image

try:
    import gspread
    from google.oauth2.service_account import Credentials
    import streamlit as st
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

def clean_private_key(key):
    if not key: return key
    key = key.replace("\\n", "\n")
    if not key.endswith("\n"): key += "\n"
    return key

def get_gsheet_client():
    if not GSPREAD_AVAILABLE: return None
    try:
        creds_dict = None
        if "gcp_json" in st.secrets:
            creds_dict = json.loads(st.secrets["gcp_json"])
        elif "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = clean_private_key(creds_dict["private_key"])

        if creds_dict:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(credentials)
        return None
    except Exception:
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("users")
            records = sheet.get_all_records()
            return {str(r["username"]): str(r["password_hash"]) for r in records}
        except Exception: pass
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: return json.load(f)
    return {"admin": hash_password("1234")}

def save_user(username, password_hash):
    client = get_gsheet_client()
    saved_to_gsheet = False
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("users")
            sheet.append_row([username, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            saved_to_gsheet = True
        except Exception: pass
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: users = json.load(f)
    users[username] = password_hash
    with open("users.json", "w") as f: json.dump(users, f, indent=4)
    return saved_to_gsheet

def file_to_base64(uploaded_file):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode in ("RGBA", "P"): image = image.convert("RGB")
            image = image.rotate(-90, expand=True)
            image.thumbnail((500, 500))
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=75)
            encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
            if len(encoded) > 48000:
                buffered = io.BytesIO()
                image.thumbnail((400, 400))
                image.save(buffered, format="JPEG", quality=60)
                encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
        except Exception: return ""
    return ""

def get_or_create_worksheet(client, sheet_name, default_cols):
    try:
        sheet = client.open("Streamlit_DB").worksheet(sheet_name)
    except Exception:
        spreadsheet = client.open("Streamlit_DB")
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
        sheet.append_row(default_cols)
    return sheet

def load_fit_items():
    client = get_gsheet_client()
    default_cols = ['id', 'owner', 'recipient', 'type', 'image_url', 'collection']
    if not client: return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitItems", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1: return pd.DataFrame(columns=default_cols)
        headers = rows[0]
        if 'collection' not in headers:
            sheet.update_cell(1, 6, 'collection')
            headers.append('collection')
        data = [r[:len(headers)] + [""] * (len(headers) - len(r)) for r in rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        for col in default_cols:
            if col not in df.columns: df[col] = ""
        df['collection'] = df['collection'].fillna("").apply(lambda x: str(x).strip().capitalize())
        return df
    except Exception: return pd.DataFrame(columns=default_cols)

def load_fit_ratings():
    client = get_gsheet_client()
    default_cols = ['combo_id', 'rater', 'rating', 'notes']
    if not client: return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitRatings", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1: return pd.DataFrame(columns=default_cols)
        headers = rows[0]
        if 'rater' not in headers:
            try: sheet.update_cell(1, len(headers)+1, 'rater'); headers.append('rater')
            except Exception: pass
        data = [r[:len(headers)] + [""] * (len(headers) - len(r)) for r in rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        for col in default_cols:
            if col not in df.columns: df[col] = ""
        return df
    except Exception: return pd.DataFrame(columns=default_cols)

def batch_update_fit_items(updates_list):
    """Met à jour plusieurs items d'un seul coup (ID, Recipient, Collection)"""
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            updates_dict = {str(u[0]): (u[1], u[2]) for u in updates_list}
            
            for idx, row in enumerate(rows):
                if row and row[0] in updates_dict:
                    new_recip, new_col = updates_dict[row[0]]
                    sheet.update_cell(idx + 1, 3, new_recip)
                    sheet.update_cell(idx + 1, 6, new_col)
            return True, ""
        except Exception as e: return False, str(e)
    return False, "Google Sheets non connecté."

def delete_fit_item(item_id):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            for idx, row in enumerate(rows):
                if row and row[0] == str(item_id):
                    if hasattr(sheet, "delete_rows"): sheet.delete_rows(idx + 1)
                    else: sheet.delete_row(idx + 1)
                    return True, ""
        except Exception as e: return False, str(e)
    return False, "Erreur."

def update_collection_recipients(collection_name, owner, new_recipients):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            for idx, row in enumerate(rows):
                if idx == 0: continue
                col_val = str(row[5]).strip().capitalize() if len(row) > 5 else ""
                if len(row) > 1 and row[1] == owner and col_val == collection_name.capitalize():
                    sheet.update_cell(idx + 1, 3, new_recipients)
            return True, ""
        except Exception as e: return False, str(e)
    return False, "Erreur."

def delete_full_collection(collection_name, owner):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            indices_to_delete = []
            for idx, row in enumerate(rows):
                if idx == 0: continue
                col_val = str(row[5]).strip().capitalize() if len(row) > 5 else ""
                if len(row) > 1 and row[1] == owner and col_val == collection_name.capitalize():
                    indices_to_delete.append(idx + 1)
            for row_idx in reversed(indices_to_delete):
                if hasattr(sheet, "delete_rows"): sheet.delete_rows(row_idx)
                else: sheet.delete_row(row_idx)
            return True, ""
        except Exception as e: return False, str(e)
    return False, "Erreur."

# ==========================================
# FONCTIONS POUR LE SYSTÈME 2 (BOURSE)
# ==========================================

def load_stock_transactions():
    client = get_gsheet_client()
    default_cols = ['id', 'owner', 'ticker', 'date', 'quantity', 'buy_price', 'trans_type']
    if not client: return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "StockTransactions", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1: return pd.DataFrame(columns=default_cols)
        
        headers = rows[0]
        # Ajouter la colonne trans_type si elle n'existait pas
        if 'trans_type' not in headers:
            try: 
                sheet.update_cell(1, len(headers)+1, 'trans_type')
                headers.append('trans_type')
            except Exception: pass
            
        data = [r[:len(headers)] + [""] * (len(headers) - len(r)) for r in rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0.0)
        
        if 'trans_type' in df.columns:
            df['trans_type'] = df['trans_type'].replace("", "Achat")
        else:
            df['trans_type'] = "Achat"
            
        return df
    except Exception: 
        return pd.DataFrame(columns=default_cols)

def add_stock_transaction(owner, ticker, date_str, quantity, price, trans_type="Achat"):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("StockTransactions")
            new_id = str(int(datetime.now().timestamp() * 1000))
            sheet.append_row([new_id, owner, str(ticker).upper(), str(date_str), str(quantity), str(price), trans_type])
            return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Google Sheets non connecté."

def delete_stock_transaction(trans_id):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("StockTransactions")
            rows = sheet.get_all_values()
            for idx, row in enumerate(rows):
                if row and row[0] == str(trans_id):
                    if hasattr(sheet, "delete_rows"): sheet.delete_rows(idx + 1)
                    else: sheet.delete_row(idx + 1)
                    return True, ""
        except Exception as e: return False, str(e)
    return False, "Erreur."

# ==========================================================
# SYSTÈME 3 — PRÉFÉRENCES
# ==========================================================

def load_system3_preferences(username):
    """
    Charge les catégories et intérêts permanents d'un utilisateur
    depuis Google Sheets.
    """

    client = get_gsheet_client()

    default_categories = {
        "🌎 Monde": [
            "Géopolitique",
            "Guerres",
            "Politique internationale",
            "Chine"
        ],
        "🇨🇦 Canada": [
            "Politique fédérale",
            "Économie canadienne",
            "Énergie"
        ],
        "⚜️ Québec": [
            "Politique québécoise",
            "Hydro-Québec",
            "Économie du Québec"
        ],
        "🤖 Robotique": [
            "Robotique humanoïde",
            "ROS2",
            "Vision par ordinateur",
            "Automatisation industrielle",
            "Robots industriels"
        ],
        "💰 Économie": [
            "Inflation",
            "Taux d'intérêt",
            "Banque du Canada",
            "Dollar canadien"
        ]
    }

    if not client or not username:
        return default_categories

    try:
        sheet = get_or_create_worksheet(
            client,
            "System3Preferences",
            ["username", "category", "interest"]
        )

        rows = sheet.get_all_records()

        user_rows = [
            row for row in rows
            if str(row.get("username", "")).strip() == str(username).strip()
        ]

        # Nouvel utilisateur :
        # on crée ses préférences par défaut
        if not user_rows:

            save_system3_preferences(
                username,
                default_categories
            )

            return default_categories

        categories = {}

        for row in user_rows:

            category = str(
                row.get("category", "")
            ).strip()

            interest = str(
                row.get("interest", "")
            ).strip()

            if not category:
                continue

            if category not in categories:
                categories[category] = []

            if interest and interest not in categories[category]:
                categories[category].append(interest)

        return categories

    except Exception:
        return default_categories


def save_system3_preferences(username, categories):
    """
    Sauvegarde définitivement les préférences de Système 3
    dans Google Sheets.
    """

    client = get_gsheet_client()

    if not client or not username:
        return False, "Google Sheets non connecté."

    try:

        sheet = get_or_create_worksheet(
            client,
            "System3Preferences",
            ["username", "category", "interest"]
        )

        rows = sheet.get_all_values()

        # --------------------------------------------------
        # SUPPRIMER LES ANCIENNES PRÉFÉRENCES DE L'UTILISATEUR
        # --------------------------------------------------

        rows_to_delete = []

        for i, row in enumerate(rows[1:], start=2):

            if len(row) > 0 and str(row[0]).strip() == str(username).strip():
                rows_to_delete.append(i)

        # Supprimer du bas vers le haut
        for row_number in reversed(rows_to_delete):
            sheet.delete_rows(row_number)

        # --------------------------------------------------
        # AJOUTER LES NOUVELLES PRÉFÉRENCES
        # --------------------------------------------------

        new_rows = []

        for category, interests in categories.items():

            for interest in interests:

                new_rows.append([
                    username,
                    category,
                    interest
                ])

        if new_rows:
            sheet.append_rows(new_rows)

        return True, ""

    except Exception as e:
        return False, str(e)