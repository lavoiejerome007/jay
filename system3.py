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
# MAPPING TICKER -> NOM DE COMPAGNIE
# ============================================================

# On utilise le nom de la compagnie pour les recherches.
# Les tickers restent utilisés pour identifier les positions
# dans le portefeuille.

COMPANY_NAMES = {

    # États-Unis
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet Google",
    "GOOG": "Alphabet Google",
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

    # Canada
    "SHOP": "Shopify",
    "SHOP.TO": "Shopify",
    "RY": "Royal Bank of Canada",
    "RY.TO": "Royal Bank of Canada",
    "TD": "Toronto-Dominion Bank",
    "TD.TO": "Toronto-Dominion Bank",
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
    "BN": "Brookfield",
    "BN.TO": "Brookfield Corporation",
    "BAM": "Brookfield Asset Management",
    "BAM.TO": "Brookfield Asset Management",
    "TOI": "Topicus.com",
    "TOI.TO": "Topicus.com",

    # Crypto / sociétés liées
    "COIN": "Coinbase",
    "MSTR": "Strategy MicroStrategy",

}


# ============================================================
# OUTILS GÉNÉRAUX
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = html.unescape(str(text))

    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_title(title):

    title = clean_text(
        title
    ).lower()

    title = re.sub(
        r"[^a-z0-9àâçéèêëîïôûùüÿñæœ\s]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# DATE
# ============================================================

def get_relative_time(date_string):

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
            (
                now - dt
            ).total_seconds()
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
# GOOGLE NEWS
# ============================================================

def fetch_google_news(
    query,
    max_results=10
):

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
            timeout=15,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
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

            date_node = item.find(
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
                date_node.text
                if date_node is not None
                else ""
            )

            source = clean_text(
                source_node.text
                if source_node is not None
                else ""
            )

            if not title:
                continue

            if not link:
                continue

            if not source:
                source = "Source inconnue"

            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "source": source,
                "date": date,
                "time": get_relative_time(
                    date
                )
            })

            if len(
                articles
            ) >= max_results:

                break

        return articles

    except Exception:

        return []


# ============================================================
# DUPLICATION
# ============================================================

def remove_duplicates(
    articles
):

    seen = set()

    result = []

    for article in articles:

        title = normalize_title(
            article.get(
                "title",
                ""
            )
        )

        if not title:
            continue

        if title in seen:
            continue

        seen.add(title)

        result.append(
            article
        )

    return result


# ============================================================
# NOM DE COMPAGNIE
# ============================================================

def get_company_name(
    ticker
):

    ticker_clean = str(
        ticker
    ).strip().upper()

    # Mapping connu
    if ticker_clean in COMPANY_NAMES:

        return COMPANY_NAMES[
            ticker_clean
        ]

    # Enlever suffixes courants
    base_ticker = ticker_clean

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

    # Si inconnu, on retourne le ticker.
    # Cela évite de casser le système.
    return ticker_clean


# ============================================================
# PORTEFEUILLE
# ============================================================

def get_portfolio_holdings():

    try:

        username = st.session_state.get(
            "username"
        )

        if not username:
            return {}

        df = load_stock_transactions()

        if df is None or df.empty:
            return {}

        if "owner" not in df.columns:
            return {}

        if "ticker" not in df.columns:
            return {}

        if "quantity" not in df.columns:
            return {}

        if "trans_type" not in df.columns:

            df["trans_type"] = "Achat"

        df = df[
            df["owner"].astype(str).str.strip()
            == str(username).strip()
        ]

        if df.empty:
            return {}

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
# NEWS DU PORTEFEUILLE
# ============================================================

