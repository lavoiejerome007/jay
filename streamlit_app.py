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
    if not key:
        return key
    key = key.replace("\\n", "\n")
    if not key.endswith("\n"):
        key += "\n"
    return key

def get_gsheet_client():
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
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
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
        except Exception:
            return ""
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
    if not client:
        return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitItems", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1:
            return pd.DataFrame(columns=default_cols)
        
        headers = rows[0]
        if 'collection' not in headers:
            sheet.update_cell(1, 6, 'collection')
            headers.append('collection')
            
        data = []
        for r in rows[1:]:
            while len(r) < len(headers):
                r.append("")
            data.append(r[:len(headers)])
            
        df = pd.DataFrame(data, columns=headers)
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
                
        df['collection'] = df['collection'].fillna("").apply(lambda x: str(x).strip().capitalize())
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

def load_fit_ratings():
    client = get_gsheet_client()
    default_cols = ['combo_id', 'rater', 'rating', 'notes']
    if not client:
        return pd.DataFrame(columns=default_cols)
    try:
        sheet = get_or_create_worksheet(client, "FitRatings", default_cols)
        rows = sheet.get_all_values()
        if not rows or len(rows) <= 1:
            return pd.DataFrame(columns=default_cols)
            
        headers = rows[0]
        if 'rater' not in headers:
            try:
                sheet.update_cell(1, len(headers)+1, 'rater')
                headers.append('rater')
            except Exception:
                pass
                
        data = []
        for r in rows[1:]:
            while len(r) < len(headers):
                r.append("")
            data.append(r[:len(headers)])
            
        df = pd.DataFrame(data, columns=headers)
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

def update_fit_item(item_id, new_recipient, new_collection):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            for idx, row in enumerate(rows):
                if row and row[0] == str(item_id):
                    sheet.update_cell(idx + 1, 3, new_recipient)
                    sheet.update_cell(idx + 1, 6, new_collection)
                    return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Google Sheets non connecté."

def delete_fit_item(item_id):
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("FitItems")
            rows = sheet.get_all_values()
            for idx, row in enumerate(rows):
                if row and row[0] == str(item_id):
                    if hasattr(sheet, "delete_rows"):
                        sheet.delete_rows(idx + 1)
                    else:
                        sheet.delete_row(idx + 1)
                    return True, ""
        except Exception as e:
            return False, str(e)
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
        except Exception as e:
            return False, str(e)
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
                if hasattr(sheet, "delete_rows"):
                    sheet.delete_rows(row_idx)
                else:
                    sheet.delete_row(row_idx)
            return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Erreur."

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
# APPLICATION PRINCIPALE
# ==========================================

