import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import html
import re

from urllib.parse import quote_plus
from datetime import datetime, timezone

from database import (
    load_stock_transactions,
    load_system3_preferences,
    save_system3_preferences
)


# ============================================================
# CONFIGURATION
# ============================================================

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?"
    "q={query}&hl=fr-CA&gl=CA&ceid=CA:fr"
)


# ============================================================
# NOM DES COMPAGNIES
# ============================================================
# Le ticker sert à identifier le titre dans le portefeuille.
# La recherche de nouvelles utilise le nom de la compagnie.
#
# Tu peux ajouter d'autres compagnies ici si nécessaire.
# ============================================================

COMPANY_NAMES = {

    # --------------------------------------------------------
    # Technologie / États-Unis
    # --------------------------------------------------------

    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "GOOG": "Alphabet",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    "AMD": "AMD",
    "INTC": "Intel",
    "AVGO": "Broadcom",
    "ORCL": "Oracle",
    "CRM": "Salesforce",
    "ADBE": "Adobe",
    "QCOM": "Qualcomm",
    "CSCO": "Cisco",
    "IBM": "IBM",

    # --------------------------------------------------------
    # Canada
    # --------------------------------------------------------

    "SHOP": "Shopify",
    "SHOP.TO": "Shopify",

    "RY": "Royal Bank of Canada",
    "RY.TO": "Royal Bank of Canada",

    "TD": "TD Bank",
    "TD.TO": "TD Bank",

    "BNS": "Bank of Nova Scotia",
    "BNS.TO": "Bank of Nova Scotia",

    "BMO": "Bank of Montreal",
    "BMO.TO": "Bank of Montreal",

    "CM": "Canadian Imperial Bank of Commerce",
    "CM.TO": "Canadian Imperial Bank of Commerce",

    "ENB": "Enbridge",
    "ENB.TO": "Enbridge",

    "CNQ": "Canadian Natural Resources",
    "CNQ.TO": "Canadian Natural Resources",

    "CNR": "Canadian National Railway",
    "CNR.TO": "Canadian National Railway",

    "CP": "Canadian Pacific Kansas City",
    "CP.TO": "Canadian Pacific Kansas City",

    "ATD": "Alimentation Couche-Tard",
    "ATD.TO": "Alimentation Couche-Tard",

    "DOL": "Dollarama",
    "DOL.TO": "Dollarama",

    "CCO": "Cameco",
    "CCO.TO": "Cameco",

    "AEM": "Agnico Eagle Mines",
    "AEM.TO": "Agnico Eagle Mines",

    "BN": "Brookfield Corporation",
    "BN.TO": "Brookfield Corporation",

    "BAM": "Brookfield Asset Management",
    "BAM.TO": "Brookfield Asset Management",

    "TOI": "Topicus.com",
    "TOI.TO": "Topicus.com",

    # --------------------------------------------------------
    # Crypto / entreprises liées
    # --------------------------------------------------------

    "COIN": "Coinbase",
    "MSTR": "Strategy",
    "MSTR.TO": "Strategy",

}


# ============================================================
# OUTILS GÉNÉRAUX
# ============================================================

def clean_text(text):
    """Nettoie le texte provenant du flux RSS."""

    if not text:
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_relative_time(date_string):
    """Convertit une date RSS en temps relatif."""

    if not date_string:
        return ""

    try:

        dt = datetime.strptime(
            date_string,
            "%a, %d %b %Y %H:%M:%S %Z"
        ).replace(
            tzinfo=timezone.utc
        )

        now = datetime.now(
            timezone.utc
        )

        seconds = int(
            (now - dt).total_seconds()
        )

        if seconds < 60:
            return "Il y a moins d'une minute"

        minutes = seconds // 60

        if minutes < 60:
            return f"Il y a {minutes} min"

        hours = minutes // 60

        if hours < 24:
            return f"Il y a {hours} h"

        days = hours // 24

        if days == 1:
            return "Hier"

        return f"Il y a {days} jours"

    except Exception:

        return date_string