def get_portfolio_news(
    holdings,
    max_articles_per_company=5
):

    all_articles = []

    for ticker in holdings.keys():

        company_name = get_company_name(
            ticker
        )

        articles = fetch_google_news(
            company_name,
            max_results=max_articles_per_company
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
# NEWS SELON LES INTÉRÊTS
# ============================================================

def search_news_for_categories(
    categories,
    max_per_search=5
):

    all_articles = []

    for category, interests in categories.items():

        category = str(
            category
        ).strip()

        # -----------------------------------------------
        # Nettoyage des intérêts
        # -----------------------------------------------

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

        # -----------------------------------------------
        # CAS 1 :
        # catégorie seule
        #
        # Exemple :
        # Monde
        #
        # On cherche les grandes nouvelles
        # de cette catégorie.
        # -----------------------------------------------

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

        # -----------------------------------------------
        # CAS 2 :
        # catégorie + intérêts
        #
        # Exemple :
        # Géopolitique
        # Chine
        # Taïwan
        #
        # On fait une recherche plus ciblée.
        # -----------------------------------------------

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

    except Exception:

        return None


# ============================================================
# RÉSUMÉ IA
# ============================================================

def get_ai_summary(
    article,
    context=""
):

    client = get_gemini_client()

    if client is None:

        return article.get(
            "description",
            ""
        )

    prompt = f"""
Tu dois résumer une vraie nouvelle.

Utilise uniquement les informations fournies.

N'invente :
- aucun fait;
- aucune statistique;
- aucune citation;
- aucune information absente.

Titre :
{article.get("title", "")}

Source :
{article.get("source", "")}

Date :
{article.get("date", "")}

Contenu fourni :
{article.get("description", "")}

Contexte :
{context}

Réponds en français.

Fais un résumé clair de 3 à 5 phrases.

Explique ensuite brièvement pourquoi cette
nouvelle peut être importante.

Si les informations sont insuffisantes,
indique-le clairement.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:

            return response.text.strip()

    except Exception:

        pass

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

    client = get_gemini_client()

    if client is None:
        return None

    prompt = f"""
Analyse cette vraie nouvelle.

Utilise uniquement les informations fournies.

N'invente :
- aucun fait;
- aucune statistique;
- aucune citation;
- aucune information absente.

Titre :
{article.get("title", "")}

Source :
{article.get("source", "")}

Date :
{article.get("date", "")}

Contenu :
{article.get("description", "")}

Contexte :
{context}

Réponds en français.

Structure :

### 1. Ce qui s'est passé

Explique les faits disponibles.

### 2. Pourquoi c'est important

Explique les conséquences possibles.

### 3. Qui est concerné

Entreprises, secteurs, pays ou personnes
si disponibles.

### 4. Impact possible

Explique les impacts possibles.

Sépare clairement les faits des hypothèses.

### 5. À retenir

Donne les trois points essentiels.

Si les informations sont insuffisantes,
dis-le clairement.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:

            return response.text.strip()

    except Exception:

        pass

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

    original_title = normalize_title(
        title
    )

    for item in related:

        item_title = normalize_title(
            item.get(
                "title",
                ""
            )
        )

        if item_title == original_title:
            continue

        result.append(
            item
        )

        if len(result) >= 5:
            break

    return result


# ============================================================
# PLUS DE DÉTAILS
# ============================================================

def show_full_details(
    article,
    context=""
):

    @st.dialog(
        "📖 Plus de détails",
        width="large"
    )
    def dialog():

        st.subheader(
            article.get(
                "title",
                "Nouvelle"
            )
        )

        st.caption(
            f"📰 {article.get('source', '')} "
            f"• 🕐 {article.get('time', '')}"
        )

        if article.get(
            "category"
        ):

            st.info(
                f"🎯 Catégorie : "
                f"**{article['category']}**"
            )

        if article.get(
            "matched_interest"
        ):

            st.info(
                f"🔎 Sujet : "
                f"**{article['matched_interest']}**"
            )

        if article.get(
            "company"
        ):

            st.info(
                f"📈 Compagnie : "
                f"**{article['company']}** "
                f"({article.get('ticker', '')})"
            )

        st.divider()

        st.markdown(
            "### 📝 Résumé"
        )

        with st.spinner(
            "Résumé de la nouvelle..."
        ):

            summary = get_ai_summary(
                article,
                context
            )

        if summary:

            st.write(
                summary
            )

        else:

            st.info(
                "Aucun résumé disponible."
            )

        st.divider()

        st.markdown(
            "### 🔎 Contenu disponible"
        )

        description = article.get(
            "description",
            ""
        )

        if description:

            st.write(
                description
            )

        else:

            st.info(
                "Le flux RSS ne fournit pas "
                "de résumé supplémentaire."
            )

        st.markdown(
            "### 🤖 Analyse"
        )

        with st.spinner(
            "Analyse de la nouvelle..."
        ):

            analysis = (
                get_ai_detailed_analysis(
                    article,
                    context
                )
            )

        if analysis:

            st.markdown(
                analysis
            )

        else:

            st.info(
                "Analyse IA non disponible."
            )

        st.divider()

        st.link_button(
            "📰 Lire l'article original",
            article["link"],
            use_container_width=True
        )

    dialog()


# ============================================================
# ARTICLES RELIÉS
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
            "Recherche d'articles reliés..."
        ):

            related = get_related_articles(
                article
            )

        if not related:

            st.warning(
                "Aucun article relié trouvé."
            )

            return

        for index, item in enumerate(
            related,
            start=1
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {index}. {item['title']}"
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
                    "Lire l'article original ↗",
                    item["link"],
                    use_container_width=True
                )

    dialog()


