import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. GESTION DE L'ÉTAT ET DES DONNÉES ---
def init_session_state():
    # Catégories et intérêts selon ta structure initiale
    if "categories" not in st.session_state:
        st.session_state.categories = {
            "🌎 Monde": ["Géopolitique", "Guerres", "Politique internationale", "Chine"],
            "🇨🇦 Canada": ["Politique fédérale", "Économie canadienne", "Énergie"],
            "⚜️ Québec": ["Politique québécoise", "Hydro-Québec", "Économie"],
            "🤖 Robotique": ["Robotique humanoïde", "ROS2", "Vision par ordinateur", "Automatisation industrielle", "Robots industriels"],
            "💰 Économie": ["Inflation", "Taux d'intérêt", "Banque du Canada", "Dollar canadien"]
        }

    # Portefeuille connecté (simulé depuis le système de gestion d'actifs)
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {
            "XEQT": {"nom": "iShares Core Equity ETF", "shares": 120},
            "SHOP": {"nom": "Shopify Inc.", "shares": 25},
            "NVDA": {"nom": "NVIDIA Corp.", "shares": 15}
        }

    # Base de données complète avec des résumés de 4-5 lignes et des fiches détaillées exhaustives
    if "news_database" not in st.session_state:
        st.session_state.news_database = {
            "top": [
                {
                    "id": "top_1",
                    "category": "Robotique · IA",
                    "title": "Un nouveau robot humanoïde atteint un nouveau niveau d'autonomie en environnement complexe",
                    "summary": "Une percée majeure vient d'être franchie dans l'intégration de modèles de fondation multimodaux directement dans l'embarqué d'un robot humanoïde. Cette avancée permet une adaptation dynamique en temps réel face à des objets non structurés sur les lignes d'assemblage industrielles. L'impact se traduit par une réduction drastique des temps de programmation manuelle pour les ingénieurs en automatisation.",
                    "time": "Il y a 3 h",
                    "details": {
                        "event": "Figure AI a présenté sa nouvelle architecture logicielle end-to-end couplée à une mise à jour matérielle majeure de ses actionneurs.",
                        "context": "Jusqu'à présent, les robots industriels nécessitaient des programmes séquentiels rigides pour chaque nouvelle tâche, limitant leur déploiement à des environnements ultra-balisés.",
                        "importance": "Cela démocratise l'utilisation de la robotique humanoïde flexible, permettant aux usines d'absorber des variations de production sans réingénierie complète des cellules de travail.",
                        "table": pd.DataFrame({
                            "Élément": ["Entreprise", "Date", "Technologie", "Coût estimé", "Performance"],
                            "Information": ["Figure AI", "30 août 2026", "Réseau de neurones VLA unifié", "Variables selon flotte", "+40% de cadence utile"]
                        }),
                        "impact": "Robotique : important\nIA : très important\nIndustrie : potentiellement disruptif",
                        "futur": "Les analystes anticipent une phase de tests pilotes à grande échelle chez les constructeurs automobiles dès le prochain trimestre, ouvrant la voie à une commercialisation de masse.",
                        "sources": ["IEEE Spectrum (8 min)", "TechCrunch (5 min)", "Communiqué officiel de l'entreprise"]
                    },
                    "related": [
                        {"titre": "Comprendre le nouveau robot humanoïde et son architecture", "source": "IEEE Spectrum", "temps": "8 min", "raison": "Idéal pour saisir les choix technologiques sous-jacents sans jargon inutile."},
                        {"titre": "Comment fonctionnent les robots humanoïdes modernes en usine ?", "source": "MIT Technology Review", "temps": "12 min", "raison": "Excellente mise en perspective de l'état actuel de l'industrie robotique."},
                        {"titre": "L'entreprise annonce sa nouvelle génération de robots autonomes", "source": "Robotics Business", "temps": "5 min", "raison": "Permet de décortiquer l'annonce originale et les spécifications techniques de base."},
                        {"titre": "L'état actuel de la robotique humanoïde en 2026", "source": "Wall Street Journal", "temps": "15 min", "raison": "Donne une perspective macro-économique globale sur les investissements du secteur."}
                    ]
                }
            ],
            "🌎 Monde": [
                {
                    "id": "monde_1",
                    "category": "🌎 Monde",
                    "title": "Accord commercial international majeur signé pour sécuriser les chaînes d'approvisionnement en terres rares",
                    "summary": "Plusieurs nations industrialisées ont ratifié un traité visant à mutualiser leurs stocks stratégiques et à subventionner le raffinage local. Cette décision vise à réduire la dépendance technologique vis-à-vis des monopoles asiatiques actuels. Les répercussions se feront sentir à court terme sur les coûts de fabrication des composants électroniques et des moteurs électriques.",
                    "time": "Il y a 5 h",
                    "details": {
                        "event": "Signature d'un consortium multilatéral encadrant l'extraction, le transport et le raffinage des minéraux critiques pour la transition énergétique.",
                        "context": "Les tensions géopolitiques répétées et les restrictions unilatérales sur l'exportation avaient provoqué des goulots d'étranglement sévères l'année précédente.",
                        "importance": "Sécurise l'approvisionnement à long terme pour l'ensemble des industries manufacturières, de l'automobile à la haute technologie.",
                        "table": pd.DataFrame({
                            "Élément": ["Secteur touché", "Date", "Pays signataires", "Impact budgétaire"],
                            "Information": ["Haute technologie et Énergie", "30 août 2026", "14 nations", "12 milliards de subventions croisées"]
                        }),
                        "impact": "Géopolitique : majeur\nÉconomie internationale : très important\nIndustrie : stabilisateur critique",
                        "futur": "Mise en place d'organismes de régulation conjoints pour valider les nouveaux sites de raffinage dès l'an prochain.",
                        "sources": ["Reuters (6 min)", "Financial Times (10 min)"]
                    },
                    "related": [
                        {"titre": "La géopolitique des minéraux critiques en 2026", "source": "Foreign Affairs", "temps": "10 min", "raison": "Analyse géostratégique complète des tensions d'approvisionnement."},
                        {"titre": "Impacts de l'accord sur l'industrie manufacturière occidentale", "source": "Bloomberg", "temps": "7 min", "raison": "Décryptage des coûts pour les chaînes de montage."}
                    ]
                }
            ],
            "🇨🇦 Canada": [
                {
                    "id": "can_1",
                    "category": "🇨🇦 Canada",
                    "title": "Ottawa dévoile son nouveau cadre réglementaire pour accélérer les grands projets énergétiques",
                    "summary": "Le gouvernement fédéral a annoncé une refonte majeure des processus d'évaluation d'impact afin de réduire les délais administratifs pour les infrastructures propres. Le plan cible en priorité les corridors de transport d'électricité interprovinciaux et les sites de production d'hydrogène vert. Les milieux économiques saluent un virage pragmatique face aux retards structurels passés.",
                    "time": "Il y a 4 h",
                    "details": {
                        "event": "Publication du décret fédéral instaurant des guichets uniques d'approbation pour les projets d'intérêt national prioritaire.",
                        "context": "Les délais d'approbation réglementaire au Canada étaient devenus l'un des principaux freins aux investissements privés en infrastructures lourdes.",
                        "importance": "Accélère la transition énergétique et stimule l'investissement industriel domestique grâce à une prévisibilité accrue.",
                        "table": pd.DataFrame({
                            "Élément": ["Juridiction", "Date", "Cible principale", "Réduction de délai visée"],
                            "Information": ["Fédéral (Canada)", "30 août 2026", "Corridors énergétiques", "Jusqu'à 50% de réduction"]
                        }),
                        "impact": "Politique fédérale : important\nÉnergie : majeur\nÉconomie canadienne : positif",
                        "futur": "Négociations serrées attendues avec les provinces pour harmoniser les normes environnementales locales.",
                        "sources": ["The Globe and Mail (7 min)", "Radio-Canada Économie (5 min)"]
                    },
                    "related": [
                        {"titre": "Les défis de l'infrastructure énergétique canadienne", "source": "The Globe and Mail", "temps": "9 min", "raison": "Comprendre les goulets d'étranglement historiques du réseau."},
                        {"titre": "Analyse du nouveau guichet unique fédéral", "source": "Financial Post", "temps": "6 min", "raison": "Vue d'ensemble des réactions du milieu des affaires."}
                    ]
                }
            ],
            "⚜️ Québec": [
                {
                    "id": "que_1",
                    "category": "⚜️ Québec",
                    "title": "Hydro-Québec lance un vaste chantier technologique pour optimiser ses postes de transformation",
                    "summary": "La société d'État amorce le déploiement massif de capteurs intelligents et de systèmes de contrôle décentralisés sur l'ensemble de son réseau de transport. Ce projet vise à maximiser la capacité de transit sans nécessiter la construction immédiate de nouvelles lignes à haute tension. Cette modernisation s'inscrit directement dans la stratégie de gestion rigoureuse de la puissance de pointe.",
                    "time": "Il y a 2 h",
                    "details": {
                        "event": "Attribution de contrats majeurs d'intégration de systèmes IIoT pour automatiser la surveillance thermique et électrique des sous-stations.",
                        "context": "La croissance de la demande industrielle et résidentielle exerce une pression constante sur les marges de réserve du réseau québécois.",
                        "importance": "Permet d'absorber une plus grande charge industrielle sans compromettre la stabilité globale du réseau électrique provincial.",
                        "table": pd.DataFrame({
                            "Élément": ["Maître d'œuvre", "Date", "Budget alloué", "Technologie"],
                            "Information": ["Hydro-Québec", "30 août 2026", "450 millions de dollars", "Réseaux maillés intelligents et IoT"]
                        }),
                        "impact": "Hydro-Québec : majeur\nÉconomie québécoise : très important\nAutomatisation : hautement pertinent",
                        "futur": "Intégration graduelle de modèles prédictifs basés sur l'intelligence artificielle pour anticiper les pannes d'équipement.",
                        "sources": ["La Presse (6 min)", "Le Devoir (5 min)"]
                    },
                    "related": [
                        {"titre": "Comment les réseaux intelligents transforment la distribution d'électricité", "source": "La Presse", "temps": "6 min", "raison": "Explication claire des enjeux de modernisation du réseau québécois."},
                        {"titre": "Le plan d'action d'Hydro-Québec face aux nouveaux défis industriels", "source": "Les Affaires", "temps": "8 min", "raison": "Analyse des besoins énergétiques futurs de la province."}
                    ]
                }
            ],
            "🤖 Robotique": [
                {
                    "id": "rob_1",
                    "category": "🤖 Robotique",
                    "title": "Standardisation accrue des piles logicielles ROS2 dans les flottes de robots mobiles autonomes",
                    "summary": "Un consortium international d'intégrateurs industriels a publié un nouveau profil de référence pour l'interopérabilité des robots mobiles en milieu manufacturier. L'adoption généralisée de ROS2 et des ponts de communication temps réel simplifie considérablement le déploiement de flottes hétérogènes. Cette normalisation réduit les coûts d'intégration et accélère le retour sur investissement pour les usines intelligentes.",
                    "time": "Il y a 6 h",
                    "details": {
                        "event": "Officialisation des spécifications techniques unifiées pour la gestion de flotte multi-marques sous environnement ROS2.",
                        "context": "Les usines devaient jusqu'à présent maintenir des couches logicielles propriétaires complexes pour faire communiquer des robots de fabricants différents.",
                        "importance": "Ouvre la voie à une modularité complète des lignes de production automatisées et facilite la maintenance prédictive.",
                        "table": pd.DataFrame({
                            "Élément": ["Cadre technique", "Date", "Secteur", "Gain d'intégration"],
                            "Information": ["ROS2 / Middleware industriel", "30 août 2026", "Logistique et assemblage", "-40% de temps de mise en service"]
                        }),
                        "impact": "Robotique mobile : majeur\nROS2 : critique\nAutomatisation industrielle : structurant",
                        "futur": "Adoption progressive par les grands équipementiers automobiles et pharmaceutiques mondiaux au cours des prochains semestres.",
                        "sources": ["Robotics Tomorrow (5 min)", "Automation World (7 min)"]
                    },
                    "related": [
                        {"titre": "Guide pratique de migration vers les architectures ROS2 industrielles", "source": "IEEE Robotics", "temps": "14 min", "raison": "Référence technique incontournable pour les ingénieurs en robotique."},
                        {"titre": "L'interopérabilité des flottes de robots en milieu fermé", "source": "Control Engineering", "temps": "8 min", "raison": "Analyse des gains opérationnels constatés sur le terrain."}
                    ]
                }
            ],
            "💰 Économie": [
                {
                    "id": "eco_1",
                    "category": "💰 Économie",
                    "title": "La Banque du Canada signale une stabilisation durable de l'inflation dans la cible de 2 pour cent",
                    "summary": "Dans sa dernière allocution, la gouvernance de la banque centrale a confirmé que les pressions sur les prix se sont normalisées à travers la plupart des secteurs de l'économie. Cette situation offre une marge de manœuvre accrue pour ajuster la politique monétaire sans secouer les marchés de l'emploi. Les analystes prévoient une consolidation de la confiance des investisseurs et des consommateurs pour la rentrée.",
                    "time": "Il y a 1 h",
                    "details": {
                        "event": "Rapport trimestriel de politique monétaire confirmant l'ancrage des anticipations d'inflation au pays.",
                        "context": "Plusieurs trimestres de hausses successives des taux directeurs avaient été nécessaires pour refroidir la surchauffe post-pandémique.",
                        "importance": "Donne de la visibilité aux entreprises pour planifier leurs investissements en capital et leurs budgets de développement.",
                        "table": pd.DataFrame({
                            "Élément": ["Indicateur", "Date", "Taux actuel", "Tendance"],
                            "Information": ["IPC Global Canada", "30 août 2026", "2.1 %", "Stable / Neutre"]
                        }),
                        "impact": "Banque du Canada : neutre à positif\nTaux d'intérêt : stabilisation\nDollar canadien : résilient",
                        "futur": "Statu quo probable des taux directeurs lors de la prochaine réunion plénière de la banque centrale.",
                        "sources": ["Financial Post (5 min)", "La Presse Économie (6 min)"]
                    },
                    "related": [
                        {"titre": "Comprendre la dynamique de l'inflation et des taux au Canada", "source": "Banque du Canada (Note)", "temps": "6 min", "raison": "Document de référence officiel vulgarisé."},
                        {"titre": "Impacts de la stabilisation des prix sur les marchés financiers", "source": "Bloomberg Canada", "temps": "8 min", "raison": "Perspectives pour les investisseurs institutionnels et particuliers."}
                    ]
                }
            ]
        }