# ============================================================
# VRAIES NOUVELLES
# ============================================================

def fetch_google_news(
    query,
    max_results=10
):
    """
    Recherche de vraies nouvelles avec Google News RSS.

    Les titres, sources, dates et liens viennent directement
    du flux RSS.
    """

    try:

        if not query:
            return []

        url = GOOGLE_NEWS_RSS.format(
            query=quote_plus(
                str(query)
            )
        )

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        articles = []

        for item in root.findall(
            ".//item"
        ):

            title_node = item.find(
                "title"
            )

            link_node = item.find(
                "link"
            )

            description_node = item.find(
                "description"
            )

            pub_date_node = item.find(
                "pubDate"
            )

            source_node = item.find(
                "source"
            )

            title = clean_text(
                title_node.text
                if title_node is not None
                else ""
            )

            link = (
                link_node.text.strip()
                if link_node is not None
                and link_node.text
                else ""
            )

            description = clean_text(
                description_node.text
                if description_node is not None
                else ""
            )

            date = (
                pub_date_node.text
                if pub_date_node is not None
                else ""
            )

            source = clean_text(
                source_node.text
                if source_node is not None
                else "Source inconnue"
            )

            if not title or not link:
                continue

            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "source": source,
                "date": date,
                "time": get_relative_time(date)
            })

            if len(articles) >= max_results:
                break

        return articles

    except Exception:

        return []


def remove_duplicates(articles):
    """Supprime les articles avec le même titre."""

    seen = set()

    result = []

    for article in articles:

        key = re.sub(
            r"[^a-z0-9]",
            "",
            article.get(
                "title",
                ""
            ).lower()
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)

        result.append(
            article
        )

    return result


# ============================================================
# NOM DE COMPAGNIE À PARTIR DU TICKER
# ============================================================

def get_company_name(ticker):
    """
    Transforme un ticker en nom de compagnie.

    Exemple :
        SHOP.TO -> Shopify
        NVDA    -> NVIDIA
    """

    ticker = str(
        ticker
    ).strip().upper()

    # Recherche exacte
    if ticker in COMPANY_NAMES:

        return COMPANY_NAMES[
            ticker
        ]

    # On essaie aussi sans suffixe boursier
    base_ticker = ticker

    for suffix in [
        ".TO",
        ".V",
        ".NE",
        ".CN",
        ".CA",
        "-C",
        "-U"
    ]:

        if base_ticker.endswith(
            suffix
        ):

            base_ticker = (
                base_ticker[
                    :-len(suffix)
                ]
            )

            break

    if base_ticker in COMPANY_NAMES:

        return COMPANY_NAMES[
            base_ticker
        ]

    # Si on ne connaît pas le ticker,
    # on retourne le ticker plutôt que de casser le système.
    return ticker


# ============================================================
# PORTEFEUILLE RÉEL DE SYSTÈME 2
# ============================================================

def get_portfolio_holdings():
    """
    Récupère les titres réellement détenus dans Système 2.

    Les données viennent de StockTransactions.
    """

    try:

        username = st.session_state.get(
            "username"
        )

        if not username:
            return {}

        df = load_stock_transactions()

        if df is None or df.empty:
            return {}

        # Vérification des colonnes
        required_columns = [
            "owner",
            "ticker",
            "quantity"
        ]

        for column in required_columns:

            if column not in df.columns:
                return {}

        # Seulement les transactions de l'utilisateur
        df = df[
            df["owner"].astype(str)
            == str(username)
        ]

        holdings = {}

        for _, row in df.iterrows():

            ticker = str(
                row.get(
                    "ticker",
                    ""
                )
            ).strip().upper()

            if not ticker:
                continue

            try:

                quantity = float(
                    row.get(
                        "quantity",
                        0
                    )
                )

            except Exception:

                continue

            trans_type = str(
                row.get(
                    "trans_type",
                    "Achat"
                )
            ).strip().lower()

            if trans_type == "achat":

                holdings[ticker] = (
                    holdings.get(
                        ticker,
                        0
                    )
                    + quantity
                )

            elif trans_type == "vente":

                holdings[ticker] = (
                    holdings.get(
                        ticker,
                        0
                    )
                    - quantity
                )

        # Seulement les titres encore détenus
        holdings = {
            ticker: quantity
            for ticker, quantity
            in holdings.items()
            if quantity > 0
        }

        return holdings

    except Exception:

        return {}