# ============================================================
# SAUVEGARDE
# ============================================================

def save_current_preferences():

    username = st.session_state.get(
        "username"
    )

    if not username:

        return (
            False,
            "Utilisateur non connecté."
        )

    categories = st.session_state.get(
        "system3_categories",
        {}
    )

    try:

        return save_system3_preferences(
            username,
            categories
        )

    except Exception as e:

        return (
            False,
            str(e)
        )


# ============================================================
# CHARGEMENT DES PRÉFÉRENCES
# ============================================================

def load_current_preferences():

    username = st.session_state.get(
        "username"
    )

    if not username:
        return {}

    loaded_for = st.session_state.get(
        "system3_preferences_user"
    )

    if (
        "system3_categories"
        not in st.session_state
        or loaded_for != username
    ):

        categories = (
            load_system3_preferences(
                username
            )
        )

        if categories is None:

            categories = {}

        st.session_state[
            "system3_categories"
        ] = categories

        st.session_state[
            "system3_preferences_user"
        ] = username

        st.session_state.pop(
            "system3_interest_news",
            None
        )

        st.session_state.pop(
            "system3_portfolio_news",
            None
        )

    return st.session_state[
        "system3_categories"
    ]


# ============================================================
# PAGE PRINCIPALE
# ============================================================

