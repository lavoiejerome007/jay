import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SIMULATION ET GESTION DE L'ÉTAT (SYSTÈME 2 + 3) ---
def init_session_state():
    # Intérêts et catégories (Système 3)
    if "categories" not in st.session_state:
        st.session_state.categories = {
            "🤖 Robotique & IA": ["Robotique humanoïde", "ROS2", "Vision par ordinateur", "Automatisation"],
            "🇨🇦 Canada": ["Politique fédérale", "Économie canadienne", "Énergie"],
            "⚜️ Québec": ["Hydro-Québec", "Économie", "Politique québécoise"],
            "💰 Économie": ["Inflation", "Taux d'intérêt", "Banque du Canada"]
        }

    # Portefeuille connecté (Simulé depuis le Système 2)
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {
            "NVDA": {"nom": "NVIDIA Corp.", "shares": 15, "avg_price": 118.50},
            "SHOP": {"nom": "Shopify Inc.", "shares": 25, "avg_price": 85.00},
            "XEQT": {"nom": "iShares Core Equity ETF", "shares": 120, "avg_price": 29.40}
        }

    # Banque d'actualités réalistes (Simule ce que le LLM/Agrégateur extrait)
    if "news_database" not in st.session_state:
        st.session_state.news_database = [
            {
                "id": "news_1",
                "category": "🤖 Robotique & IA",
                "tags": "Robotique humanoïde · Vision par ordinateur",
                "title": "Figure et OpenAI dévoilent une nouvelle architecture VLM pour la préhension fine",
                "summary": "Déploiement en usine d'un modèle de vision-langage-action capable de corriger ses trajectoires en temps réel à 50 Hz sans recompilation.",
                "relevance": 96,
                "time": "Il y a 2 h",
                "details": {
                    "event": "Présentation et tests en usine d'assemblage du modèle Figure 02 avec rétroaction haptique et visuelle combinée.",
                    "context": "Jusqu'à présent, les bras robotiques nécessitaient des trajectoires pré-calculées ou des temps de pause lors de la détection d'obstacles.",
                    "impact": "Robotique: Majeur | IA: Très important | Logistique: Disruptif",
                    "data": pd.DataFrame({"Métrique": ["Modèle", "Temps de réponse", "Taux de succès"], "Valeur": ["VLA-v3", "20 ms", "98.4%"]})
                },
                "related": [
                    {"titre": "L'architecture derrière les VLM temps réel", "source": "IEEE Spectrum", "temps": "7 min", "raison": "Explication technique du modèle d'inférence."},
                    {"titre": "Bilan du test d'intégration en usine automobile", "source": "Robotics World", "temps": "5 min", "raison": "Étude de cas sur les gains de productivité enregistrés."}
                ]
            },
            {
                "id": "news_2",
                "category": "⚜️ Québec",
                "tags": "Hydro-Québec · Énergie",
                "title": "Hydro-Québec accélère ses appels d'offres pour les réseaux intelligents d'automatisation",
                "summary": "Un plan d'investissement ciblant la modernisation des postes de distribution avec des capteurs IoT et du contrôle distribué.",
                "relevance": 91,
                "time": "Il y a 4 h",
                "details": {
                    "event": "Annonce officielle de plusieurs contrats d'infrastructure pour numériser la gestion de charge régionale.",
                    "context": "La hausse de la demande industrielle nécessite une optimisation logicielle plutôt qu'uniquement de nouvelles centrales.",
                    "impact": "Énergie: Élevé | Secteur Techno local: Positif",
                    "data": pd.DataFrame({"Poste": ["Budget", "Horizon", "Cible"], "Valeur": ["450M$", "2026-2028", "Postes HT"]})
                },
                "related": [
                    {"titre": "Comprendre le plan de modernisation du réseau québécois", "source": "La Presse Éco", "temps": "6 min", "raison": "Résumé analytique des retombées industrielles."}
                ]
            },
            {
                "id": "news_3",
                "ticker": "NVDA",
                "category": "📈 Mes investissements",
                "tags": "NVIDIA · Robotique · Semi-conducteurs",
                "title": "NVDA : Lancement officiel des puces Thor dédiées à l'autonomie robotique",
                "summary": "NVIDIA commence les livraisons aux constructeurs de robots industriels et humanoïdes avec un gain d'efficacité énergétique de 3x.",
                "relevance": 98,
                "time": "Il y a 1 h",
                "details": {
                    "event": "Disponibilité générale de la plateforme SoC Thor intégrant l'architecture Blackwell pour les systèmes embarqués.",
                    "context": "Thor remplace Orin comme standard industriel pour l'IA embarquée à forte contrainte thermique.",
                    "impact": "Action NVDA: Catalyst positif | Secteur Robotique: Standardisation",
                    "data": pd.DataFrame({"Indicateur": ["Marge estimée", "Volume T3", "Consommation"], "Valeur": ["64%", "50k unités", "100W-300W"]})
                },
                "related": [
                    {"titre": "Analyse financière : L'impact du secteur robotique sur le chiffre d'affaires de NVIDIA", "source": "Bloomberg", "temps": "9 min", "raison": "Chiffrage de la croissance du segment embarqué."}
                ]
            },
            {
                "id": "news_4",
                "ticker": "SHOP",
                "category": "📈 Mes investissements",
                "tags": "Shopify · Commerce · Automatisation",
                "title": "SHOP : Intégration d'agents d'IA autonomes pour la gestion de stocks transfrontaliers",
                "summary": "Shopify déploie un nouvel outil natif permettant aux marchands d'automatiser entièrement la commande et le réapprovisionnement.",
                "relevance": 89,
                "time": "Il y a 5 h",
                "details": {
                    "event": "Lancement de Shopify Sidekick v2 avec capacité d'action directe sur les API logistiques tierces.",
                    "context": "Consolidation de la suite logicielle pour réduire le taux d'abandon des marchands à fort volume.",
                    "impact": "Action SHOP: Neutre à positif | Logistique: Optimisation",
                    "data": pd.DataFrame({"Métrique": ["Adoption bêta", "Réduction temps gestion"], "Valeur": ["12,000 marchands", "-35%"]})
                },
                "related": [
                    {"titre": "Comment les marchands à fort volume utilisent l'IA de Shopify", "source": "TechCrunch", "temps": "6 min", "raison": "Retour d'expérience des premiers utilisateurs."}
                ]
            }
        ]