# ============================================================
# NOUVELLES DU PORTEFEUILLE
# ============================================================

def get_portfolio_news(
    holdings,
    max_articles_per_ticker=5
):
    """
    Recherche les vraies nouvelles des compagnies
    du portefeuille.

    IMPORTANT :
    On ne recherche PAS le ticker.

    Exemple :
        SHOP.TO -> Shopify
        NVDA -> NVIDIA
    """

    all_articles = []

    for ticker in holdings.keys():

        company_name = get_company_name(
            ticker
        )

        # ----------------------------------------------------
        # RECHERCHE PAR NOM DE COMPAGNIE
        # ----------------------------------------------------

        articles = fetch_google_news(
            company_name,
            max_results=max_articles_per_ticker
        )

        for article in articles:

            article[
                "ticker"
            ] = ticker

            article[
                "company"
            ] = company_name

        all_articles.extend(
            articles
        )

    return remove_duplicates(
        all_articles
    )


# ============================================================
# NOUVELLES SELON LES CATÉGORIES ET INTÉRÊTS
# ============================================================

def search_news_for_categories(
    categories,
    max_per_search=5
):
    """
    Nouvelle logique :

    CATÉGORIE SEULE
    ----------------
    Monde
        []

    Recherche :
        Monde actualités dernières nouvelles

    CATÉGORIE + INTÉRÊTS
    --------------------
    Géopolitique
        Chine
        Taïwan

    Recherche :
        Géopolitique Chine
        Géopolitique Taïwan

    Ainsi, les intérêts sont optionnels.
    """

    all_articles = []

    for category, interests in categories.items():

        category = str(
            category
        ).strip()

        if not category:
            continue

        # ----------------------------------------------------
        # Nettoyage des intérêts
        # ----------------------------------------------------

        valid_interests = []

        if interests:

            for interest in interests:

                interest = str(
                    interest
                ).strip()

                if interest:

                    valid_interests.append(
                        interest
                    )

        # ----------------------------------------------------
        # CATÉGORIE SANS INTÉRÊT
        # ----------------------------------------------------

        if not valid_interests:

            query = (
                f"{category} "
                f"actualités dernières nouvelles"
            )

            articles = fetch_google_news(
                query,
                max_results=max_per_search
            )

            for article in articles:

                article[
                    "category"
                ] = category

                article[
                    "matched_interest"
                ] = category

            all_articles.extend(
                articles
            )

        # ----------------------------------------------------
        # CATÉGORIE AVEC INTÉRÊTS
        # ----------------------------------------------------

        else:

            for interest in valid_interests:

                query = (
                    f"{category} "
                    f"{interest}"
                )

                articles = fetch_google_news(
                    query,
                    max_results=max_per_search
                )

                for article in articles:

                    article[
                        "category"
                    ] = category

                    article[
                        "matched_interest"
                    ] = interest

                all_articles.extend(
                    articles
                )

    return remove_duplicates(
        all_articles
    )


# ============================================================
# ANCIENNE FONCTION CONSERVÉE
# ============================================================

def search_news_for_interests(
    interests,
    max_per_interest=5
):
    """
    Conservée pour compatibilité.

    Le système principal utilise maintenant
    search_news_for_categories().
    """

    all_articles = []

    for interest in interests:

        interest = str(
            interest
        ).strip()

        if not interest:
            continue

        articles = fetch_google_news(
            interest,
            max_results=max_per_interest
        )

        for article in articles:

            article[
                "matched_interest"
            ] = interest

        all_articles.extend(
            articles
        )

    return remove_duplicates(
        all_articles
    )


