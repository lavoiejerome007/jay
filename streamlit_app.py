import streamlit as st
import json
import os
import hashlib

# ==========================================
# 1. GESTION DU FICHIER DES UTILISATEURS
# ==========================================
USER_DB_FILE = "users.json"

def hash_password(password):
    """Transforme le mot de passe en chaîne sécurisée."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {"admin": hash_password("1234")}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ==========================================
# 2. INITIALISATION DE LA SESSION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

users_db = load_users()

# ==========================================
# 3. INTERFACE DE CONNEXION / INSCRIPTION
# ==========================================
def show_login_page():
    st.title("🔒 Bienvenue - Accès Sécurisé")
    
    tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte"])
    
    with tab_login:
        st.subheader("Connexion")
        username_input = st.text_input("Nom d'utilisateur", key="login_user")
        password_input = st.text_input("Mot de passe", type="password", key="login_pass")
        
        if st.button("Connexion", type="primary"):
            hashed_input = hash_password(password_input)
            if username_input in users_db and users_db[username_input] == hashed_input:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_input
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
                
    with tab_signup:
        st.subheader("Créer un nouveau compte")
        new_user = st.text_input("Choisissez un nom d'utilisateur", key="signup_user")
        new_pass = st.text_input("Choisissez un mot de passe", type="password", key="signup_pass")
        confirm_pass = st.text_input("Confirmez le mot de passe", type="password", key="signup_confirm")
        
        if st.button("S'inscrire"):
            if not new_user or not new_pass:
                st.warning("Veuillez remplir tous les champs.")
            elif new_user in users_db:
                st.error("Ce nom d'utilisateur existe déjà !")
            elif new_pass != confirm_pass:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                users_db[new_user] = hash_password(new_pass)
                save_users(users_db)
                st.success("Compte créé avec succès ! Vous pouvez vous connecter.")

# ==========================================
# 4. STRUCTURE DE LA PAGE PRINCIPALE (DASHBOARD)
# ==========================================
def show_main_page():
    # --- BARRE LATÉRALE (MENU) ---
    with st.sidebar:
        st.write(f"👤 Connecté : **{st.session_state['username']}**")
        st.markdown("---")
        
        # Menu de navigation entre les différents systèmes
        st.subheader("Navigation")
        choix_menu = st.radio(
            "Aller vers :",
            ["🏠 Accueil", "⚙️ Système 1", "📊 Système 2", "📝 Données Personnelles"]
        )
        
        st.markdown("---")
        if st.button("Se déconnecter"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

    # --- AFFICHAGE SELON LE CHOIX DU MENU ---
    if choix_menu == "🏠 Accueil":
        st.title(f"👋 Bonjour {st.session_state['username']} !")
        st.write("Bienvenue sur la plateforme. Utilise le menu à gauche pour naviguer entre les différents systèmes.")
        st.info("👉 Prochaine étape : Choisis un système et dis-moi ce qu'il doit faire !")

    elif choix_menu == "⚙️ Système 1":
        st.title("⚙️ Système 1 : Espace de travail")
        st.write("C'est ici que nous allons coder ta première fonctionnalité.")
        # On ajoutera le code de ton Système 1 ici

    elif choix_menu == "📊 Système 2":
        st.title("📊 Système 2 : Outils")
        st.write("Cet espace est réservé pour une autre fonctionnalité indépendante.")
        # On ajoutera le code de ton Système 2 ici

    elif choix_menu == "📝 Données Personnelles":
        st.title("📝 Tes données")
        st.write(f"Voici l'espace privé de **{st.session_state['username']}**.")
        st.write("Plus tard, on pourra connecter cet espace à Google Sheets pour que chacun puisse sauvegarder ses propres textes, scores, ou informations.")

# ==========================================
# 5. LOGIQUE D'AFFICHAGE DU SITE
# ==========================================
if not st.session_state["logged_in"]:
    show_login_page()
else:
    show_main_page()