# --- 2. MODALES DYNAMIQUES (DIALOGS) ---
@st.dialog("📖 Fiche d'Analyse Détaillée", width="large")
def show_details_modal(news):
    st.subheader(news["title"])
    st.caption(f"{news['category']} • {news['tags']}")
    
    st.markdown("### 🧠 Ce qui s'est réellement passé")
    st.write(news["details"]["event"])
    
    st.markdown("### 📅 Contexte")
    st.write(news["details"]["context"])
    
    st.markdown("### 📊 Données importantes")
    st.dataframe(news["details"]["data"], hide_index=True, use_container_width=True)
    
    st.markdown("### 🌎 Impact")
    st.write(news["details"]["impact"])

@st.dialog("📰 Articles Reliés pour Approfondir", width="large")
def show_related_modal(news):
    st.subheader(f"Dossier de lecture : {news['title']}")
    
    for i, art in enumerate(news.get("related", []), 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {art['titre']}")
            st.caption(f"📍 {art['source']} — ⏱️ {art['temps']}")
            st.write(f"**Pourquoi lire ceci :** {art['raison']}")
            st.button("Consulter la source ↗", key=f"src_{news['id']}_{i}")

# --- 3. INTERFACE PRINCIPALE ---
def show_system3():
    init_session_state()
    
    st.title("📰 Mon Briefing Personalisé")
    tab_accueil, tab_perso = st.tabs(["🏠 Accueil", "⚙️ Personnaliser"])
    
    # --- PAGE 1: ACCUEIL ---
    with tab_accueil:
        # 1. À RETENIR
        top_news = st.session_state.news_database[0]
        st.header("🔥 À retenir aujourd'hui")
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(top_news["title"])
                st.caption(f"{top_news['category']} · {top_news['tags']}")
                st.write(top_news["summary"])
                st.caption(f"🕐 {top_news['time']}")
            with col2:
                st.markdown(f"<h3 style='text-align: right; color: #00CC96;'>🟢 {top_news['relevance']}%</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: right;'>Pertinence</p>", unsafe_allow_html=True)
            
            c1, c2, _ = st.columns([1, 1, 3])
            if c1.button("📖 Plus de détails", key="top_det"):
                show_details_modal(top_news)
            if c2.button("📰 Articles reliés", key="top_rel"):
                show_related_modal(top_news)

        st.divider()

        # 2. SECTION INVESTISSEMENTS (SYSTÈME 2 LINK)
        st.header("📈 MES INVESTISSEMENTS")
        st.caption("Nouvelles filtrées selon les titres actuellement détenus dans votre portefeuille.")
        
        portfolio_tickers = list(st.session_state.portfolio.keys())
        stock_news = [n for n in st.session_state.news_database if n.get("ticker") in portfolio_tickers]
        
        if stock_news:
            for item in stock_news:
                with st.container(border=True):
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"**[{item['ticker']}]** — {item['title']}")
                        st.write(item["summary"])
                        st.caption(f"⏱️ {item['time']} · {item['tags']}")
                    with cols[1]:
                        st.markdown(f"<h4 style='text-align: right; color: #00CC96;'>🟢 {item['relevance']}%</h4>", unsafe_allow_html=True)
                    
                    b1, b2, _ = st.columns([1, 1, 3])
                    if b1.button("📖 Plus de détails", key=f"det_{item['id']}"):
                        show_details_modal(item)
                    if b2.button("📰 Articles reliés", key=f"rel_{item['id']}"):
                        show_related_modal(item)
        else:
            st.info("Aucune nouvelle majeure aujourd'hui sur les titres de votre portefeuille.")

        st.divider()

        # 3. SECTIONS PAR CATÉGORIES
        for category, interests in st.session_state.categories.items():
            st.header(category.upper())
            st.caption(" • ".join(interests))
            
            cat_items = [n for n in st.session_state.news_database if n["category"] == category]
            
            if cat_items:
                for item in cat_items:
                    with st.container(border=True):
                        st.subheader(item["title"])
                        st.write(item["summary"])
                        st.caption(f"🟢 Pertinence : {item['relevance']}% | 🕐 {item['time']}")
                        
                        b1, b2, _ = st.columns([1, 1, 3])
                        if b1.button("📖 Plus de détails", key=f"det_{item['id']}"):
                            show_details_modal(item)
                        if b2.button("📰 Articles reliés", key=f"rel_{item['id']}"):
                            show_related_modal(item)
            else:
                st.caption("Aucune nouvelle urgente dans cette catégorie pour le moment.")
            st.write("---")

    # --- PAGE 2: PERSONNALISATION ---
    with tab_perso:
        st.header("🎯 Configuration des Filtres")
        st.write("Ajustez vos catégories et mots-clés de veille.")
        
        for cat, tags in st.session_state.categories.items():
            with st.expander(cat, expanded=True):
                st.multiselect("Intérêts actifs :", options=tags, default=tags, key=f"m_{cat}")

if __name__ == "__main__":
    st.set_page_config(page_title="Mon Briefing", layout="wide")
    show_system3()