import streamlit as st
import hashlib
import json
import os
import pandas as pd
from datetime import datetime

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
    # Sidebar personnalisée basée sur ton croquis
    with st.sidebar:
        # 1. Boîte de profil en haut
        with st.container(border=True):
            st.markdown(f"**Bienvenue**<br>`{st.session_state['username']}`", unsafe_allow_html=True)
            if st.button("👤 Mon Profil", use_container_width=True):
                st.session_state["current_page"] = "Profil"
                st.rerun()

        st.divider()

        # 2. Utilitaires ajoutés entre le profil et la déconnexion
        st.subheader("🛠️ Utilitaires")
        if st.button("🏠 Tableau de bord", use_container_width=True):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        with st.expander("📊 Statistiques rapides"):
            st.metric("Systèmes actifs", "9 / 9")
            st.metric("Statut Cloud", "Connecté" if get_gsheet_client() else "Local")

        st.divider()

        # 3. Bouton déconnecté tout en bas
        if st.button("🚪 Se déconnecter", type="secondary", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["current_page"] = "Accueil"
            st.rerun()

    # Gestion de l'affichage de la page centrale
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

        # Grille 3x3
        for i in range(0, 9, 3):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.container(border=True):
                    st.subheader(systems[i])
                    st.write("Accéder au module.")
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

    # --- PAGES DES SOUS-SYSTÈMES (1 à 9) ---
    elif page.startswith("Système"):
        if st.button("← Retour au tableau de bord"):
            st.session_state["current_page"] = "Accueil"
            st.rerun()
            
        st.title(f"⚙️ {page}")
        st.markdown(f"Espace de travail et de sauvegarde pour le **{page}**.")
        
        # Enregistrement isolé de données liées à l'utilisateur pour ce système
        st.subheader("Enregistrer une donnée")
        user_input_data = st.text_input(f"Entrez l'information pour {page} :")
        if st.button("Sauvegarder dans Google Sheets"):
            client = get_gsheet_client()
            if client:
                try:
                    sheet = client.open("Streamlit_DB").worksheet("data")
                    sheet.append_row([st.session_state['username'], page, user_input_data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    st.success("Donnée enregistrée avec succès !")
                except Exception as e:
                    st.error(f"Erreur d'écriture : {e}")
            else:
                st.warning("Google Sheets non connecté.")