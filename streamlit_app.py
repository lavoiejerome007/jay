import streamlit as st
from database import load_users, save_user, hash_password
from system1 import show_system1
from system2 import show_system2
# Plus tard, tu ajouteras : from system2 import show_system2

st.set_page_config(page_title="Mon Application Web", page_icon="🚀", layout="wide")

# Initialisation de session
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "current_page" not in st.session_state: st.session_state["current_page"] = "Accueil"

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
    # Sidebar
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

    # Navigation logic
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
        show_system1()  # On appelle la fonction du fichier system1.py

    elif page == "Système 2":      # <--- AJOUTE CES DEUX LIGNES
        show_system2()

    elif page.startswith("Système"):
        if st.button("← Retour"): st.session_state["current_page"] = "Accueil"; st.rerun()
        st.title(f"⚙️ {page}")
        st.info("Ce module sera configuré prochainement.")