import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. GESTION DE L'ÉTAT ET DES PRÉFÉRENCES ---
def init_session_state():
    if "categories" not in st.session_state:
        st.session_state.categories = {
            "🌎 Monde": ["Géopolitique", "Guerres", "Politique internationale", "Chine"],
            "🇨🇦 Canada": ["Politique fédérale", "Économie canadienne", "Énergie"],
            "⚜️ Québec": ["Politique québécoise", "Hydro-Québec", "Économie"],
            "🤖 Robotique": ["Robotique humanoïde", "ROS2", "Vision par ordinateur", "Automatisation industrielle", "Robots industriels"],
            "💰 Économie": ["Inflation", "Taux d'intérêt", "Banque du Canada", "Dollar canadien"]
        }

# --- 2. FENÊTRES CONTEXTUELLES (MODALS) ---
@st.dialog("📖 Fiche d'Analyse Détaillée", width="large")
def show_details(title, category, tags):
    st.subheader(title)
    st.caption(f"{category} • {tags}")
    
    st.markdown("### 🧠 Ce qui s'est réellement passé")
    st.write("Explication détaillée générée par l'IA sur l'événement, les acteurs impliqués et la chronologie des faits.")
    
    st.markdown("### 📅 Contexte")
    st.write("Historique de la situation et développements préalables ayant mené à cette annonce.")
    
    st.markdown("### 🔍 Pourquoi c'est important")
    st.write("Analyse des conséquences technologiques, économiques ou politiques à court et moyen terme.")
    
    st.markdown("### 📊 Données importantes")
    df = pd.DataFrame({
        "Élément": ["Entreprise", "Date", "Technologie", "Performance"],
        "Information": ["Figure AI / OpenAI", datetime.today().strftime("%d %B %Y"), "Réseau de neurones end-to-end", "+40% de vitesse d'inférence"]
    })
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("### 🌎 Impact")
    st.markdown("- **Robotique :** Important\n- **IA :** Très important\n- **Industrie :** Potentiellement disruptif")
    
    st.markdown("### 🔮 Et ensuite ?")
    st.write("Projections des experts sur les prochaines étapes de développement ou de régulation.")

@st.dialog("📰 Articles Reliés pour Approfondir", width="large")
def show_related_articles(title):
    st.subheader(f"Dossier de lecture : {title}")
    
    articles = [
        {"titre": "Comprendre la nouvelle architecture end-to-end", "source": "IEEE Spectrum", "temps": "8 min", "raison": "Idéal pour comprendre la technologie sous-jacente sans entrer dans le code pur."},
        {"titre": "L'impact de l'automatisation sur la chaîne logistique en 2026", "source": "Wall Street Journal", "temps": "12 min", "raison": "Donne une perspective macro-économique et industrielle de l'annonce."},
        {"titre": "Interview du lead de projet", "source": "TechCrunch", "temps": "5 min", "raison": "Permet de comprendre la vision à long terme de l'entreprise."}
    ]
    
    for i, art in enumerate(articles, 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {art['titre']}")
            st.caption(f"📍 {art['source']} — ⏱️ {art['temps']} de lecture")
            st.write(f"**Pourquoi lire ceci :** {art['raison']}")
            st.button("Lire l'article original ↗", key=f"read_{i}")

# --- 3. INTERFACE PRINCIPALE ---
def show_system3():
    init_session_state()
    
    st.title("📰 Mon Briefing Intelligent")
    tab_accueil, tab_perso = st.tabs(["🏠 Accueil", "⚙️ Personnaliser"])
    
    # --- PAGE 1: ACCUEIL ---
    with tab_accueil:
        st.header("🔥 À retenir aujourd'hui")
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("🤖 Un nouveau robot humanoïde atteint un niveau d'autonomie inédit en usine")
                st.caption("Robotique · IA · ROS2")
                st.write("Une percée majeure dans la manipulation d'objets non standardisés sur les lignes d'assemblage grâce à un nouveau modèle de vision par ordinateur.")
                st.caption("🕐 Il y a 3 h")
            with col2:
                st.markdown("<h3 style='text-align: right; color: #00CC96;'>🟢 96%</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: right;'>Pertinence</p>", unsafe_allow_html=True)
            
            c1, c2, _ = st.columns([1, 1, 3])
            if c1.button("📖 Plus de détails", key="det_main"):
                show_details("Un nouveau robot humanoïde atteint un niveau d'autonomie inédit", "Robotique", "IA, ROS2")
            if c2.button("📰 Articles reliés", key="art_main"):
                show_related_articles("Nouveau robot humanoïde autonome")

        st.divider()
        
        # Affichage dynamique basé sur les catégories de l'utilisateur
        for category, interests in st.session_state.categories.items():
            st.header(category.upper())
            st.caption(" | ".join(interests))
            
            # Simulation d'une nouvelle par catégorie
            with st.container(border=True):
                st.markdown(f"**Évolution majeure concernant : {interests[0] if interests else 'Général'}**")
                st.write(f"Un événement significatif vient de se produire dans le secteur {category.split()[1] if len(category.split()) > 1 else category}, impactant directement vos intérêts de suivi.")
                st.caption("🟢 Pertinence : 88%")
                
                b1, b2, _ = st.columns([1, 1, 3])
                if b1.button("📖 Plus de détails", key=f"det_{category}"):
                    show_details(f"Nouvelle de la catégorie {category}", category, interests[0])
                if b2.button("📰 Articles reliés", key=f"art_{category}"):
                    show_related_articles(f"Dossier {category}")
            st.write("---")

    # --- PAGE 2: PERSONNALISATION ---
    with tab_perso:
        st.header("🎯 Catégories & Intérêts")
        st.write("Ajustez votre radar d'information. L'IA utilisera ces mots-clés pour filtrer et prioriser votre briefing quotidien.")
        
        # Ajouter une nouvelle catégorie
        new_cat = st.text_input("Ajouter une catégorie (ex: 🧬 Santé)")
        if st.button("➕ Ajouter la catégorie"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories[new_cat] = []
                st.rerun()

        st.divider()
        
        # Gérer les catégories existantes
        for cat in list(st.session_state.categories.keys()):
            with st.expander(cat, expanded=True):
                col_tags, col_delete = st.columns([4, 1])
                
                with col_tags:
                    # Utilisation de multiselect pour agir comme des "tags" gérables
                    current_interests = st.session_state.categories[cat]
                    updated_interests = st.multiselect(
                        f"Intérêts pour {cat}", 
                        options=current_interests + ["Ajouter un intérêt..."], 
                        default=current_interests,
                        key=f"tags_{cat}"
                    )
                    
                    new_interest = st.text_input(f"Nouvel intérêt", key=f"new_{cat}", label_visibility="collapsed", placeholder="Taper et appuyer sur Entrée pour ajouter...")
                    if new_interest:
                        if new_interest not in st.session_state.categories[cat]:
                            st.session_state.categories[cat].append(new_interest)
                            st.rerun()
                            
                    # Mise à jour si des tags sont retirés via le multiselect
                    real_updates = [t for t in updated_interests if t != "Ajouter un intérêt..."]
                    if real_updates != current_interests:
                        st.session_state.categories[cat] = real_updates
                        st.rerun()

                with col_delete:
                    if st.button("🗑️ Supprimer", key=f"del_cat_{cat}"):
                        del st.session_state.categories[cat]
                        st.rerun()

# Pour lancer ce système de manière autonome :
if __name__ == "__main__":
    st.set_page_config(page_title="Mon Briefing", layout="wide")
    show_system3()