# --- 2. FENÊTRES CONTEXTUELLES (MODALS DÉTAILLÉES) ---
@st.dialog("📖 Fiche d'Analyse Détaillée", width="large")
def show_full_details(item):
    det = item["details"]
    st.subheader(item["title"])
    st.caption(f"Catégorie : {item['category']} • Publié {item['time']}")
    
    st.markdown("### 🧠 Ce qui s'est réellement passé")
    st.write(det["event"])
    
    st.markdown("### 📅 Contexte")
    st.write(det["context"])
    
    st.markdown("### 🔍 Pourquoi c'est important")
    st.write(det["importance"])
    
    st.markdown("### 📊 Données importantes")
    st.dataframe(det["table"], hide_index=True, use_container_width=True)
    
    st.markdown("### 🌎 Impact")
    st.text(det["impact"])
    
    st.markdown("### 🔮 Et ensuite ?")
    st.write(det["futur"])
    
    st.markdown("### 📰 Sources")
    for src in det["sources"]:
        st.markdown(f"- {src}")

@st.dialog("📰 Articles Reliés pour Approfondir", width="large")
def show_related_articles_modal(item):
    st.subheader(f"Dossier de lecture : {item['title']}")
    st.write("Sélection d'articles recommandés pour comprendre le sujet en profondeur, adaptés même aux débutants :")
    
    for i, art in enumerate(item["related"], 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {art['titre']}")
            st.caption(f"📍 {art['source']} — ⏱️ {art['temps']} de lecture")
            st.write(f"**Pourquoi cet article est intéressant :** {art['raison']}")
            st.button("Consulter l'article original ↗", key=f"read_src_{item['id']}_{i}")

# --- 3. INTERFACE PRINCIPALE ---
def main():
    init_session_state()
    
    # Navigation simple demandée
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Aller à", ["🏠 Accueil", "⚙️ Personnaliser", "📈 Portefeuille"])
    
    if page == "🏠 Accueil":
        st.title("MON BRIEFING")
        st.caption(f"30 août 2026")
        st.divider()
        
        # --- 🔥 À RETENIR ---
        st.header("🔥 À RETENIR")
        for top_item in st.session_state.news_database["top"]:
            with st.container(border=True):
                st.subheader(f"🤖 {top_item['title']}")
                st.caption(f"{top_item['category']}")
                st.write(top_item["summary"])
                st.caption(f"🕐 {top_item['time']}")
                
                c1, c2, _ = st.columns([1, 1, 3])
                if c1.button("📖 Plus de détails", key=f"btn_top_det_{top_item['id']}"):
                    show_full_details(top_item)
                if c2.button("📰 Articles reliés", key=f"btn_top_rel_{top_item['id']}"):
                    show_related_articles_modal(top_item)
        
        st.divider()
        
        # --- SECTIONS PAR CATÉGORIE (Minimum 1 article garanti) ---
        categories_keys = ["🌎 Monde", "🇨🇦 Canada", "⚜️ Québec", "🤖 Robotique", "💰 Économie"]
        
        for cat in categories_keys:
            st.header(cat)
            interests = st.session_state.categories.get(cat, [])
            if interests:
                st.caption("Intérêts suivis : " + " • ".join(interests))
            st.markdown("---")
            
            # Récupérer les articles de la catégorie
            articles = st.session_state.news_database.get(cat, [])
            
            if articles:
                for item in articles:
                    with st.container(border=True):
                        st.subheader(item["title"])
                        st.write(item["summary"])
                        st.caption(f"🕐 {item['time']}")
                        
                        b1, b2, _ = st.columns([1, 1, 3])
                        if b1.button("📖 Plus de détails", key=f"det_{item['id']}"):
                            show_full_details(item)
                        if b2.button("📰 Articles reliés", key=f"rel_{item['id']}"):
                            show_related_articles_modal(item)
            else:
                st.info(f"Aucune nouvelle pour le moment dans la section {cat}.")
            
            st.write("")

        # --- 📈 INVESTISSEMENTS ---
        st.header("📈 INVESTISSEMENTS")
        st.markdown("---")
        st.caption("Actualités connectées directement aux actions configurées dans votre portefeuille.")
        
        # Simulation d'actualités boursières liées au portefeuille
        portfolio_news = [
            {
                "ticker": "XEQT",
                "title": "XEQT : Résilience des marchés mondiaux face aux variations de taux",
                "summary": "L'ETF diversifié mondial maintient une excellente tenue grâce à l'équilibre de ses positions géographiques et sectorielles, offrant un profil de rendement stable aux investisseurs à long terme.",
                "time": "Il y a 3 h",
                "details": {
                    "event": "Analyse de la performance trimestrielle des composantes majeurs de l'indice global.",
                    "context": "La diversification géographique reste la meilleure protection contre la volatilité locale.",
                    "importance": "Confirme la pertinence d'une détention indicielle à large spectre.",
                    "table": pd.DataFrame({"Métrique": ["Rendement YTD", "Volatilité"], "Valeur": ["+8.4%", "Faible"]}),
                    "impact": "Portefeuille global : Stable et diversifié",
                    "futur": "Poursuite de la stratégie d'accumulation passive recommandée.",
                    "sources": ["Morningstar Canada", "Financial Post"]
                },
                "related": [{"titre": "Pourquoi garder le cap sur les ETF mondiaux", "source": "Journal des Investisseurs", "temps": "5 min", "raison": "Rappel des principes de gestion indicielle."}]
            },
            {
                "ticker": "SHOP",
                "title": "SHOP : Nouvelle mise à jour de l'écosystème marchand et intégration logistique",
                "summary": "Shopify déploie de nouvelles fonctionnalités d'automatisation des stocks pour ses marchands, renforçant son avantage concurrentiel dans le commerce en ligne transfrontalier.",
                "time": "Il y a 4 h",
                "details": {
                    "event": "Lancement d'outils de gestion intelligente des flux de marchandises pour les boutiques à fort volume.",
                    "context": "La saison des achats de fin d'année approche, poussant la plateforme à optimiser son infrastructure.",
                    "importance": "Soutient la croissance du volume brut de marchandises (GMV).",
                    "table": pd.DataFrame({"Métrique": ["Hausse d'adoption", "Impact opérationnel"], "Valeur": ["+15%", "Réduction des frictions logistiques"]}),
                    "impact": "Action SHOP : Potentiel haussier à moyen terme",
                    "futur": "Surveillance des volumes transactionnels lors du prochain trimestre.",
                    "sources": ["TechCrunch", "Bloomberg Tech"]
                },
                "related": [{"titre": "L'expansion logistique de Shopify", "source": "TechCrunch", "temps": "6 min", "raison": "Analyse de la stratégie de logistique intégrée."}]
            },
            {
                "ticker": "NVDA",
                "title": "NVDA : Partenariat élargi avec les fabricants de systèmes robotiques autonomes",
                "summary": "Nvidia annonce l'optimisation de sa plateforme matérielle pour le traitement en temps réel des modèles de vision par ordinateur appliqués à la robotique mobile.",
                "time": "Il y a 2 h",
                "details": {
                    "event": "Présentation des nouveaux kits de développement pour puces embarquées à haute efficacité énergétique.",
                    "context": "L'explosion de la demande en robotique humanoïde et industrielle nécessite des processeurs ultra-performants en bordure de réseau.",
                    "importance": "Positionne l'entreprise au cœur de la chaîne de valeur de la robotique intelligente.",
                    "table": pd.DataFrame({"Métrique": ["Nouveau processeur", "Gain énergétique"], "Valeur": ["Plateforme Thor", "3x plus efficace"]}),
                    "impact": "Action NVDA : Position dominante confirmée dans l'IA physique",
                    "futur": "Livraisons massives prévues pour les constructeurs de robots partenaires.",
                    "sources": ["Reuters", "EE Times"]
                },
                "related": [{"titre": "L'offensive de Nvidia dans l'IA physique et la robotique", "source": "IEEE Spectrum", "temps": "7 min", "raison": "Comprendre l'extension du marché adressable de l'entreprise."}]
            }
        ]
        
        for stock in portfolio_news:
            with st.container(border=True):
                st.markdown(f"**[{stock['ticker']}]** — {stock['title']}")
                st.write(stock["summary"])
                st.caption(f"🕐 {stock['time']}")
                
                b1, b2, _ = st.columns([1, 1, 3])
                if b1.button("📖 Plus de détails", key=f"det_stock_{stock['ticker']}"):
                    show_full_details(stock)
                if b2.button("📰 Articles reliés", key=f"rel_stock_{stock['ticker']}"):
                    show_related_articles_modal(stock)

    elif page == "⚙️ Personnaliser":
        st.title("⚙️ PERSONNALISATION")
        st.write("Ajustez vos catégories et gérez vos intérêts de veille.")
        st.divider()
        
        # Ajout d'une catégorie
        new_cat_input = st.text_input("Ajouter une catégorie (ex: 🧬 Santé)")
        if st.button("➕ Ajouter la catégorie"):
            if new_cat_input and new_cat_input not in st.session_state.categories:
                st.session_state.categories[new_cat_input] = []
                st.success(f"Catégorie {new_cat_input} ajoutée avec succès !")
                st.rerun()
                
        st.divider()
        
        # Gestion des intérêts par catégorie
        for cat, interests in list(st.session_state.categories.items()):
            with st.expander(f"📁 {cat}", expanded=True):
                updated_interests = st.multiselect(
                    f"Intérêts pour {cat}",
                    options=interests + ["Ajouter un intérêt..."],
                    default=interests,
                    key=f"ms_{cat}"
                )
                
                new_interest = st.text_input(f"Ajouter un intérêt dans {cat}", key=f"new_int_{cat}", placeholder="Taper un intérêt et valider...")
                if st.button(f"Ajouter à {cat}", key=f"btn_add_{cat}"):
                    if new_interest and new_interest not in st.session_state.categories[cat]:
                        st.session_state.categories[cat].append(new_interest)
                        st.success(intérêt ajouté)
                        st.rerun()

                # Mise à jour si l'utilisateur retire des éléments
                clean_interests = [i for i in updated_interests if i != "Ajouter un intérêt..."]
                if clean_interests != st.session_state.categories[cat]:
                    st.session_state.categories[cat] = clean_interests

    elif page == "📈 Portefeuille":
        st.title("📈 PORTEFEUILLE")
        st.write("Gestion de vos titres actifs connectés au système de veille.")
        st.divider()
        
        for ticker, data in st.session_state.portfolio.items():
            with st.container(border=True):
                st.subheader(f"{ticker} — {data['nom']}")
                st.write(f"Actions détenues : {data['shares']}")
        
        st.info("Le portefeuille est synchronisé automatiquement avec la section Investissements de votre page d'accueil.")

if __name__ == "__main__":
    st.set_page_config(page_title="Mon Briefing Personnel", layout="wide")
    main()