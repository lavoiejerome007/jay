import streamlit as st
import hashlib
import json
import os
import base64
import io
import pandas as pd
from datetime import datetime
from PIL import Image

# Vérification de l'installation de gspread
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

st.set_page_config(page_title="Mon Application Web", page_icon="🚀", layout="wide")

# ==========================================
# FONCTIONS BASES DE DONNÉES / GOOGLE SHEETS
# ==========================================

def clean_private_key(key):
    """Nettoie la clé privée pour les anciennes méthodes de secrets."""
    if not key:
        return key
    key = key.replace("\\n", "\n")
    if not key.endswith("\n"):
        key += "\n"
    return key

def get_gsheet_client():
    """Connexion robuste à Google Sheets via JSON brut."""
    if not GSPREAD_AVAILABLE:
        return None
        
    try:
        creds_dict = None
        if "gcp_json" in st.secrets:
            creds_dict = json.loads(st.secrets["gcp_json"])
        elif "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = clean_private_key(creds_dict["private_key"])

        if creds_dict:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
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
            users_dict = {}
            for r in records:
                users_dict[str(r["username"])] = str(r["password_hash"])
            return users_dict
        except Exception:
            pass
    
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {"admin": hash_password("1234")}

def save_user(username, password_hash):
    client = get_gsheet_client()
    saved_to_gsheet = False
    
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("users")
            sheet.append_row([username, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            saved_to_gsheet = True
        except Exception:
            pass

    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    users[username] = password_hash
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)
        
    return saved_to_gsheet

def file_to_base64(uploaded_file):
    """Convertit, optimise et sécurise la taille de l'image pour Google Sheets."""
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
                
            image.thumbnail((500, 500))
            
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=75)
            encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Sécurité anti-dépassement de la limite Google Sheets (50k caractères par cellule)
            if len(encoded) > 48000:
                buffered = io.BytesIO()
                image.thumbnail((400, 400))
                image.save(buffered, format="JPEG", quality=60)
                encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
            return f"data:image/jpeg;base64,{encoded}"
        except Exception:
            return ""
    return ""

def get_or_create_worksheet(client, sheet_name, default_cols):
    """Récupère ou crée automatiquement un onglet Google Sheets avec ses en-têtes."""
    try:
        sheet = client.open("Streamlit_DB").worksheet(sheet_name)
    except Exception:
        spreadsheet = client.open("Streamlit_DB")
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
        sheet.append_row(default_cols)
    return sheet

def load_fit_items():
    """Charge les pièces de linge (chandails et pantalons)."""
    client = get_gsheet_client()
    default_cols = ['id', 'owner', 'recipient', 'type', 'image_url']
    if not client:
        return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitItems", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1:
            return pd.DataFrame(columns=default_cols)
        headers = rows[0]
        df = pd.DataFrame(rows[1:], columns=headers)
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

def load_fit_ratings():
    """Charge les notes et commentaires des combinaisons."""
    client = get_gsheet_client()
    default_cols = ['combo_id', 'rating', 'notes']
    if not client:
        return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitRatings", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1:
            return pd.DataFrame(columns=default_cols)
        headers = rows[0]
        df = pd.DataFrame(rows[1:], columns=headers)
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

# ==========================================
# GESTION DE LA SESSION & NAVIGATION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Accueil"

# ==========================================
# PAGE DE CONNEXION / INSCRIPTION
# ==========================================

