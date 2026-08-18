import streamlit as st
import hashlib
import json
import os
import pandas as pd
from datetime import datetime

# Essai d'importation de gspread pour Google Sheets
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

def clean_private_key(key_str):
    """Reconstruit une clé PEM parfaite peu importe le formatage TOML."""
    if not isinstance(key_str, str):
        return key_str
    
    # Remplacer les \n littéraux
    key_str = key_str.replace("\\n", "\n")
    
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    if header in key_str and footer in key_str:
        # Extraire uniquement le corps Base64
        parts = key_str.split(header)
        body_and_footer = parts[1].split(footer)
        raw_body = body_and_footer[0]
        
        # Supprimer tous les espaces, retours à la ligne et caractères parasites
        clean_body = "".join(raw_body.split())
        
        # Reconstruire une clé PEM standard
        return f"{header}\n{clean_body}\n{footer}\n"
    
    return key_str

def get_gsheet_client():
    """Connexion à Google Sheets via les secrets Streamlit."""
    if not GSPREAD_AVAILABLE:
        return None
    try:
        if "gcp_service_account" in st.secrets:
            # Copie du dictionnaire des secrets
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            # Nettoyage automatique et réparation de la clé
            if "private_key" in creds_dict:
                creds_dict["private_key"] = clean_private_key(creds_dict["private_key"])

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(credentials)
            return client
    except Exception as e:
        st.error(f"Erreur de connexion à Google Sheets : {e}")
    return None

def hash_password(password):
    """Hache le mot de passe pour la sécurité."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Charge la liste des utilisateurs depuis Google Sheets ou localement en secours."""
    client = get_gsheet_client()
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("users")
            records = sheet.get_all_records()
            users_dict = {}
            for r in records:
                users_dict[str(r["username"])] = str(r["password_hash"])
            return users_dict
        except Exception as e:
            st.warning("Impossible de lire Google Sheets. Utilisation du stockage local temporaire.")
    
    # Mode secours local (fichiers JSON)
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {"admin": hash_password("1234")}

def save_user(username, password_hash):
    """Sauvegarde un nouvel utilisateur dans Google Sheets et/ou localement."""
    client = get_gsheet_client()
    saved_to_gsheet = False
    
    if client:
        try:
            sheet = client.open("Streamlit_DB").worksheet("users")
            sheet.append_row([username, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            saved_to_gsheet = True
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde sur Google Sheets : {e}")

    # Sauvegarde locale en parallèle
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    users[username] = password_hash
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)
        
    return saved_to_gsheet

# ==========================================
# GESTION DE LA SESSION & AUTHENTIFICATION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ==========================================
# PAGE DE CONNEXION / INSCRIPTION
# ==========================================

if not st.session_state["logged_in"]:
    st.title("🔐 Bienvenue sur votre Application")
    st.markdown("Connectez-vous ou créez un compte pour accéder aux différents systèmes.")
    
    tab_login, tab_register = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])
    
    with tab_login:
        user_input = st.text_input("Nom d'utilisateur", key="login_user")
        pass_input = st.text_input("Mot de passe", type="password", key="login_pass")
        
        if st.button("Connexion", type="primary"):
            users = load_users()
            if user_input in users and users[user_input] == hash_password(pass_input):
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_input
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
                    st.success("Compte créé et enregistré sur Google Sheets ! Vous pouvez vous connecter.")
                else:
                    st.success("Compte créé localement. Configurer Google Sheets pour la sauvegarde permanente.")

# ==========================================
# TABLEAU DE BORD & SYSTÈMES (CONNECTÉ)
# ==========================================

else:
    # Barre latérale (Sidebar)
    with st.sidebar:
        st.write(f"👤 Connecté en tant que : **{st.session_state['username']}**")
        if st.button("Se déconnecter", type="secondary"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()
            
        st.divider()
        st.subheader("📌 Menu des Systèmes")
        system_choice = st.radio(
            "Choisissez un système :",
            ["Accueil / Aperçu", "Système 1", "Système 2", "Système 3"]
        )

    # Contenu principal selon le système choisi
    if system_choice == "Accueil / Aperçu":
        st.title("🏠 Tableau de Bord Principal")
        st.markdown(f"Content de te revoir, **{st.session_state['username']}** !")
        
        # Statut Google Sheets
        client = get_gsheet_client()
        if client:
            st.success("✅ Connecté à Google Sheets avec succès ! Tes données sont enregistrées en permanence.")
        else:
            st.info("ℹ️ Mode stockage local actif. Suis le guide ci-dessous pour connecter ton Google Sheet.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Système 1", "Prêt", "Actif")
        with col2:
            st.metric("Système 2", "En attente", "Inactif")
        with col3:
            st.metric("Système 3", "En attente", "Inactif")

    elif system_choice == "Système 1":
        st.title("⚙️ Système 1")
        st.write("Espace de travail pour le premier module.")
        
        st.subheader("Enregistrer une information")
        info_perso = st.text_input("Entrez une donnée à sauvegarder :")
        if st.button("Sauvegarder l'information"):
            client = get_gsheet_client()
            if client:
                try:
                    sheet = client.open("Streamlit_DB").worksheet("data")
                    sheet.append_row([st.session_state['username'], info_perso, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    st.success("Donnée sauvegardée dans Google Sheets !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.warning("Google Sheets n'est pas encore configuré.")

    elif system_choice == "Système 2":
        st.title("📊 Système 2")
        st.write("Espace pour le deuxième système.")

    elif system_choice == "Système 3":
        st.title("🛠️ Système 3")
        st.write("Espace pour le troisième système.")