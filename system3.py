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
# NETTOYAGE
# ============================================================

def clean_text(text):
    """Nettoie le texte provenant du RSS."""

    if not text:
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# DATE
# ============================================================

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

def fetch_google_news(query, max_results=10):
    """
    Recherche de vrais articles avec Google News RSS.

    Les informations suivantes viennent directement du flux :
    - titre
    - source
    - date
    - description
    - lien
    """

    try:

        if not query:
            return []

        url = GOOGLE_NEWS_RSS.format(
            query=quote_plus(str(query))
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        articles = []

        for item in root.findall(".//item"):

            title_node = item.find("title")
            link_node = item.find("link")
            description_node = item.find("description")
            date_node = item.find("pubDate")
            source_node = item.find("source")

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
                "time": get_relative_time(date)
            })

            if len(articles) >= max_results:
                break

        return articles

    except Exception:
        return []


# ============================================================
# DUPLICATION
# ============================================================

def normalize_title(title):

    title = clean_text(title).lower()

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


def remove_duplicates(articles):

    seen = set()
    result = []

    for article in articles:

        title = normalize_title(
            article.get("title", "")
        )

        if not title:
            continue

        if title in seen:
            continue

        seen.add(title)

        result.append(article)

    return result


# ============================================================
# PORTEFEUILLE RÉEL DE SYSTÈME 2
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

        # ----------------------------------------------------
        # S'assurer que les colonnes existent
        # ----------------------------------------------------

        required_columns = [
            "owner",
            "ticker",
            "quantity",
            "trans_type"
        ]

        for column in required_columns:

            if column not in df.columns:

                if column == "trans_type":
                    df[column] = "Achat"
                else:
                    return {}

        # ----------------------------------------------------
        # Seulement l'utilisateur connecté
        # ----------------------------------------------------

        df = df[
            df["owner"].astype(str).str.strip()
            == str(username).strip()
        ]

        if df.empty:
            return {}

        holdings = {}

        # ----------------------------------------------------
        # Calcul des positions
        # ----------------------------------------------------

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
            ).strip()

            if trans_type.lower() == "achat":

                holdings[ticker] = (
                    holdings.get(
                        ticker,
                        0
                    )
                    + quantity
                )

            elif trans_type.lower() == "vente":

                holdings[ticker] = (
                    holdings.get(
                        ticker,
                        0
                    )
                    - quantity
                )

        # ----------------------------------------------------
        # Garder seulement les positions positives
        # ----------------------------------------------------

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

    all_articles = []

    for ticker in holdings.keys():

        articles = fetch_google_news(
            ticker,
            max_results=max_articles_per_ticker
        )

        for article in articles:

            article["ticker"] = ticker

        all_articles.extend(
            articles
        )

    return remove_duplicates(
        all_articles
    )


# ============================================================
# NOUVELLES SELON LES INTÉRÊTS
# ============================================================

def search_news_for_interests(
    interests,
    max_per_interest=5
):

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

        # Si le client existe déjà
        # dans le fichier appelant
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

Tu dois utiliser UNIQUEMENT les informations
présentes dans le titre et le contenu fourni.

INTERDICTIONS :
- ne pas inventer de faits;
- ne pas inventer de chiffres;
- ne pas inventer de citations;
- ne pas inventer de contexte;
- ne pas prétendre avoir lu l'article complet.

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

Fais :
1. un résumé de 3 à 5 phrases;
2. explique en 1 ou 2 phrases pourquoi cette nouvelle
   peut être importante.

Si le contenu fourni est insuffisant, indique-le.
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

IMPORTANT :
Tu dois uniquement utiliser les informations
qui sont fournies ci-dessous.

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

Structure :

### 1. Ce qui s'est passé

Explique les faits disponibles.

### 2. Pourquoi c'est important

Explique les conséquences possibles.

### 3. Qui est concerné

Entreprises, secteurs, pays ou personnes
si ces informations sont disponibles.

### 4. Impact possible

Explique les impacts possibles.

Fais clairement la différence entre :
- les faits;
- les conséquences possibles;
- les hypothèses.