if not st.session_state["logged_in"]:
    st.title("🔐 Bienvenue sur votre Application")
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
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
                
    with tab_register:
        new_user = st.text_input("Nouveau nom d'utilisateur", key="reg_user")
        new_pass = st.text_input("Nouveau mot de passe", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirmer", type="password", key="reg_confirm")
        if st.button("S'inscrire"):
            if new_pass != confirm_pass:
                st.error("Mots de passe différents.")
            else:
                save_user(new_user, hash_password(new_pass))
                st.success("Compte créé !")

else:
    with st.sidebar:
        with st.container(border=True):
            st.markdown(f"**Bienvenue**<br>`{st.session_state['username']}`", unsafe_allow_html=True)
            if st.button("👤 Mon Profil", use_container_width=True):
                st.session_state["current_page"] = "Profil"
                st.rerun()
        st.divider()
        if st.button("🏠 Tableau de bord", use_container_width=True):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
        st.divider()
        if st.button("🚪 Se déconnecter", type="secondary", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["current_page"] = "Accueil"
            st.rerun()

    page = st.session_state["current_page"]

    if page == "Accueil":
        st.title("🎛️ Tableau de Bord des Systèmes")
        systems = [f"Système {i}" for i in range(1, 10)]
        for i in range(0, 9, 3):
            cols = st.columns(3)
            for j in range(3):
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(systems[i+j])
                        st.write("Fit-Note" if (i+j) == 0 else "Accéder au module.")
                        if st.button(f"Ouvrir {systems[i+j]}", use_container_width=True):
                            st.session_state["current_page"] = systems[i+j]
                            st.rerun()

    elif page == "Profil":
        st.title("👤 Gestion du Profil")
        if st.button("← Retour"): st.session_state["current_page"] = "Accueil"; st.rerun()

    elif page == "Système 1":
        if st.button("← Retour au tableau de bord"):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        st.title("👕 Fit-Note")
        
        tab_view, tab_rate, tab_add, tab_items, tab_collections = st.tabs(["👁️ Visualiser", "⭐ Noter", "➕ Ajouter", "👕 Pièces", "📁 Collections"])
        
        client = get_gsheet_client()
        items_df = load_fit_items()
        ratings_df = load_fit_ratings()

        # --- TAB AJOUTER ---
        with tab_add:
            st.subheader("Ajouter une pièce de linge")
            item_type = st.selectbox("Type de vêtement", ["Chandail (Haut)", "Pantalon (Bas)"])
            
            # Récupérer les collections existantes de l'utilisateur pour alimenter le menu déroulant
            existing_cols = []
            if not items_df.empty:
                user_items_for_cols = items_df[items_df['owner'] == st.session_state['username']]
                existing_cols = sorted([c for c in user_items_for_cols['collection'].unique() if c.strip() != ""])
            
            col_choice_options = ["-- Aucune / Nouvelle collection --"] + existing_cols
            selected_col_option = st.selectbox("Sélectionner une collection existante", col_choice_options)
            
            if selected_col_option == "-- Aucune / Nouvelle collection --":
                item_col = st.text_input("Ou nom de la nouvelle collection")
            else:
                item_col = selected_col_option
                
            recipient = st.text_input("Partager avec (nom d'utilisateur, séparé par des virgules) :")
            item_file = st.file_uploader("📸 Image", type=["png", "jpg", "jpeg"], key="item_up")
            
            if st.button("Sauvegarder l'item"):
                if item_file and client:
                    with st.spinner("Traitement..."):
                        img_b64 = file_to_base64(item_file)
                        type_val = "shirt" if "Chandail" in item_type else "pants"
                        col_normalized = item_col.strip().capitalize() if item_col else ""
                        new_id = int(datetime.now().timestamp())
                        
                        sheet_items = get_or_create_worksheet(client, "FitItems", ['id', 'owner', 'recipient', 'type', 'image_url', 'collection'])
                        sheet_items.append_row([str(new_id), st.session_state['username'], recipient.strip(), type_val, img_b64, col_normalized])
                        st.success("Enregistré !")
                        st.rerun()
                else:
                    st.warning("Fichier manquant ou problème de connexion.")

        # --- TAB PIÈCES ---
        with tab_items:
            st.subheader("Gérer mes pièces de linge")
            if not items_df.empty:
                my_items = items_df[items_df['owner'] == st.session_state['username']]
                for idx, row in my_items.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if row['image_url']: st.image(row['image_url'], width=150)
                        with col2:
                            st.write(f"**Type:** {'Chandail' if row['type'] == 'shirt' else 'Pantalon'}")
                            new_col = st.text_input("Collection", value=row.get('collection', ''), key=f"upd_col_{row['id']}")
                            new_recipient = st.text_input("Partagé avec", value=row.get('recipient', ''), key=f"upd_recip_{row['id']}")
                            colA, colB = st.columns(2)
                            with colA:
                                if st.button("💾 Mettre à jour", key=f"btn_upd_{row['id']}"):
                                    update_fit_item(row['id'], new_recipient.strip(), new_col.strip().capitalize())
                                    st.rerun()
                            with colB:
                                if st.button("🗑️ Supprimer", key=f"del_{row['id']}"):
                                    delete_fit_item(row['id'])
                                    st.rerun()

        # --- TAB COLLECTIONS ---
        with tab_collections:
            st.subheader("Gérer mes collections")
            if not items_df.empty:
                my_items = items_df[items_df['owner'] == st.session_state['username']]
                my_collections = my_items[my_items['collection'].str.strip() != '']['collection'].unique()
                
                for col_name in my_collections:
                    st.markdown(f"### 📁 Collection : {col_name}")
                    col_items = my_items[my_items['collection'] == col_name]
                    
                    with st.expander(f"⚙️ Actions pour la collection '{col_name}'"):
                        new_col_recip = st.text_input("Partager avec :", key=f"share_col_{col_name}")
                        if st.button("Appliquer", key=f"btn_share_{col_name}"):
                            update_collection_recipients(col_name, st.session_state['username'], new_col_recip)
                            st.rerun()
                        if st.button("🚨 Supprimer la collection complète", key=f"btn_del_col_{col_name}"):
                            delete_full_collection(col_name, st.session_state['username'])
                            st.rerun()
                    
                    for idx, row in col_items.iterrows():
                        colA, colB = st.columns([1, 4])
                        with colA:
                            if row['image_url']: st.image(row['image_url'], width=80)
                        with colB:
                            st.write(f"**{'Chandail' if row['type'] == 'shirt' else 'Pantalon'}**")
                            if st.button("Retirer", key=f"rm_col_{row['id']}"):
                                update_fit_item(row['id'], row['recipient'], "")
                                st.rerun()
                    st.divider()

        # --- TAB VISUALISER (MES FITS SEULEMENT & TAGS INTERACTIFS) ---
        with tab_view:
            st.subheader("Mes combinaisons")
            if not items_df.empty:
                my_items = items_df[items_df['owner'] == st.session_state['username']]
                unique_collections = sorted([c for c in my_items['collection'].unique() if c.strip() != ""])
                
                # État de filtre par tag cliquable
                if "selected_tag_filter" not in st.session_state:
                    st.session_state["selected_tag_filter"] = "Tous"
                
                # Tags interactifs en haut
                st.markdown("**Filtrer par collection :**")
                cols_tag = st.columns(len(unique_collections) + 1)
                with cols_tag[0]:
                    if st.button("🌟 Tous", use_container_width=True):
                        st.session_state["selected_tag_filter"] = "Tous"
                for idx, c_tag in enumerate(unique_collections):
                    with cols_tag[idx + 1]:
                        if st.button(f"🏷️ {c_tag}", use_container_width=True, key=f"tag_btn_{c_tag}"):
                            st.session_state["selected_tag_filter"] = c_tag
                
                st.write("")
                
                all_my_cols = my_items['collection'].unique()
                
                for col_name in all_my_cols:
                    display_name = col_name if str(col_name).strip() != "" else "Général (Sans collection)"
                    
                    # Si un filtre de tag est actif, on n'affiche que la collection sélectionnée
                    current_filter = st.session_state["selected_tag_filter"]
                    if current_filter != "Tous" and display_name != current_filter:
                        continue
                        
                    col_items = my_items[my_items['collection'] == col_name]
                    
                    shirts = col_items[col_items['type'] == 'shirt'].to_dict('records')
                    pants = col_items[col_items['type'] == 'pants'].to_dict('records')
                    
                    if shirts and pants:
                        st.markdown(f"### 📁 {display_name}")
                        for s in shirts:
                            for p in pants:
                                combo_id = f"S{s['id']}_P{p['id']}"
                                
                                if not ratings_df.empty:
                                    combo_ratings = ratings_df[ratings_df['combo_id'] == combo_id]
                                else:
                                    combo_ratings = pd.DataFrame()
                                    
                                if not combo_ratings.empty:
                                    avg = pd.to_numeric(combo_ratings['rating'], errors='coerce').mean()
                                    rating_txt = f"⭐ Note moyenne des partages : **{avg:.1f}/100** ({len(combo_ratings)} avis)"
                                else:
                                    rating_txt = "⭐ Note : **Aucune note reçue**"

                                with st.container(border=True):
                                    # Affichage vertical : 1 image au-dessus de l'autre
                                    if s['image_url']: 
                                        st.image(s['image_url'], width=350)
                                    if p['image_url']: 
                                        st.image(p['image_url'], width=350)
                                        
                                    st.markdown(rating_txt)
                                    
                                    if not combo_ratings.empty:
                                        for _, r in combo_ratings.iterrows():
                                            if str(r['notes']).strip():
                                                st.caption(f"💬 `{r['rater']}` : *{r['notes']}*")
                        st.write("")

        # --- TAB NOTER (ARCHIVE / PARTAGÉ AVEC MOI OU MOI-MÊME) ---
        with tab_rate:
            st.subheader("🗄️ Archive des partages (Noter)")
            st.write("Ici apparaissent les combinaisons des vêtements qui t'ont été partagés (ou partagés à toi-même).")
            
            if not items_df.empty:
                # Filtrer : Linge où je suis dans le recipient (incluant si je me le suis partagé à moi-même)
                shared_with_me = items_df[
                    items_df['recipient'].str.contains(st.session_state['username'], na=False)
                ]
                
                if shared_with_me.empty:
                    st.info("Aucun vêtement ne t'a été partagé pour le moment.")
                else:
                    unique_owners = shared_with_me['owner'].unique()
                    
                    for owner in unique_owners:
                        st.markdown(f"#### 👤 Vestiaire de `{owner}`")
                        owner_items = shared_with_me[shared_with_me['owner'] == owner]
                        
                        shirts = owner_items[owner_items['type'] == 'shirt'].to_dict('records')
                        pants = owner_items[owner_items['type'] == 'pants'].to_dict('records')
                        
                        if not shirts or not pants:
                            continue
                            
                        for s in shirts:
                            for p in pants:
                                combo_id = f"S{s['id']}_P{p['id']}"
                                
                                if not ratings_df.empty:
                                    my_rate_row = ratings_df[(ratings_df['combo_id'] == combo_id) & (ratings_df['rater'] == st.session_state['username'])]
                                else:
                                    my_rate_row = pd.DataFrame()
                                    
                                if not my_rate_row.empty:
                                    current_rate = int(pd.to_numeric(my_rate_row.iloc[0]['rating'], errors='coerce'))
                                    current_note = str(my_rate_row.iloc[0]['notes'])
                                else:
                                    current_rate, current_note = 0, ""

                                with st.expander(f"Combinaison de {owner}"):
                                    # Affichage vertical pour les notes également
                                    if s['image_url']: st.image(s['image_url'], width=300)
                                    if p['image_url']: st.image(p['image_url'], width=300)
                                        
                                    new_rating = st.number_input("Ma note /100", min_value=0, max_value=100, value=current_rate, key=f"rate_{combo_id}")
                                    new_note = st.text_input("Mon commentaire", value=current_note, key=f"note_{combo_id}")
                                    
                                    if st.button("Enregistrer ma note", key=f"save_{combo_id}"):
                                        if client:
                                            sheet_ratings = get_or_create_worksheet(client, "FitRatings", ['combo_id', 'rater', 'rating', 'notes'])
                                            rows = sheet_ratings.get_all_values()
                                            headers = rows[0]
                                            
                                            try:
                                                c_i, r_i, rat_i, n_i = headers.index('combo_id'), headers.index('rater'), headers.index('rating'), headers.index('notes')
                                            except ValueError:
                                                c_i, r_i, rat_i, n_i = 0, 1, 2, 3
                                                
                                            found_row = None
                                            for idx, r in enumerate(rows[1:], start=2):
                                                while len(r) < len(headers): r.append("")
                                                if r[c_i] == combo_id and r[r_i] == st.session_state['username']:
                                                    found_row = idx
                                                    break
                                            
                                            if found_row:
                                                sheet_ratings.update_cell(found_row, rat_i + 1, str(new_rating))
                                                sheet_ratings.update_cell(found_row, n_i + 1, str(new_note))
                                            else:
                                                new_r = [""] * len(headers)
                                                new_r[c_i], new_r[r_i], new_r[rat_i], new_r[n_i] = combo_id, st.session_state['username'], str(new_rating), str(new_note)
                                                sheet_ratings.append_row(new_r)
                                                
                                            st.success("Note et commentaire sauvegardés !")
                                            st.rerun()

    elif page.startswith("Système"):
        if st.button("← Retour"): st.session_state["current_page"] = "Accueil"; st.rerun()
        st.title(f"⚙️ {page}")
        st.info("Ce module sera configuré prochainement.")