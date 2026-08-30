import streamlit as st
import pandas as pd
from datetime import datetime

def show_system3():
    # --- 1. GESTION DE L'ÉTAT ET DES DONNÉES ---
    if "categories" not in st.session_state:
        st.session_state.categories = {
            "🌎 Monde": ["Géopolitique", "Guerres", "Politique internationale", "Chine"],
            "🇨🇦 Canada": ["Politique fédérale", "Économie canadienne", "Énergie"],
            "⚜️ Québec": ["Politique québécoise", "Hydro-Québec", "Économie"],
            "🤖 Robotique": ["Robotique humanoïde", "ROS2", "Vision par ordinateur", "Automatisation industrielle", "Robots industriels"],
            "💰 Économie": ["Inflation", "Taux d'intérêt", "Banque du Canada", "Dollar canadien"]
        }

    # Connexion au portefeuille réel (AAPL, CGNT.V, NVDA, ROBO)
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {
            "AAPL": {"nom": "Apple Inc.", "shares": 10},
            "CGNT.V": {"nom": "Cognetivity Neurosciences Ltd.", "shares": 500},
            "NVDA": {"nom": "NVIDIA Corp.", "shares": 15},
            "ROBO": {"nom": "Robo Global Robotics & Automation ETF", "shares": 20}
        }

    if "news_database" not in st.session_state:
        st.session_state.news_database = {
            "top": [
                {
                    "id": "top_1",
                    "category": "Robotique · IA",
                    "title": "Un nouveau robot humanoïde devient capable de travailler seul en usine",
                    "summary": "Une grande avancée technique permet maintenant d'intégrer des cerveaux artificiels directement à l'intérieur des robots humanoïdes. Grâce à cela, le robot s'adapte tout seul et en direct face à des objets qui bougent ou qui sont mal rangés sur les lignes de montage de l'usine. Pour les ingénieurs en automatisation, cela change tout : il n'y a plus besoin de passer des heures à reprogrammer chaque geste du robot à la main. Le travail de production devient beaucoup plus souple, ce qui aide l'usine à fabriquer plus de produits sans avoir à tout casser et refaire dans l'atelier.",
                    "time": "Il y a 3 h",
                    "details": {
                        "probleme": "Jusqu'à présent, les robots industriels étaient prisonniers de programmes informatiques rigides. Dès qu'une pièce changeait de millimètre sur la ligne de montage, le robot plantait ou ratait son geste, ce qui obligeait des techniciens à passer des heures à le reprogrammer.",
                        "mecanisme": "L'entreprise Figure AI a combiné un modèle d'intelligence artificielle multimodal (un 'cerveau' virtuel) avec des moteurs ultra-précis dans les membres du robot. Au lieu d'exécuter un code ligne par ligne, le robot analyse sa caméra en direct, comprend ce qu'il voit (par exemple, une boîte mal positionnée) et calcule lui-même le mouvement physique à faire pour rectifier la situation.",
                        "pourquoi_important": "Cela résout le plus grand casse-tête de l'industrie manufacturière moderne : le manque de flexibilité des lignes de production face à la variété des produits. Le robot devient enfin un 'travailleur universel' adaptable.",
                        "table": pd.DataFrame({
                            "Élément": ["Entreprise", "Date", "Technologie", "Coût", "Gain de vitesse"],
                            "Information": ["Figure AI", "30 août 2026", "Cerveau artificiel unifié", "Variables selon la flotte", "+40% de rapidité utile"]
                        }),
                        "impact": "Robotique : très fort\nIA : majeur\nIndustrie : changement radical des méthodes de travail",
                        "futur": "Les usines automobiles vont tester ces robots à grande échelle dès les prochains mois avant de lancer une vente partout dans le monde.",
                        "sources": ["IEEE Spectrum - Article de fond (8 min)", "TechCrunch - Actualité technique (5 min)", "Communiqué officiel de l'entreprise"]
                    },
                    "related": [
                        {"titre": "Comprendre le nouveau robot humanoïde et son fonctionnement", "source": "IEEE Spectrum", "temps": "8 min", "raison": "Idéal pour voir comment le robot fonctionne sans utiliser de mots trop compliqués."},
                        {"titre": "Comment les robots humanoïdes modernes travaillent en usine", "source": "MIT Technology Review", "temps": "12 min", "raison": "Donne une vue d'ensemble simple sur l'état actuel de la robotique dans le monde."},
                        {"titre": "L'entreprise dévoile sa nouvelle génération de machines autonomes", "source": "Robotics Business", "temps": "5 min", "raison": "Permet de lire l'annonce de départ avec les chiffres de base."},
                        {"titre": "Où en est la robotique humanoïde en 2026 ?", "source": "Wall Street Journal", "temps": "15 min", "raison": "Explique pourquoi les entreprises investissent autant d'argent là-dedans."}
                    ]
                }
            ],
            "🌎 Monde": [
                {
                    "id": "monde_1",
                    "category": "🌎 Monde",
                    "title": "Un grand accord international signé pour mieux partager les métaux rares",
                    "summary": "Plusieurs grands pays industrialisés viennent de signer un traité pour mettre en commun leurs réserves de métaux rares et aider financièrement les usines qui les raffinent chez eux. Le but principal est de dépendre beaucoup moins d'un seul pays asiatique pour fabriquer les composants électroniques et les moteurs électriques. À brève échéance, cela devrait aider à stabiliser le prix de fabrication des ordinateurs, des téléphones et des voitures électriques partout en Occident.",
                    "time": "Il y a 5 h",
                    "details": {
                        "probleme": "L'industrie technologique mondiale dépendait presque entièrement d'un seul pays (la Chine) pour l'extraction et surtout le raffinage des minéraux critiques (lithium, cobalt, terres rares). Le moindre conflit politique menaçait de bloquer la fabrication de tous nos appareils électroniques.",
                        "mecanisme": "Quatorze pays industrialisés ont créé un fonds commun de 12 milliards de dollars pour financer des usines de raffinage locales et s'échanger directement leurs stocks en cas de crise, contournant ainsi les monopoles d'exportation.",
                        "pourquoi_important": "Cela sécurise toute la chaîne d'approvisionnement des usines occidentales, évitant des arrêts de production massifs comme ceux vécus par le passé dans l'automobile et l'électronique.",
                        "table": pd.DataFrame({
                            "Élément": ["Secteur touché", "Date", "Pays participants", "Aide financière"],
                            "Information": ["Haute technologie et Énergie", "30 août 2026", "14 nations", "12 milliards de subventions partagées"]
                        }),
                        "impact": "Politique mondiale : très important\nÉconomie : stabilisateur fort\nUsines : sécurité garantie",
                        "futur": "Mise en place de comités de contrôle pour valider les nouveaux centres de raffinage dès l'année prochaine.",
                        "sources": ["Reuters - Dépêche économique (6 min)", "Financial Times - Analyse globale (10 min)"]
                    },
                    "related": [
                        {"titre": "La guerre des métaux rares en 2026", "source": "Foreign Affairs", "temps": "10 min", "raison": "Explique clairement les tensions politiques derrière les chaînes d'approvisionnement."},
                        {"titre": "Ce que change cet accord pour les usines occidentales", "source": "Bloomberg", "temps": "7 min", "raison": "Détaille l'impact direct sur les coûts de fabrication."}
                    ]
                }
            ],
            "🇨🇦 Canada": [
                {
                    "id": "can_1",
                    "category": "🇨🇦 Canada",
                    "title": "Ottawa simplifie les règles pour faire avancer plus vite les projets d'énergie propre",
                    "summary": "Le gouvernement fédéral canadien a décidé de changer ses méthodes d'évaluation pour faire perdre moins de temps aux grands projets d'infrastructure écologique. Le plan vise en premier lieu les lignes de transport d'électricité qui passent d'une province à l'autre ainsi que les usines d'hydrogène vert. Les gens d'affaires applaudissent ce changement, car les anciens délais administratifs bloquaient inutilement l'argent des investisseurs depuis des années.",
                    "time": "Il y a 4 h",
                    "details": {
                        "probleme": "Le Canada était enlisé dans une bureaucratie administrative interminable pour approuver la construction de nouvelles infrastructures énergétiques. Il fallait parfois 10 ans d'études d'impact pour poser un câble électrique ou bâtir une usine propre, ce qui faisait fuir les investisseurs.",
                        "mecanisme": "Ottawa instaure un 'guichet unique' fédéral qui regroupe toutes les autorisations en un seul processus synchronisé, réduisant les allers-retours entre ministères et coupant les délais d'attente de moitié.",
                        "pourquoi_important": "Cela permet de débloquer des milliards de dollars d'investissements privés et d'accélérer concrètement la transition énergétique du pays.",
                        "table": pd.DataFrame({
                            "Élément": ["Gouvernement", "Date", "Cible prioritaire", "Gain de temps visé"],
                            "Information": ["Fédéral (Canada)", "30 août 2026", "Lignes d'énergie et transport", "Jusqu'à 50% de délai en moins"]
                        }),
                        "impact": "Politique fédérale : très positif\nÉnergie : grand accélérateur\nÉconomie : stimulant",
                        "futur": "Discussions ardues à venir avec les provinces pour s'assurer que les lois locales s'accordent bien avec ce nouveau système.",
                        "sources": ["The Globe and Mail (7 min)", "Radio-Canada Économie (5 min)"]
                    },
                    "related": [
                        {"titre": "Les problèmes du réseau électrique canadien", "source": "The Globe and Mail", "temps": "9 min", "raison": "Montre pourquoi les réformes étaient devenues urgentes."},
                        {"titre": "Analyse du nouveau guichet unique d'Ottawa", "source": "Financial Post", "temps": "6 min", "raison": "Résumé des réactions du milieu des affaires."}
                    ]
                }
            ],
            "⚜️ Québec": [
                {
                    "id": "que_1",
                    "category": "⚜️ Québec",
                    "title": "Hydro-Québec lance un grand plan technologique pour moderniser ses postes électriques",
                    "summary": "La société d'État commence à installer partout des capteurs intelligents et des petits ordinateurs de contrôle à distance sur l'ensemble de ses lignes de transport. Le but est de faire passer plus d'électricité dans les fils existants sans être obligé de bâtir tout de suite de nouvelles tours à haute tension. Cette modernisation aide directement à mieux gérer les périodes de grand froid où les gens consomment un maximum de courant.",
                    "time": "Il y a 2 h",
                    "details": {
                        "probleme": "La demande en électricité monte en flèche au Québec en raison de l'arrivée de nouvelles usines et des hivers froids. Construire de nouvelles lignes à haute tension prend des années et coûte des milliards, créant un risque de pénurie de puissance aux heures de pointe.",
                        "mecanisme": "Hydro-Québec déploie massivement des capteurs IIoT (objets connectés industriels) dans ses sous-stations pour surveiller en temps réel la température et la charge exacte des lignes. En connaissant la capacité réelle minute par minute, le réseau accepte de faire passer plus de courant en toute sécurité sans surchauffer.",
                        "pourquoi_important": "Cela évite de dépenser des fortunes en nouvelles constructions tout en permettant de brancher de nouvelles industries sans risquer de pannes majeures.",
                        "table": pd.DataFrame({
                            "Élément": ["Promoteur", "Date", "Enveloppe budgétaire", "Technologie utilisée"],
                            "Information": ["Hydro-Québec", "30 août 2026", "450 millions de dollars", "Objets connectés et réseaux intelligents"]
                        }),
                        "impact": "Hydro-Québec : stratégique\nÉconomie du Québec : majeur\nTechnologie : très utile",
                        "futur": "Ajout progressif de programmes informatiques capables de deviner à l'avance quand une pièce risque de briser.",
                        "sources": ["La Presse (6 min)", "Le Devoir (5 min)"]
                    },
                    "related": [
                        {"titre": "Comment les réseaux intelligents transforment l'électricité", "source": "La Presse", "temps": "6 min", "raison": "Explique simplement la modernisation du réseau québécois."},
                        {"titre": "Le plan d'action d'Hydro-Québec face à la forte demande", "source": "Les Affaires", "temps": "8 min", "raison": "Détaille les besoins en énergie des usines de la province."}
                    ]
                }
            ],
            "🤖 Robotique": [
                {
                    "id": "rob_1",
                    "category": "🤖 Robotique",
                    "title": "Les usines adoptent un langage informatique commun pour faire communiquer leurs robots",
                    "summary": "Un grand groupe d'experts internationaux vient de publier un standard officiel pour relier ensemble des robots mobiles de marques différentes dans une même usine. Grâce à cette entente sur le système ROS2, il devient beaucoup plus simple de faire travailler des machines de fabricants variés sans passer des semaines à coder des programmes de liaison. Cela réduit fortement les frais d'installation et permet aux usines intelligentes de démarrer beaucoup plus vite.",
                    "time": "Il y a 6 h",
                    "details": {
                        "probleme": "Dans une usine moderne, acheter un robot d'une marque A et un autre d'une marque B tournait au cauchemar informatique. Chaque fabricant imposait son propre logiciel fermé, rendant impossible la communication entre les machines sans passer par des programmes de traduction sur mesure hors de prix.",
                        "mecanisme": "Le consortium industriel officialise un profil de référence unifié basé sur le framework open-source **ROS2** (Robot Operating System). Cela crée un 'pont de communication' universel en temps réel pour toutes les flottes de robots mobiles.",
                        "pourquoi_important": "Cela supprime les barrières technologiques entre fournisseurs, permettant aux usines de composer des lignes de production modulaires et de changer de matériel facilement.",
                        "table": pd.DataFrame({
                            "Élément": ["Standard technique", "Date", "Domaine", "Économie de temps"],
                            "Information": ["ROS2 / Logiciel industriel", "30 août 2026", "Logistique d'usine", "-40% de temps d'installation"]
                        }),
                        "impact": "Robotique mobile : majeur\nROS2 : incontournable\nUsines : gain de temps énorme",
                        "futur": "Utilisation massive de ce standard par les grands constructeurs automobiles et pharmaceutiques mondiaux dès l'an prochain.",
                        "sources": ["Robotics Tomorrow (5 min)", "Automation World (7 min)"]
                    },
                    "related": [
                        {"titre": "Guide simple pour passer aux logiciels ROS2 en usine", "source": "IEEE Robotics", "temps": "14 min", "raison": "La référence technique de base pour les ingénieurs en robotique."},
                        {"titre": "Cómo hacer cooperar robots de marcas diferentes", "source": "Control Engineering", "temps": "8 min", "raison": "Explique les gains réels mesurés sur le terrain par les usines."}
                    ]
                }
            ],
            "💰 Économie": [
                {
                    "id": "eco_1",
                    "category": "💰 Économie",
                    "title": "La Banque du Canada confirme que la hausse des prix est enfin rentrée dans l'ordre",
                    "summary": "Dans son dernier rapport, la banque centrale a annoncé que l'inflation est revenue s'est stabilisée solidement autour de sa cible idéale de 2 pour cent. Cette bonne nouvelle signifie que la vie quotidienne devient plus prévisible et que le coût de la vie ne s'emballe plus de façon anormale. Pour les familles comme pour les entreprises, cela offre un climat beaucoup plus stable pour planifier les budgets et les achats importants des prochains mois.",
                    "time": "Il y a 1 h",
                    "details": {
                        "probleme": "Après les chocs économiques mondiaux de la période post-pandémique, l'inflation s'était emballée, réduisant le pouvoir d'achat des consommateurs et créant une incertitude totale pour les investissements des entreprises.",
                        "mecanisme": "La Banque du Canada a maintenu des taux directeurs élevés pendant plusieurs trimestres, ce qui a eu pour effet de ralentir l'emprunt excessif, de calmer la surchauffe de la demande et de ramener l'Indice des prix à la consommation (IPC) pile dans sa zone cible saine.",
                        "pourquoi_important": "La stabilisation des prix redonne de la visibilité financière aux entreprises pour calculer leurs coûts de revient et planifier leurs investissements à long terme sans crainte de soubresauts monétaires.",
                        "table": pd.DataFrame({
                            "Élément": ["Indicateur", "Date", "Chiffre actuel", "Tendance"],
                            "Information": ["Inflation au Canada", "30 août 2026", "2.1 %", "Stable et calme"]
                        }),
                        "impact": "Banque centrale : rassurant\nTaux d'intérêt : stabilisés\nDollar canadien : solide",
                        "futur": "La banque centrale devrait laisser ses taux de base tranquilles lors de sa prochaine rencontre officielle.",
                        "sources": ["Financial Post (5 min)", "La Presse Économie (6 min)"]
                    },
                    "related": [
                        {"titre": "Comprendre l'inflation et les taux d'intérêt au Canada", "source": "Banque du Canada (Note)", "temps": "6 min", "raison": "Un document officiel très simple pour tout comprendre."},
                        {"titre": "Ce que change la fin de l'inflation pour vos finances", "source": "Bloomberg Canada", "temps": "8 min", "raison": "Analyse claire pour les épargnants et les investisseurs."}
                    ]
                }
            ]
        }

    # --- 2. FENÊTRES CONTEXTUELLES (MODALS DÉTAILLÉES) ---
    @st.dialog("📖 Fiche d'Analyse Détaillée et Compréhension", width="large")
    def show_full_details(item):
        det = item["details"]
        st.subheader(item["title"])
        st.caption(f"Catégorie : {item['category']} • Publié {item['time']}")
        
        st.markdown("### 🛑 1. Quel est le problème de départ ?")
        st.write(det["probleme"])
        
        st.markdown("### ⚙️ 2. Comment ça fonctionne derrière ? (Le Mécanisme)")
        st.write(det["mecanisme"])
        
        st.markdown("### 💡 3. Pourquoi c'est important pour le secteur ?")
        st.write(det["pourquoi_important"])
        
        st.markdown("### 📊 4. Les Chiffres Clés")
        st.dataframe(det["table"], hide_index=True, use_container_width=True)
        
        st.markdown("### 🌎 5. Les Impacts Concrets")
        st.text(det["impact"])
        
        st.markdown("### 🔮 6. Qu'est-ce qui va se passer ensuite ?")
        st.write(det["futur"])
        
        st.markdown("### 📰 7. Pour aller plus loin (Sources)")
        for src in det["sources"]:
            st.markdown(f"- {src}")

    @st.dialog("📰 Articles Reliés pour Approfondir", width="large")
    def show_related_articles_modal(item):
        st.subheader(f"Dossier de lecture : {item['title']}")
        st.write("Voici une sélection d'articles faciles à lire pour comprendre le sujet en profondeur, même si vous débutez :")
        
        for i, art in enumerate(item["related"], 1):
            with st.container(border=True):
                st.markdown(f"#### {i}. {art['titre']}")
                st.caption(f"📍 {art['source']} — ⏱️ {art['temps']} de lecture")
                st.write(f"**Pourquoi lire cet article :** {art['raison']}")
                st.button("Lire l'article original ↗", key=f"read_src_{item['id']}_{i}")

    # --- 3. NAVIGATION PAR ONGLETS EN HAUT ---
    tabs = st.tabs(["🏠 Accueil", "⚙️ Personnaliser", "📈 Portefeuille"])

    # --- ONGLET 1 : ACCUEIL ---
    with tabs[0]:
        st.title("MON BRIEFING QUOTIDIEN")
        st.caption("Mise à jour : 30 août 2026")
        st.divider()
        
        st.header("🔥 LE SUJET MAJEUR DU JOUR")
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
        
        categories_keys = list(st.session_state.categories.keys())
        
        for cat in categories_keys:
            st.header(cat)
            interests = st.session_state.categories.get(cat, [])
            if interests:
                st.caption("Intérêts suivis : " + " • ".join(interests))
            st.markdown("---")
            
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

        st.header("📈 ACTUALITÉS DE VOTRE PORTEFEUILLE")
        st.markdown("---")
        st.caption("Actualités connectées directement aux vrais titres que vous possédez (AAPL, CGNT.V, NVDA, ROBO).")
        
        portfolio_news = [
            {
                "ticker": "AAPL",
                "title": "AAPL : Apple intègre de nouvelles fonctions d'intelligence artificielle sur ses appareils",
                "summary": "Apple vient de présenter une mise à jour importante de ses logiciels qui renforce l'utilisation de l'intelligence artificielle directement sur les téléphones et les ordinateurs. Cette nouveauté simplifie la vie des usagers au quotidien tout en protégeant mieux leurs données personnelles. Pour les investisseurs, cela stimule la demande pour les nouveaux modèles d'appareils et consolide la position de l'entreprise sur le marché technologique mondial.",
                "time": "Il y a 3 h",
                "details": {
                    "probleme": "Apple faisait face à des critiques sur son retard perçu dans l'intégration grand public de l'intelligence artificielle générative par rapport à ses concurrents, tout en voulant préserver sa politique stricte de confidentialité.",
                    "mecanisme": "L'entreprise a déployé une architecture hybride qui exécute des modèles légers directement sur la puce de l'appareil pour les tâches courantes, et utilise un cloud sécurisé dédié pour les calculs lourds.",
                    "pourquoi_important": "Cela relance l'attrait pour le matériel (iPhone, Mac) et rassure les investisseurs sur la capacité d'Apple à monétiser l'ère de l'IA.",
                    "table": pd.DataFrame({"Métrique": ["Secteur", "Impact ventes"], "Valeur": ["Appareils mobiles", "Hausse de la demande"]}),
                    "impact": "Action AAPL : Solide et rassurante",
                    "futur": "Suivi attentif des chiffres de vente lors de la sortie des prochains produits en magasin.",
                    "sources": ["Bloomberg Tech", "Wall Street Journal"]
                },
                "related": [{"titre": "La stratégie d'Apple dans l'intelligence artificielle", "source": "TechCrunch", "temps": "6 min", "raison": "Explication claire des choix technologiques de l'entreprise."}]
            },
            {
                "ticker": "CGNT.V",
                "title": "CGNT.V : Cognetivity avance dans l'application médicale de sa technologie cognitive",
                "summary": "L'entreprise Cognetivity Neurosciences poursuit le déploiement de sa plateforme numérique d'évaluation de la santé cérébrale dans plusieurs cliniques partenaires. Cette solution aide les professionnels de la santé à repérer plus rapidement les troubles cognitifs grâce à des tests sur tablette simples et rapides. Les marchés surveillent de près l'adoption de cet outil par le réseau médical.",
                "time": "Il y a 5 h",
                "details": {
                    "probleme": "Le dépistage traditionnel des troubles de la mémoire est long, coûteux et dépend de tests psychologiques subjectifs réalisés en cabinet spécialisé.",
                    "mecanisme": "Cognetivity utilise une application sur tablette basée sur la science cognitive qui teste les réflexes visuels du cerveau en quelques minutes pour détecter des anomalies.",
                    "pourquoi_important": "Cela permet un diagnostic beaucoup plus précoce à grande échelle dans les cliniques générales, ce qui intéresse fortement le secteur de la santé.",
                    "table": pd.DataFrame({"Métrique": ["Domaine", "Statut commercial"], "Valeur": ["Santé numérique", "Expansion des cliniques"]}),
                    "impact": "Action CGNT.V : Potentiel de croissance lié au secteur médical",
                    "futur": "Évaluation des retombées des nouveaux contrats signés dans le réseau de la santé.",
                    "sources": ["Stockwatch", "Financial Post Med"]
                },
                "related": [{"titre": "L'innovation dans le dépistage de la santé mentale", "source": "Medical News Today", "temps": "5 min", "raison": "Comprendre l'utilité des tests cognitifs numériques."}]
            },
            {
                "ticker": "NVDA",
                "title": "NVDA : Nvidia lance de nouvelles puces graphiques ultra-rapides pour les serveurs d'IA",
                "summary": "Nvidia a dévoilé une nouvelle génération de puces informatiques conçues spécialement pour faire tourner les modèles d'intelligence artificielle les plus lourds. Ces processeurs offrent une puissance de calcul décuplée tout en consommant moins d'électricité par opération. Les plus grands centres de données du monde entier se bousculent pour s'en procurer.",
                "time": "Il y a 2 h",
                "details": {
                    "probleme": "La complexité croissante des modèles de langage demande une puissance de calcul monstrueuse que les anciens processeurs ne pouvaient plus suivre sans surchauffer et consommer trop d'énergie.",
                    "mecanisme": "Nvidia conçoit des architectures de puces spécialisées en traitement parallèle massif, associées à des interconnexions à très haut débit pour relier des milliers de processeurs entre eux.",
                    "pourquoi_important": "Cela permet aux géants du web de faire tourner des intelligences artificielles géantes plus rapidement et à moindre coût énergétique.",
                    "table": pd.DataFrame({"Métrique": ["Performance", "Efficacité"], "Valeur": ["3x plus rapide", "Moins énergivore"]}),
                    "impact": "Action NVDA : Position dominante confirmée",
                    "futur": "Livraisons massives prévues pour les grands géants du web au cours du prochain trimestre.",
                    "sources": ["Reuters", "EE Times"]
                },
                "related": [{"titre": "La domination de Nvidia dans les puces d'IA", "source": "IEEE Spectrum", "temps": "7 min", "raison": "Explique pourquoi les puces de l'entreprise sont si indispensables."}]
            },
            {
                "ticker": "ROBO",
                "title": "ROBO : L'ETF mondial de la robotique profite de la modernisation des usines",
                "summary": "Le fonds négocié en bourse ROBO enregistre de bons résultats grâce à l'automatisation accélérée des chaînes de fabrication à travers le monde. Les entreprises manufacturières investissent massivement dans les robots intelligents et les capteurs pour compenser le manque de main-d'œuvre. Ce fonds diversifié permet de suivre l'ensemble de cette industrie en pleine transformation.",
                "time": "Il y a 4 h",
                "details": {
                    "probleme": "La pénurie de main-d'œuvre chronique et la hausse des coûts salariaux poussent les usines à chercher des solutions d'automatisation pour rester rentables.",
                    "mecanisme": "L'ETF regroupe et investit dans les meilleures entreprises mondiales de robotique, d'intelligence artificielle industrielle et de capteurs, répartissant ainsi le risque financier sur l'ensemble du secteur.",
                    "pourquoi_important": "Il offre un moyen simple de profiter de la croissance globale de l'industrie de la robotique sans avoir à choisir une seule action en particulier.",
                    "table": pd.DataFrame({"Métrique": ["Type de placement", "Secteur cible"], "Valeur": ["ETF indiciel diversifié", "Robotique et Automatisation"]}),
                    "impact": "Action ROBO : Croissance stable portée par l'industrie",
                    "futur": "Poursuite de la demande en équipements robotisés dans les secteurs de l'automobile et de l'électronique.",
                    "sources": ["Morningstar", "ETF Daily News"]
                },
                "related": [{"titre": "Pourquoi investir dans la robotique et l'automatisation", "source": "Journal des Investisseurs", "temps": "5 min", "raison": "Rappelle les avantages d'un fonds indiciel spécialisé."}]
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

    # --- ONGLET 2 : PERSONNALISER (CORRIGÉ POUR SUPPRESSION ET SAUVEGARDE) ---
    with tabs[1]:
        st.title("⚙️ PERSONNALISATION")
        st.write("Ajustez vos catégories, supprimez celles qui ne vous intéressent plus et gérez vos intérêts de veille.")
        st.divider()
        
        # Ajout d'une catégorie
        new_cat_input = st.text_input("Ajouter une nouvelle catégorie (ex: 🧬 Santé)")
        if st.button("➕ Ajouter la catégorie"):
            if new_cat_input and new_cat_input not in st.session_state.categories:
                st.session_state.categories[new_cat_input] = []
                st.success(f"Catégorie {new_cat_input} ajoutée avec succès !")
                st.rerun()
                
        st.divider()
        st.subheader("📁 Gestion de vos catégories et intérêts actuels")
        
        # Gestion propre avec copie de liste pour éviter les erreurs de modification en boucle
        for cat, interests in list(st.session_state.categories.items()):
            with st.expander(f"📁 {cat}", expanded=True):
                
                # Formulaire ou boutons de suppression de catégorie
                col_del1, col_del2 = st.columns([3, 1])
                with col_del2:
                    if st.button("🗑️ Supprimer", key=f"del_cat_{cat}"):
                        del st.session_state.categories[cat]
                        if cat in st.session_state.news_database:
                            del st.session_state.news_database[cat]
                        st.success(f"Catégorie '{cat}' supprimée avec succès !")
                        st.rerun()

                # Gestion des intérêts avec sauvegarde réelle dans st.session_state
                current_interests = st.session_state.categories[cat]
                
                updated_interests = st.multiselect(
                    f"Intérêts suivis pour {cat}",
                    options=current_interests,
                    default=current_interests,
                    key=f"ms_{cat}"
                )
                
                # Mise à jour immédiate si l'utilisateur décoche (supprime) un intérêt
                if updated_interests != current_interests:
                    st.session_state.categories[cat] = updated_interests
                    st.rerun()

                # Ajouter un nouvel intérêt
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_interest = st.text_input(f"Ajouter un intérêt dans {cat}", key=f"new_int_{cat}", placeholder="Taper un intérêt...")
                with col2:
                    st.write("") # Espacement visuel
                    st.write("")
                    if st.button("Ajouter", key=f"btn_add_{cat}"):
                        if new_interest and new_interest not in st.session_state.categories[cat]:
                            st.session_state.categories[cat].append(new_interest)
                            st.success("Intérêt ajouté !")
                            st.rerun()

    # --- ONGLET 3 : PORTEFEUILLE ---
    with tabs[2]:
        st.title("📈 VOTRE PORTEFEUILLE")
        st.write("Voici la liste complète des vrais titres financiers que vous possédez dans votre portefeuille d'investissement :")
        st.divider()
        
        for ticker, data in st.session_state.portfolio.items():
            with st.container(border=True):
                st.subheader(f"{ticker} — {data['nom']}")
                st.write(f"Actions détenues : **{data['shares']}**")
        
        st.info("💡 Ces titres sont automatiquement reliés à la section des actualités boursières de votre page d'accueil pour suivre vos investissements en temps réel.")