if not st.session_state["logged_in"]:
    st.title("🔐 Bienvenue sur votre Application")
    st.markdown("Connectez-vous ou créez un compte pour accéder à vos systèmes.")
    
    tab_login, tab_register = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])
    
    with tab_login:
        user_input = st.text_input("Nom d'utilisateur", key="login_user")
        pass_input = st.text_input("Mot de passe", type="password", key="login_pass")
        
        if st.button("Connexion", type="primary"):
            users = load_users()
            if user_input in users and users[user_input] == hash_password(pass_input):
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_input
                st.session_state["current_page"] = "Accueil"
                st.success(f"Bienvenue {user_input} !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
                
    with tab_register:
        new_user = st.text_input("Nouveau nom d'utilisateur", key="reg_user")
        new_pass = st.text_input("Nouveau mot de passe", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirmer le mot de passe", type="password", key="reg_confirm")
        
        if st.button("S'inscrire"):
            users = load_users()
            if not new_user or not new_pass:
                st.warning("Veuillez remplir tous les champs.")
            elif new_user in users:
                st.error("Ce nom d'utilisateur existe déjà.")
            elif new_pass != confirm_pass:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                saved_online = save_user(new_user, hash_password(new_pass))
                if saved_online:
                    st.success("✅ Compte créé et enregistré sur Google Sheets !")
                else:
                    st.success("⚠️ Compte créé localement.")

# ==========================================
# APPLICATION PRINCIPALE (CONNECTÉ)
# ==========================================

else:
    with st.sidebar:
        with st.container(border=True):
            st.markdown(f"**Bienvenue**<br>`{st.session_state['username']}`", unsafe_allow_html=True)
            if st.button("👤 Mon Profil", use_container_width=True):
                st.session_state["current_page"] = "Profil"
                st.rerun()

        st.divider()

        st.subheader("🛠️ Utilitaires")
        if st.button("🏠 Tableau de bord", use_container_width=True):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        with st.expander("📊 Statistiques rapides"):
            st.metric("Systèmes actifs", "9 / 9")
            st.metric("Statut Cloud", "Connecté" if get_gsheet_client() else "Local")

        st.divider()

        if st.button("🚪 Se déconnecter", type="secondary", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["current_page"] = "Accueil"
            st.rerun()

    page = st.session_state["current_page"]

    # --- PAGE ACCUEIL : GRILLE 3x3 DES SYSTÈMES ---
    if page == "Accueil":
        st.title("🎛️ Tableau de Bord des Systèmes")
        st.markdown("Sélectionnez un système ci-dessous pour ouvrir son espace dédié.")
        st.write("")

        systems = [
            "Système 1", "Système 2", "Système 3",
            "Système 4", "Système 5", "Système 6",
            "Système 7", "Système 8", "Système 9"
        ]

        for i in range(0, 9, 3):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.container(border=True):
                    st.subheader(systems[i])
                    title_name = "Fit-Note" if i == 0 else "Accéder au module."
                    st.write(title_name)
                    if st.button(f"Ouvrir {systems[i]}", key=f"btn_{i}", use_container_width=True):
                        st.session_state["current_page"] = systems[i]
                        st.rerun()
                        
            with col2:
                with st.container(border=True):
                    st.subheader(systems[i+1])
                    st.write("Accéder au module.")
                    if st.button(f"Ouvrir {systems[i+1]}", key=f"btn_{i+1}", use_container_width=True):
                        st.session_state["current_page"] = systems[i+1]
                        st.rerun()
                        
            with col3:
                with st.container(border=True):
                    st.subheader(systems[i+2])
                    st.write("Accéder au module.")
                    if st.button(f"Ouvrir {systems[i+2]}", key=f"btn_{i+2}", use_container_width=True):
                        st.session_state["current_page"] = systems[i+2]
                        st.rerun()
            st.write("")

    # --- PAGE PROFIL ---
    elif page == "Profil":
        if st.button("← Retour au tableau de bord"):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        st.title("👤 Gestion du Profil")
        st.write(f"Nom d'utilisateur connecté : **{st.session_state['username']}**")
        st.info("Espace dédié à la configuration de ton profil utilisateur.")

    # --- PAGE SYSTÈME 1 : FIT-NOTE ---
    elif page == "Système 1":
        if st.button("← Retour au tableau de bord"):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        st.title("👕 Fit-Note")
        
        tab_view, tab_rate, tab_add = st.tabs(["👁️ Visualiser", "⭐ Noter", "➕ Ajouter"])
        
        client = get_gsheet_client()
        items_df = load_fit_items()
        ratings_df = load_fit_ratings()

        # --- TAB AJOUTER ---
        with tab_add:
            st.subheader("Ajouter une pièce de linge")
            
            item_type = st.selectbox("Type de vêtement", ["Chandail (Haut)", "Pantalon (Bas)"])
            item_file = st.file_uploader("📸 Glisser ou sélectionner l'image", type=["png", "jpg", "jpeg"], key="item_up")
            
            recipient = st.text_input("Partager avec (nom d'utilisateur, optionnel) :")
            
            if st.button("Sauvegarder l'item"):
                if item_file:
                    with st.spinner("Traitement et vérification de l'image en cours..."):
                        img_b64 = file_to_base64(item_file)
                        type_val = "shirt" if "Chandail" in item_type else "pants"
                    
                    if client and img_b64:
                        sheet_items = get_or_create_worksheet(client, "FitItems", ['id', 'owner', 'recipient', 'type', 'image_url'])
                        new_id = len(items_df) + 1
                        sheet_items.append_row([str(new_id), st.session_state['username'], recipient.strip(), type_val, img_b64])
                        st.success("Pièce de linge enregistrée et partagée avec succès !")
                        st.rerun()
                    else:
                        st.error("Google Sheets non connecté ou erreur de traitement de l'image.")
                else:
                    st.warning("Veuillez importer une image avant de sauvegarder.")

        # Filtrer les items accessibles par l'utilisateur connecté
        if not items_df.empty:
            accessible_items = items_df[(items_df['owner'] == st.session_state['username']) | (items_df['recipient'] == st.session_state['username'])]
            shirts = accessible_items[accessible_items['type'] == 'shirt'].to_dict('records')
            pants = accessible_items[accessible_items['type'] == 'pants'].to_dict('records')
        else:
            shirts = []
            pants = []

        ratings_dict = {}
        if not ratings_df.empty:
            for _, r in ratings_df.iterrows():
                ratings_dict[str(r['combo_id'])] = {"rating": r['rating'], "notes": r['notes']}

        # --- TAB VISUALISER ---
        with tab_view:
            st.subheader("Toutes les combinaisons possibles (Chandails + Pantalons)")
            if not shirts or not pants:
                st.info("Ajoutez au moins un chandail et un pantalon (ou attendez des partages) pour voir les combinaisons.")
            else:
                for s in shirts:
                    for p in pants:
                        combo_id = f"S{s['id']}_P{p['id']}"
                        combo_data = ratings_dict.get(combo_id, {"rating": "0", "notes": ""})
                        
                        with st.container(border=True):
                            if s['image_url']:
                                st.image(s['image_url'], width=500)
                            if p['image_url']:
                                st.image(p['image_url'], width=500)
                                
                            st.write(f"Créateur Chandail : `{s['owner']}` | Créateur Pantalon : `{p['owner']}`")
                            st.markdown(f"⭐ Note reçue : **{combo_data['rating']}/100**")
                            st.markdown(f"💬 Commentaire : *{combo_data['notes'] if combo_data['notes'] else 'Aucun commentaire'}*")

        # --- TAB NOTER ---
        with tab_rate:
            st.subheader("Noter les combinaisons de linge")
            if not shirts or not pants:
                st.info("Aucune combinaison disponible à noter pour le moment.")
            else:
                for s in shirts:
                    for p in pants:
                        combo_id = f"S{s['id']}_P{p['id']}"
                        combo_data = ratings_dict.get(combo_id, {"rating": "0", "notes": ""})
                        
                        with st.expander(f"Combinaison (Chandail #{s['id']} + Pantalon #{p['id']})"):
                            if s['image_url']:
                                st.image(s['image_url'], width=500)
                            if p['image_url']:
                                st.image(p['image_url'], width=500)
                            
                            try:
                                current_rating = int(combo_data['rating'])
                            except ValueError:
                                current_rating = 0
                                
                            new_rating = st.number_input("Note /100", min_value=0, max_value=100, value=current_rating, key=f"rate_{combo_id}")
                            new_note = st.text_input("Commentaire", value=str(combo_data['notes']), key=f"note_{combo_id}")
                            
                            if st.button("Enregistrer la note", key=f"save_{combo_id}"):
                                if client:
                                    sheet_ratings = get_or_create_worksheet(client, "FitRatings", ['combo_id', 'rating', 'notes'])
                                    rows = sheet_ratings.get_all_values()
                                    
                                    found_row = None
                                    for idx, r in enumerate(rows[1:], start=2):
                                        if r and r[0] == combo_id:
                                            found_row = idx
                                            break
                                    
                                    if found_row:
                                        sheet_ratings.update_cell(found_row, 2, str(new_rating))
                                        sheet_ratings.update_cell(found_row, 3, str(new_note))
                                    else:
                                        sheet_ratings.append_row([combo_id, str(new_rating), str(new_note)])
                                        
                                    st.success("Note et commentaire mis à jour avec succès !")
                                    st.rerun()

    # --- PAGES DES AUTRES SOUS-SYSTÈMES (2 à 9) ---
    elif page.startswith("Système"):
        if st.button("← Retour au tableau de bord"):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        st.title(f"⚙️ {page}")
        st.markdown(f"Espace de travail et de configuration pour le **{page}**.")
        st.info("Ce module sera configuré prochainement.")