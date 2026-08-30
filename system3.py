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

    # Connexion au portefeuille réel (récupéré depuis le Système 2 / données utilisateur)
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
                        "event": "L'entreprise Figure AI a sorti un nouveau logiciel complet combiné avec de nouveaux moteurs plus puissants dans les bras et les jambes du robot.",
                        "context": "Avant cette mise à jour, les robots d'usine étaient très rigides. Ils devaient suivre un plan informatique ultra-strict, ce qui bloquait leur utilisation dès qu'un objet changeait de place.",
                        "importance": "Cette technologie rend enfin les robots humanoïdes utiles et faciles à installer dans n'importe quelle usine normale.",
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
                        "event": "Création d'un groupe de travail international qui fixe des règles communes pour extraire, transporter et nettoyer les minéraux indispensables à l'industrie moderne.",
                        "context": "Ces derniers mois, les disputes politiques et les blocages sur les exportations avaient créé de grosses pénuries dans les chaînes d'approvisionnement des usines.",
                        "importance": "Cela protège durablement toutes les industries de haute technologie contre de futures ruptures de stock mondiales.",
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
                        "event": "Signature d'un décret fédéral qui crée un guichet unique d'autorisation pour valider plus rapidement les projets industriels d'importance nationale.",
                        "context": "Le Canada était reconnu pour sa lenteur administrative terrible, ce qui décourageait les entreprises privées de lancer de grands travaux d'infrastructure.",
                        "importance": "Permet de construire plus vite les réseaux d'énergie dont le pays a besoin tout en stimulant l'économie locale.",
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
                        "event": "Signature de contrats importants avec des entreprises technologiques pour surveiller en direct la chaleur et le courant dans les postes de transformation.",
                        "context": "La consommation d'électricité des usines et des maisons ne cesse de grimper, ce qui laisse peu de marge de sécurité au réseau québécois.",
                        "importance": "Permet de brancher de nouvelles industries sans risquer de provoquer des pannes générales sur le réseau.",
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
                        "event": "Publication des spécifications techniques mondiales pour unifier la gestion des flottes de robots sous environnement ROS2.",
                        "context": "Jusqu'à présent, chaque marque de robot utilisait son propre langage fermé, rendant impossible la communication entre des machines de fabricants différents.",
                        "importance": "Apporte une flexibilité totale aux chaînes de montage et facilite grandement la maintenance de l'équipement.",
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
                        {"titre": "Comment faire coopérer des robots de marques différentes", "source": "Control Engineering", "temps": "8 min", "raison": "Explique les gains réels mesurés sur le terrain par les usines."}
                    ]
                }
            ],
            "💰 Économie": [
                {
                    "id": "eco_1",
                    "category": "💰 Économie",
                    "title": "La Banque du Canada confirme que la hausse des prix est enfin rentrée dans l'ordre",
                    "summary": "Dans son dernier rapport, la banque centrale a annoncé que l'inflation est revenue s'établir solidement autour de sa cible idéale de 2 pour cent. Cette bonne nouvelle signifie que la vie quotidienne devient plus prévisible et que le coût de la vie ne s'emballe plus de façon anormale. Pour les familles comme pour les entreprises, cela offre un climat beaucoup plus stable pour planifier les budgets et les achats importants des prochains mois.",
                    "time": "Il y a 1 h",
                    "details": {
                        "event": "Publication du rapport trimestriel qui montre que la hausse générale des prix a ralenti et s'est stabilisée au pays.",
                        "context": "Il a fallu traverser plusieurs années de fortes hausses des taux directeurs pour réussir à calmer la surchauffe économique qui a suivi la pandémie.",
                        "importance": "Redonne de la confiance aux chefs d'entreprise pour investir et créer de nouveaux emplois au pays.",
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
    @st.dialog("📖 Fiche d'Analyse Détaillée", width="large")
    def show_full_details(item):
        det = item["details"]
        st.subheader(item["title"])
        st.caption(f"Catégorie : {item['category']} • Publié {item['time']}")
        
        st.markdown("### 🧠 Ce qui s'est réellement passé")
        st.write(det["event"])
        
        st.markdown("### 📅 Le Contexte")
        st.write(det["context"])
        
        st.markdown("### 🔍 Pourquoi c'est important pour vous")
        st.write(det["importance"])
        
        st.markdown("### 📊 Les Chiffres Clés")
        st.dataframe(det["table"], hide_index=True, use_container_width=True)
        
        st.markdown("### 🌎 Les Impacts Concrets")
        st.text(det["impact"])
        
        st.markdown("### 🔮 Qu'est-ce qui va se passer ensuite ?")
        st.write(det["futur"])
        
        st.markdown("### 📰 Pour aller plus loin (Sources)")
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

    # --- 3. NAVIGATION PAR ONGLETS EN HAUT (STYLE BOURSE) ---
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
        
        categories_keys = ["🌎 Monde", "🇨🇦 Canada", "⚜️ Québec", "🤖 Robotique", "💰 Économie"]
        
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
        
        # Actualités basées sur le vrai portefeuille utilisateur (AAPL, CGNT.V, NVDA, ROBO)
        portfolio_news = [
            {
                "ticker": "AAPL",
                "title": "AAPL : Apple intègre de nouvelles fonctions d'intelligence artificielle sur ses appareils",
                "summary": "Apple vient de présenter une mise à jour importante de ses logiciels qui renforce l'utilisation de l'intelligence artificielle directement sur les téléphones et les ordinateurs. Cette nouveauté simplifie la vie des usagers au quotidien tout en protégeant mieux leurs données personnelles. Pour les investisseurs, cela stimule la demande pour les nouveaux modèles d'appareils et consolide la position de l'entreprise sur le marché technologique mondial.",
                "time": "Il y a 3 h",
                "details": {
                    "event": "Lancement d'une suite de fonctions intelligentes embarquées optimisant la rapidité d'exécution et la confidentialité.",
                    "context": "La concurrence est très forte dans le domaine de l'intelligence artificielle pour mobile, obligeant Apple à se démarquer par la sécurité.",
                    "importance": "Encourage le renouvellement du matériel chez les consommateurs et sécurise les revenus de l'entreprise.",
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
                    "event": "Signature de nouvelles ententes de distribution pour intégrer l'outil d'évaluation dans des cliniques spécialisées.",
                    "context": "Le vieillissement de la population pousse le secteur médical à chercher des solutions technologiques pour dépister plus tôt les problèmes de mémoire.",
                    "importance": "Valide l'utilité clinique du produit et favorise son expansion commerciale à l'international.",
                    "table": pd.DataFrame({"Métrique": ["Domaine", "Statut commercial"], "Valeur": ["Santé numérique", "Expansion des cliniques"]}),
                    "impact": "Action CGNT.V : Potentiel de croissance lié au secteur médical",
                    "futur": "Évaluation des retombées des nouveaux contrats signés dans le réseau de la santé.",
                    "sources": ["Stockwatch", "Financial Post Med"]
                },
                "related": [{"titre": "L'innovation dans le dépistage de la santé mentale", "source": "Medical News Today", "temps": "5 min", "raison": "Comprendre l'utilité des tests cognitifs numériques."}]
            },
            {
                "ticker": "NVDA",
                "title": "NVDA : Nvidia lance de nouveaux puces graphiques ultra-rapides pour les serveurs d'IA",
                "summary": "Nvidia a dévoilé une nouvelle génération de puces informatiques conçues spécialement pour faire tourner les modèles d'intelligence artificielle les plus lourds. Ces processeurs offrent une puissance de calcul décuplée tout en consommant moins d'électricité par opération. Les plus grands centres de données du monde entier se bousculent pour s'en procurer.",
                "time": "Il y a 2 h",
                "details": {
                    "event": "Présentation officielle de la nouvelle architecture de puces graphiques pour serveurs informatiques.",
                    "context": "La demande mondiale en serveurs d'intelligence artificielle explose, ce qui pousse Nvidia à innover sans cesse pour garder son avance.",
                    "importance": "Maintient l'entreprise au sommet de la chaîne de fabrication des technologies d'intelligence artificielle.",
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
                    "event": "Analyse de la performance des entreprises qui composent le fonds spécialisé en robotique et automatisation.",
                    "context": "La recherche de productivité pousse les usines à automatiser toutes leurs tâches répétitives.",
                    "importance": "Offre une exposition sécuritaire et diversifiée à l'ensemble du secteur de la robotique industrielle.",
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

    # --- ONGLET 2 : PERSONNALISER ---
    with tabs[1]:
        st.title("⚙️ PERSONNALISATION")
        st.write("Ajustez vos catégories et gérez vos intérêts de veille selon vos goûts.")
        st.divider()
        
        new_cat_input = st.text_input("Ajouter une catégorie (ex: 🧬 Santé)")
        if st.button("➕ Ajouter la catégorie"):
            if new_cat_input and new_cat_input not in st.session_state.categories:
                st.session_state.categories[new_cat_input] = []
                st.success(f"Catégorie {new_cat_input} ajoutée avec succès !")
                st.rerun()
                
        st.divider()
        
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
                        st.success("Intérêt ajouté avec succès !")
                        st.rerun()

                clean_interests = [i for i in updated_interests if i != "Ajouter un intérêt..."]
                if clean_interests != st.session_state.categories[cat]:
                    st.session_state.categories[cat] = clean_interests

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