# ============================================================
# GEMINI
# ============================================================

def get_gemini_client():

    try:

        if "client" in globals():

            return globals()["client"]

        from google import genai

        if "GEMINI_API_KEY" not in st.secrets:

            return None

        return genai.Client(
            api_key=st.secrets[
                "GEMINI_API_KEY"
            ]
        )

    except Exception as e:

        st.session_state["system3_gemini_error"] = str(e)
        return None


# ============================================================
# RÉSUMÉ IA
# ============================================================

def get_ai_summary(
    article,
    context=""
):
    """
    Résume une vraie nouvelle.

    L'IA ne crée pas la nouvelle.
    """

    client = get_gemini_client()

    if client is None:

        return article.get(
            "description",
            ""
        )

    prompt = f"""
Tu dois résumer une vraie nouvelle provenant
d'un flux d'actualité.

IMPORTANT :
- Ne crée aucun fait.
- N'invente aucune information.
- Utilise uniquement les informations fournies.
- Si une information n'est pas disponible,
  ne l'invente pas.
- Réponds en français.

Titre :
{article.get("title", "")}

Source :
{article.get("source", "")}

Résumé fourni :
{article.get("description", "")}

Contexte :
{context}

Fais un résumé clair en 3 à 5 phrases.

Explique ensuite brièvement pourquoi cette nouvelle
peut être importante.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:

            return response.text.strip()

    except Exception as e:

        st.session_state["system3_gemini_error"] = str(e)

    return article.get(
        "description",
        ""
    )


# ============================================================
# ANALYSE DÉTAILLÉE
# ============================================================

def get_ai_detailed_analysis(
    article,
    context=""
):
    """Produit une analyse détaillée."""

    client = get_gemini_client()

    if client is None:
        return None

    prompt = f"""
Analyse cette vraie nouvelle.

IMPORTANT :
- Ne crée aucun fait.
- Ne crée aucune statistique.
- Ne présente pas une hypothèse comme un fait.
- Utilise seulement les informations fournies.
- Réponds en français.

TITRE :
{article.get("title", "")}

SOURCE :
{article.get("source", "")}

DATE :
{article.get("date", "")}

RÉSUMÉ :
{article.get("description", "")}

CONTEXTE UTILISATEUR :
{context}

Structure :

### 1. Ce qui s'est passé
Résume les faits.

### 2. Pourquoi c'est important
Explique les conséquences possibles.

### 3. Qui est concerné
Entreprises, secteurs, pays ou personnes.

### 4. Impact possible
Explique les impacts possibles.
Ne présente aucune prédiction comme une certitude.

### 5. À retenir
Donne les points essentiels.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:

            return response.text.strip()

    except Exception as e:

        st.session_state["system3_gemini_error"] = str(e)

    return None


# ============================================================
# ARTICLES RELIÉS
# ============================================================

def get_related_articles(
    article
):

    title = article.get(
        "title",
        ""
    )

    if not title:
        return []

    related = fetch_google_news(
        title,
        max_results=10
    )

    result = []

    original_title = title.lower()

    for item in related:

        if (
            item["title"].lower()
            == original_title
        ):
            continue

        result.append(
            item
        )

        if len(result) >= 5:
            break

    return result


# ============================================================
# FENÊTRE : PLUS DE DÉTAILS
# ============================================================