### 5. À retenir

Donne les 3 points essentiels.

Si les informations fournies sont insuffisantes,
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

def get_related_articles(article):

    title = article.get(
        "title",
        ""
    )

    if not title:
        return []

    # Recherche basée sur le vrai titre
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

        if article.get("ticker"):

            st.info(
                f"📈 Cette nouvelle concerne "
                f"**{article['ticker']}**, "
                f"un titre de ton portefeuille."
            )

        if article.get(
            "matched_interest"
        ):

            st.info(
                f"🎯 Cette nouvelle correspond "
                f"à ton intérêt : "
                f"**{article['matched_interest']}**"
            )

        st.divider()

        # ----------------------------------------------------
        # RÉSUMÉ
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # CONTENU RSS
        # ----------------------------------------------------

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
                "de résumé pour cet article."
            )

        # ----------------------------------------------------
        # ANALYSE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ARTICLE ORIGINAL
        # ----------------------------------------------------

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
# SAUVEGARDER LES PRÉFÉRENCES
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

        result = save_system3_preferences(
            username,
            categories
        )

        # Normalement :
        # (True, "")
        return result

    except Exception as e:

        return (
            False,
            str(e)
        )


# ============================================================
# CHARGER LES PRÉFÉRENCES
# ============================================================

def load_current_preferences():

    username = st.session_state.get(
        "username"
    )

    if not username:
        return {}

    # --------------------------------------------------------
    # IMPORTANT :
    # si un autre utilisateur vient de se connecter,
    # on ne doit PAS conserver les intérêts précédents.
    # --------------------------------------------------------

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

        # Les anciennes nouvelles ne correspondent
        # peut-être plus aux nouveaux intérêts.
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

    # ========================================================
    # UTILISATEUR
    # ========================================================

    username = st.session_state.get(
        "username"
    )

    if not username:

        st.error(
            "Tu dois être connecté pour utiliser Système 3."
        )

        return

    # ========================================================
    # CHARGEMENT PERMANENT
    # ========================================================

    categories = load_current_preferences()

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
            "tes intérêts et ton portefeuille."
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

            st.session_state.pop(
                "system3_portfolio_news",
                None
            )

            st.rerun()

        st.divider()

        # ====================================================
        # INTÉRÊTS
        # ====================================================

        all_interests = []

        for category, interests in categories.items():

            for interest in interests:

                if interest not in all_interests:

                    all_interests.append(
                        interest
                    )

        st.header(
            "🔥 Actualités selon mes intérêts"
        )

        if not all_interests:

            st.info(
                "Tu n'as actuellement aucun intérêt."
                " Va dans « Mes intérêts » pour en ajouter."
            )

        else:

            # ------------------------------------------------
            # PREMIÈRE RECHERCHE
            # ------------------------------------------------

            if (
                "system3_interest_news"
                not in st.session_state
            ):

                with st.spinner(
                    "Recherche des vraies nouvelles..."
                ):

                    st.session_state[
                        "system3_interest_news"
                    ] = search_news_for_interests(
                        all_interests,
                        max_per_interest=5
                    )

            interest_news = (
                st.session_state[
                    "system3_interest_news"
                ]
            )

            if not interest_news:

                st.warning(
                    "Aucune nouvelle trouvée "
                    "pour tes intérêts."
                )

            else:

                # ------------------------------------------------
                # AFFICHAGE
                # ------------------------------------------------

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


        # ====================================================
        # PORTEFEUILLE
        # ====================================================

        st.divider()

        st.header(
            "📈 Actualités de mon portefeuille"
        )

        holdings = (
            get_portfolio_holdings()
        )

        if not holdings:

            st.info(
                "Aucun titre actuellement détenu "
                "dans ton portefeuille de Système 2."
            )

        else:

            portfolio_display = " • ".join(
                [
                    f"{ticker} ({quantity:g})"
                    for ticker, quantity
                    in holdings.items()
                ]
            )

            st.caption(
                f"Titres suivis : {portfolio_display}"
            )

            # ------------------------------------------------
            # RECHERCHE
            # ------------------------------------------------

            if (
                "system3_portfolio_news"
                not in st.session_state
            ):

                with st.spinner(
                    "Recherche des nouvelles "
                    "de ton portefeuille..."
                ):

                    st.session_state[
                        "system3_portfolio_news"
                    ] = get_portfolio_news(
                        holdings,
                        max_articles_per_ticker=5
                    )

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

                for index, article in enumerate(
                    portfolio_news[:20]
                ):

                    ticker = article.get(
                        "ticker",
                        ""
                    )

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### 📈 {ticker} — "
                            f"{article['title']}"
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
                                key=f"portfolio_detail_{index}",
                                use_container_width=True
                            ):

                                show_full_details(
                                    article,
                                    f"Titre détenu : {ticker}"
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


    # ========================================================
    # MES INTÉRÊTS
    # ========================================================

    with tab_settings:

        st.title(
            "⚙️ MES INTÉRÊTS"
        )

        st.write(
            "Tes intérêts sont sauvegardés dans ton compte. "
            "Les modifications restent après une déconnexion "
            "ou un redémarrage de l'application."
        )

        st.divider()

        # ====================================================
        # AJOUTER UNE CATÉGORIE
        # ====================================================

        st.subheader(
            "➕ Ajouter une catégorie"
        )

        new_category = st.text_input(
            "Nom de la catégorie",
            placeholder="Exemple : 🧬 Santé",
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
                        f"Erreur de sauvegarde : {error}"
                    )

        st.divider()

        # ====================================================
        # CATÉGORIES
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

                st.write(
                    f"{len(interests)} intérêt(s)"
                )

                # ------------------------------------------------
                # INTÉRÊTS
                # ------------------------------------------------

                selected_interests = st.multiselect(
                    "Intérêts suivis",
                    options=interests,
                    default=interests,
                    key=f"select_{category}"
                )

                # ------------------------------------------------
                # AJOUTER UN INTÉRÊT
                # ------------------------------------------------

                new_interest = st.text_input(
                    "Ajouter un intérêt",
                    placeholder="Exemple : Intelligence artificielle",
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

                        # ----------------------------------------
                        # MODIFIER LA MÉMOIRE DE SESSION
                        # ----------------------------------------

                        categories[
                            category
                        ] = updated_interests

                        # ----------------------------------------
                        # SUPPRIMER LES ANCIENNES NOUVELLES
                        # ----------------------------------------

                        st.session_state.pop(
                            "system3_interest_news",
                            None
                        )

                        # ----------------------------------------
                        # SAUVEGARDER DANS GOOGLE SHEETS
                        # ----------------------------------------

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
                # SUPPRIMER CATÉGORIE
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
                                "✅ Catégorie supprimée définitivement."
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Erreur : {error}"
                            )

        # ====================================================
        # RÉSUMÉ
        # ====================================================

        st.divider()

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

        st.caption(
            f"{total} intérêt(s) suivi(s)"
        )


    # ========================================================
    # PORTEFEUILLE
    # ========================================================

    with tab_portfolio:

        st.title(
            "📈 MON PORTEFEUILLE"
        )

        st.write(
            "Les titres affichés ici proviennent "
            "directement des transactions de Système 2."
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

                with st.container(
                    border=True
                ):

                    st.subheader(
                        ticker
                    )

                    st.write(
                        f"Actions détenues : "
                        f"**{quantity:g}**"
                    )

                    if st.button(
                        f"📰 Nouvelles de {ticker}",
                        key=f"ticker_news_{ticker}",
                        use_container_width=True
                    ):

                        with st.spinner(
                            f"Recherche des vraies nouvelles "
                            f"de {ticker}..."
                        ):

                            ticker_news = (
                                fetch_google_news(
                                    ticker,
                                    max_results=10
                                )
                            )

                        if not ticker_news:

                            st.warning(
                                "Aucune nouvelle trouvée."
                            )

                        else:

                            for i, article in enumerate(
                                ticker_news
                            ):

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

                                st.link_button(
                                    "Lire l'article original ↗",
                                    article["link"],
                                    use_container_width=True
                                )

                                st.divider()