def show_system3():

    username = st.session_state.get(
        "username"
    )

    if not username:

        st.error(
            "Tu dois être connecté "
            "pour utiliser Système 3."
        )

        return

    # ========================================================
    # CHARGEMENT PERMANENT DES INTÉRÊTS
    # ========================================================

    categories = (
        load_current_preferences()
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
            "Actualités personnalisées selon "
            "tes intérêts."
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

            st.rerun()

        st.divider()

        # ====================================================
        # ACTUALITÉS
        # ====================================================

        st.header(
            "🔥 Actualités"
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

                    st.session_state[
                        "system3_interest_news"
                    ] = search_news_for_categories(
                        categories,
                        max_per_search=5
                    )

            interest_news = (
                st.session_state[
                    "system3_interest_news"
                ]
            )

            if not interest_news:

                st.warning(
                    "Aucune nouvelle trouvée "
                    "pour tes catégories."
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

                        st.caption(
                            f"📰 {article['source']} "
                            f"• 🕐 {article['time']} "
                            f"• 🎯 "
                            f"{article.get('category', '')}"
                        )

                        if article.get(
                            "matched_interest"
                        ) != article.get(
                            "category"
                        ):

                            st.caption(
                                f"🔎 "
                                f"{article.get('matched_interest', '')}"
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
                                        "category",
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

        # ====================================================
        # IMPORTANT :
        # PAS DE RECHERCHE DU PORTEFEUILLE ICI
        # ====================================================

        st.divider()

        st.caption(
            "📈 Les actualités de ton portefeuille "
            "sont disponibles dans l'onglet "
            "« Mon portefeuille »."
        )


    # ========================================================
    # MES INTÉRÊTS
    # ========================================================

    with tab_settings:

        st.title(
            "⚙️ MES INTÉRÊTS"
        )

        st.write(
            "Tes intérêts sont sauvegardés dans ton compte. "
            "Une catégorie peut fonctionner seule ou "
            "contenir des sujets plus précis."
        )

        st.info(
            "💡 Exemple :\n\n"
            "**Monde** → grandes nouvelles mondiales.\n\n"
            "**Géopolitique** → grandes nouvelles géopolitiques.\n\n"
            "**Géopolitique + Chine + Taïwan** → nouvelles "
            "géopolitiques davantage centrées sur la Chine "
            "et Taïwan."
        )

        st.divider()

        # ====================================================
        # AJOUT CATÉGORIE
        # ====================================================

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

                # Une catégorie peut être vide.
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
                        "✅ Catégorie sauvegardée."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Erreur : {error}"
                    )

        st.divider()

        # ====================================================
        # CATÉGORIES EXISTANTES
        # ====================================================

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

                # ------------------------------------------------
                # INTÉRÊTS EXISTANTS
                # ------------------------------------------------

                selected_interests = st.multiselect(
                    "Intérêts précis",
                    options=interests,
                    default=interests,
                    key=f"select_{category}"
                )

                # ------------------------------------------------
                # AJOUTER UN INTÉRÊT
                # ------------------------------------------------

                new_interest = st.text_input(
                    "Ajouter un intérêt précis",
                    placeholder="Exemple : Chine",
                    key=f"new_{category}"
                )

                col1, col2 = st.columns(2)

                # ------------------------------------------------
                # ENREGISTRER
                # ------------------------------------------------

                with col1:

                    if st.button(
                        "💾 Enregistrer",
                        key=f"save_{category}",
                        use_container_width=True
                    ):

                        updated_interests = list(
                            selected_interests
                        )

                        new_interest_clean = (
                            new_interest.strip()
                        )

                        if new_interest_clean:

                            if (
                                new_interest_clean
                                not in updated_interests
                            ):

                                updated_interests.append(
                                    new_interest_clean
                                )

                        categories[
                            category
                        ] = updated_interests

                        # Supprime les anciennes recherches
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

                # ------------------------------------------------
                # SUPPRIMER
                # ------------------------------------------------

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

        # ====================================================
        # RÉSUMÉ
        # ====================================================

        st.subheader(
            "🎯 Mes intérêts actuels"
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
                    f"toutes les grandes nouvelles"
                )

        st.caption(
            f"{total} intérêt(s) précis"
        )


    # ========================================================
    # PORTEFEUILLE
    #
    # IMPORTANT :
    # C'est seulement ici que les recherches
    # de nouvelles du portefeuille sont faites.
    # ========================================================

    with tab_portfolio:

        st.title(
            "📈 MON PORTEFEUILLE"
        )

        st.write(
            "Les titres proviennent directement "
            "de ton portefeuille de Système 2."
        )

        st.divider()

        # ----------------------------------------------------
        # RÉCUPÉRATION DU PORTEFEUILLE
        # ----------------------------------------------------

        holdings = (
            get_portfolio_holdings()
        )

        if not holdings:

            st.info(
                "Aucun titre actuellement détenu."
            )

        else:

            st.subheader(
                "Mes positions"
            )

            for ticker, quantity in holdings.items():

                company_name = get_company_name(
                    ticker
                )

                st.markdown(
                    f"**{company_name}** "
                    f"({ticker}) — "
                    f"{quantity:g} action(s)"
                )

            st.divider()

            # ------------------------------------------------
            # RECHERCHE UNIQUEMENT ICI
            # ------------------------------------------------

            if st.button(
                "🔎 Rechercher les nouvelles "
                "de mon portefeuille",
                type="primary",
                use_container_width=True
            ):

                st.session_state.pop(
                    "system3_portfolio_news",
                    None
                )

                with st.spinner(
                    "Recherche des vraies nouvelles "
                    "de tes compagnies..."
                ):

                    st.session_state[
                        "system3_portfolio_news"
                    ] = get_portfolio_news(
                        holdings,
                        max_articles_per_company=5
                    )

            # ------------------------------------------------
            # AFFICHAGE
            # ------------------------------------------------

            if (
                "system3_portfolio_news"
                not in st.session_state
            ):

                st.info(
                    "Clique sur « Rechercher les nouvelles "
                    "de mon portefeuille » pour lancer "
                    "la recherche."
                )

            else:

                portfolio_news = (
                    st.session_state[
                        "system3_portfolio_news"
                    ]
                )

                if not portfolio_news:

                    st.warning(
                        "Aucune nouvelle trouvée "
                        "pour ton portefeuille."
                    )

                else:

                    st.subheader(
                        "📰 Actualités de mes compagnies"
                    )

                    for index, article in enumerate(
                        portfolio_news[:30]
                    ):

                        ticker = article.get(
                            "ticker",
                            ""
                        )

                        company = article.get(
                            "company",
                            get_company_name(
                                ticker
                            )
                        )

                        with st.container(
                            border=True
                        ):

                            st.markdown(
                                f"### {company} — "
                                f"{article['title']}"
                            )

                            st.caption(
                                f"📈 {ticker} "
                                f"• 📰 {article['source']} "
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
                                    key=f"portfolio_detail_{index}",
                                    use_container_width=True
                                ):

                                    show_full_details(
                                        article,
                                        f"Compagnie : {company}"
                                    )

                            with col2:

                                if st.button(
                                    "📰 Articles reliés",
                                    key=f"portfolio_related_{index}",
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