def show_full_details(
    article,
    context=""
):
    """Affiche les détails directement dans la page.

    On n'utilise volontairement pas st.dialog ici : le bouton
    « Plus de détails » doit fonctionner sur toutes les versions
    de Streamlit et afficher immédiatement le contenu.
    """

    st.divider()
    st.header("📖 Plus de détails")

    st.subheader(
        article.get("title", "Nouvelle")
    )

    st.caption(
        f"📰 {article.get('source', 'Source inconnue')} "
        f"• 🕐 {article.get('time', '')}"
    )

    if article.get("company"):
        st.info(
            f"📈 Compagnie : **{article['company']}** "
            f"({article.get('ticker', '')})"
        )

    elif article.get("ticker"):
        st.info(
            f"📈 Cette nouvelle concerne **{article['ticker']}**, "
            "un titre de ton portefeuille."
        )

    if article.get("category"):
        st.info(
            f"📁 Catégorie : **{article['category']}**"
        )

    if article.get("matched_interest"):
        st.info(
            f"🎯 Sujet : **{article['matched_interest']}**"
        )

    st.markdown("### 📝 Résumé")

    with st.spinner("Résumé de la nouvelle avec Gemini 3.6 Flash..."):
        summary = get_ai_summary(article, context)

    if summary:
        st.write(summary)
    else:
        st.info(
            "Aucun résumé IA disponible. Consulte l'article original."
        )

    st.markdown("### 🔎 Informations de l'article")

    if article.get("description"):
        st.write(article["description"])
    else:
        st.info("Aucun résumé supplémentaire n'est fourni par le flux.")

    st.markdown("### 🤖 Analyse IA détaillée")

    with st.spinner("Analyse de la nouvelle avec Gemini 3.6 Flash..."):
        analysis = get_ai_detailed_analysis(article, context)

    if analysis:
        st.markdown(analysis)
    else:
        st.error("Analyse IA non disponible.")
        error = st.session_state.get("system3_gemini_error")
        if error:
            with st.expander("Voir l'erreur technique"):
                st.code(error)

    st.divider()

    if article.get("link"):
        st.link_button(
            "📰 Lire l'article original",
            article["link"],
            use_container_width=True
        )


# ============================================================
# FENÊTRE : ARTICLES RELIÉS
# ============================================================

def show_related_articles(
    article
):

    @st.dialog(
        "📰 Articles reliés",
        width="large"
    )
    def dialog():

        st.subheader(
            "Articles reliés"
        )

        st.caption(
            "Recherche en temps réel de vrais articles "
            "sur le même sujet."
        )

        with st.spinner(
            "Recherche..."
        ):

            related = (
                get_related_articles(
                    article
                )
            )

        if not related:

            st.warning(
                "Aucun article relié trouvé."
            )

            return

        for i, item in enumerate(
            related,
            start=1
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {i}. {item['title']}"
                )

                st.caption(
                    f"📰 {item['source']} "
                    f"• 🕐 {item['time']}"
                )

                if item.get(
                    "description"
                ):

                    st.write(
                        item["description"]
                    )

                st.link_button(
                    "Lire l'article ↗",
                    item["link"],
                    use_container_width=True
                )

    dialog()


# ============================================================
# SAUVEGARDE DES INTÉRÊTS
# ============================================================

def normalize_categories(categories):
    """Normalise les catégories en conservant les catégories vides."""

    if not isinstance(categories, dict):
        return {}

    normalized = {}

    for category, interests in categories.items():
        category = str(category).strip()

        if not category:
            continue

        if interests is None:
            interests = []
        elif isinstance(interests, str):
            interests = [interests]
        elif not isinstance(interests, (list, tuple, set)):
            interests = []

        clean_interests = []

        for interest in interests:
            interest = str(interest).strip()
            if interest and interest not in clean_interests:
                clean_interests.append(interest)

        normalized[category] = clean_interests

    return normalized


def save_current_preferences(categories=None):
    """Sauvegarde immédiatement les préférences dans database.py."""

    username = st.session_state.get("username")

    if not username:
        return False, "Utilisateur non connecté."

    if categories is None:
        categories = st.session_state.get(
            "system3_categories",
            {}
        )

    categories = normalize_categories(categories)
    st.session_state["system3_categories"] = categories

    try:
        result = save_system3_preferences(
            username,
            categories
        )

        if isinstance(result, tuple):
            if len(result) >= 2:
                return bool(result[0]), result[1]
            if len(result) == 1:
                return bool(result[0]), None

        if result is False:
            return False, "La sauvegarde a été refusée par database.py."

        return True, None

    except Exception as e:
        return False, str(e)


# ============================================================
# PAGE PRINCIPALE
# ============================================================

def show_system3():

    username = st.session_state.get(
        "username"
    )

    if not username:

        st.error(
            "Tu dois être connecté pour utiliser Système 3."
        )

        return

    # ========================================================
    # CHARGER LES INTÉRÊTS
    # ========================================================

    if (
        "system3_categories"
        not in st.session_state
    ):

        st.session_state[
            "system3_categories"
        ] = normalize_categories(
            load_system3_preferences(username)
        )

    categories = (
        st.session_state[
            "system3_categories"
        ]
    )

    # ========================================================
    # TABS
    # ========================================================

    tab_home, tab_settings, tab_portfolio = st.tabs([
        "🏠 Accueil",
        "⚙️ Mes intérêts",
        "📈 Mon portefeuille"
    ])


    # ========================================================
    # ACCUEIL
    # ========================================================

    with tab_home:

        st.title(
            "📰 MON BRIEFING"
        )

        st.caption(
            "Actualités personnalisées selon tes intérêts."
        )

        # ----------------------------------------------------
        # ACTUALISER
        # ----------------------------------------------------

        if st.button(
            "🔄 Actualiser les nouvelles",
            type="primary",
            use_container_width=True
        ):

            st.session_state.pop(
                "system3_interest_news",
                None
            )

            # IMPORTANT :
            # On ne touche plus aux nouvelles
            # du portefeuille ici.
            #
            # Elles sont indépendantes de l'accueil.

            st.rerun()

        st.divider()

        # ----------------------------------------------------
        # ACTUALITÉS DES CATÉGORIES
        # ----------------------------------------------------

        st.header(
            "🔥 Actualités selon mes intérêts"
        )

        if not categories:

            st.info(
                "Tu n'as actuellement aucune catégorie. "
                "Va dans « Mes intérêts » pour en ajouter."
            )

        else:

            if (
                "system3_interest_news"
                not in st.session_state
            ):

                with st.spinner(
                    "Recherche des vraies nouvelles..."
                ):

                    # ==================================================
                    # CHANGEMENT IMPORTANT
                    #
                    # On envoie maintenant les catégories COMPLÈTES.
                    #
                    # Avant :
                    #     [Chine, IA, etc.]
                    #
                    # Maintenant :
                    #     {
                    #         "Monde": [],
                    #         "Géopolitique": ["Chine"],
                    #         ...
                    #     }
                    #
                    # Ainsi une catégorie sans intérêt fonctionne.
                    # ==================================================

                    st.session_state[
                        "system3_interest_news"
                    ] = search_news_for_categories(
                        categories,
                        max_per_search=4
                    )

            interest_news = (
                st.session_state[
                    "system3_interest_news"
                ]
            )

            if not interest_news:

                st.warning(
                    "Aucune nouvelle trouvée."
                )

            else:

                for index, article in enumerate(
                    interest_news[:20]
                ):

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### {article['title']}"
                        )

                        category = article.get(
                            "category",
                            ""
                        )

                        subject = article.get(
                            "matched_interest",
                            ""
                        )

                        if (
                            subject
                            and subject != category
                        ):

                            caption = (
                                f"📰 {article['source']} "
                                f"• 🕐 {article['time']} "
                                f"• 📁 {category} "
                                f"• 🎯 {subject}"
                            )

                        else:

                            caption = (
                                f"📰 {article['source']} "
                                f"• 🕐 {article['time']} "
                                f"• 📁 {category}"
                            )

                        st.caption(
                            caption
                        )

                        if article.get(
                            "description"
                        ):

                            st.write(
                                article["description"]
                            )

                        col1, col2, col3 = st.columns(
                            [1, 1, 1]
                        )

                        with col1:

                            if st.button(
                                "📖 Plus de détails",
                                key=f"interest_detail_{index}",
                                use_container_width=True
                            ):

                                show_full_details(
                                    article,
                                    article.get(
                                        "matched_interest",
                                        ""
                                    )
                                )

                        with col2:

                            if st.button(
                                "📰 Articles reliés",
                                key=f"interest_related_{index}",
                                use_container_width=True
                            ):

                                show_related_articles(
                                    article
                                )

                        with col3:

                            st.link_button(
                                "↗ Article original",
                                article["link"],
                                use_container_width=True
                            )


    # ========================================================
    # MES INTÉRÊTS
    # ========================================================

    with tab_settings:

        st.title(
            "⚙️ MES INTÉRÊTS"
        )

        st.write(
            "Les modifications sont sauvegardées "
            "dans ton compte et resteront après "
            "une déconnexion ou un redémarrage."
        )

        st.info(
            "💡 Une catégorie peut fonctionner sans intérêt.\n\n"
            "Exemple : **Monde** sans intérêt = grandes "
            "nouvelles mondiales.\n\n"
            "Exemple : **Géopolitique → Chine** = nouvelles "
            "géopolitiques centrées sur la Chine."
        )

        st.divider()

        # ----------------------------------------------------
        # AJOUTER UNE CATÉGORIE
        # ----------------------------------------------------

        st.subheader(
            "➕ Ajouter une catégorie"
        )

        new_category = st.text_input(
            "Nom de la catégorie",
            placeholder="Exemple : 🌎 Monde",
            key="system3_new_category"
        )

        if st.button(
            "Ajouter la catégorie",
            key="system3_add_category",
            use_container_width=True
        ):

            new_category = (
                new_category.strip()
            )

            if not new_category:

                st.warning(
                    "Entre un nom de catégorie."
                )

            elif new_category in categories:

                st.warning(
                    "Cette catégorie existe déjà."
                )

            else:

                # IMPORTANT :
                # Une catégorie vide est VALIDE.
                categories[
                    new_category
                ] = []

                success, error = (
                    save_current_preferences()
                )

                if success:

                    st.session_state.pop(
                        "system3_interest_news",
                        None
                    )

                    st.success(
                        "✅ Catégorie sauvegardée définitivement."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Erreur : {error}"
                    )

        st.divider()

        # ----------------------------------------------------
        # CATÉGORIES EXISTANTES
        # ----------------------------------------------------

        for category in list(
            categories.keys()
        ):

            interests = categories[
                category
            ]

            with st.expander(
                f"📁 {category}",
                expanded=True
            ):

                if interests:

                    st.write(
                        f"{len(interests)} intérêt(s)"
                    )

                else:

                    st.write(
                        "Aucun intérêt précis — "
                        "la catégorie sera utilisée directement."
                    )

                # --------------------------------------------
                # INTÉRÊTS EXISTANTS
                # --------------------------------------------

                selected_interests = st.multiselect(
                    "Intérêts",
                    options=interests,
                    default=interests,
                    key=f"select_{category}"
                )

                # --------------------------------------------
                # NOUVEL INTÉRÊT
                # --------------------------------------------

                new_interest = st.text_input(
                    "Ajouter un intérêt",
                    placeholder="Exemple : Chine",
                    key=f"new_{category}"
                )

                col1, col2 = st.columns(2)

                # --------------------------------------------
                # ENREGISTRER
                # --------------------------------------------

                with col1:

                    if st.button(
                        "💾 Enregistrer",
                        key=f"save_{category}",
                        use_container_width=True
                    ):

                        updated_interests = list(
                            selected_interests
                        )

                        if new_interest.strip():

                            if (
                                new_interest.strip()
                                not in updated_interests
                            ):

                                updated_interests.append(
                                    new_interest.strip()
                                )

                        categories[
                            category
                        ] = updated_interests

                        # Les nouvelles deviennent obsolètes
                        st.session_state.pop(
                            "system3_interest_news",
                            None
                        )

                        success, error = (
                            save_current_preferences()
                        )

                        if success:

                            st.success(
                                "✅ Intérêts sauvegardés définitivement."
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Erreur de sauvegarde : {error}"
                            )

                # --------------------------------------------
                # SUPPRIMER
                # --------------------------------------------

                with col2:

                    if st.button(
                        "🗑️ Supprimer la catégorie",
                        key=f"delete_{category}",
                        use_container_width=True
                    ):

                        del categories[
                            category
                        ]

                        st.session_state.pop(
                            "system3_interest_news",
                            None
                        )

                        success, error = (
                            save_current_preferences()
                        )

                        if success:

                            st.success(
                                "Catégorie supprimée définitivement."
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Erreur : {error}"
                            )

        st.divider()

        # ----------------------------------------------------
        # RÉSUMÉ
        # ----------------------------------------------------

        st.subheader(
            "🎯 Résumé de mes intérêts"
        )

        total = 0

        for category, interests in categories.items():

            if interests:

                total += len(
                    interests
                )

                st.markdown(
                    f"**{category}** : "
                    + " • ".join(
                        interests
                    )
                )

            else:

                st.markdown(
                    f"**{category}** : "
                    "toutes les grandes nouvelles"
                )

        st.caption(
            f"{total} intérêt(s) suivi(s)"
        )


    # ========================================================
    # PORTEFEUILLE
    #
    # IMPORTANT :
    #
    # AUCUNE recherche du portefeuille n'est faite dans
    # l'accueil.
    #
    # Les recherches sont faites uniquement lorsque
    # l'utilisateur appuie sur le bouton d'une compagnie.
    # ========================================================

    with tab_portfolio:

        st.title(
            "📈 MON PORTEFEUILLE"
        )

        st.write(
            "Les titres affichés ici proviennent "
            "directement des transactions enregistrées "
            "dans Système 2."
        )

        st.divider()

        holdings = (
            get_portfolio_holdings()
        )

        if not holdings:

            st.info(
                "Aucun titre actuellement détenu."
            )

        else:

            for ticker, quantity in holdings.items():

                company_name = get_company_name(
                    ticker
                )

                with st.container(
                    border=True
                ):

                    st.subheader(
                        company_name
                    )

                    st.caption(
                        f"Ticker : {ticker}"
                    )

                    st.write(
                        f"Actions détenues : "
                        f"**{quantity:g}**"
                    )

                    # ==================================================
                    # LA RECHERCHE SE FAIT SEULEMENT ICI
                    # ==================================================

                    if st.button(
                        f"📰 Nouvelles de {company_name}",
                        key=f"ticker_news_{ticker}",
                        use_container_width=True
                    ):

                        with st.spinner(
                            f"Recherche des nouvelles de "
                            f"{company_name}..."
                        ):

                            company_news = (
                                fetch_google_news(
                                    company_name,
                                    max_results=10
                                )
                            )

                        if not company_news:

                            st.warning(
                                "Aucune nouvelle trouvée."
                            )

                        else:

                            for i, article in enumerate(
                                company_news
                            ):

                                # Informations supplémentaires
                                article[
                                    "ticker"
                                ] = ticker

                                article[
                                    "company"
                                ] = company_name

                                st.markdown(
                                    f"### {article['title']}"
                                )

                                st.caption(
                                    f"📰 {article['source']} "
                                    f"• 🕐 {article['time']}"
                                )

                                if article.get(
                                    "description"
                                ):

                                    st.write(
                                        article["description"]
                                    )

                                col1, col2, col3 = st.columns(
                                    [1, 1, 1]
                                )

                                with col1:

                                    if st.button(
                                        "📖 Plus de détails",
                                        key=f"portfolio_detail_{ticker}_{i}",
                                        use_container_width=True
                                    ):

                                        show_full_details(
                                            article,
                                            f"Compagnie : "
                                            f"{company_name}"
                                        )

                                with col2:

                                    if st.button(
                                        "📰 Articles reliés",
                                        key=f"portfolio_related_{ticker}_{i}",
                                        use_container_width=True
                                    ):

                                        show_related_articles(
                                            article
                                        )

                                with col3:

                                    st.link_button(
                                        "Lire l'article ↗",
                                        article["link"],
                                        use_container_width=True
                                    )

                                st.divider()