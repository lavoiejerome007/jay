import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import re
import json
from datetime import datetime, timedelta
from google import genai
from database import load_stock_transactions, add_stock_transaction, delete_stock_transaction

# --- CONFIGURATION IA (GEMINI) ---
secrets = st.secrets
if "GEMINI_API_KEY" in secrets:
    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
else:
    client = None

# Modèle standard (rapide / radar / analyses simples)
def call_flash_ai(prompt):
    if not client: return "Erreur : Clé API Gemini manquante."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text
    except Exception as e: return f"Erreur IA Flash : {str(e)}"

# Modèle plus puissant avec paramètre de température bloqué à 0 (déterministe / stable)
def call_pro_ai(prompt):
    if not client: return "Erreur : Clé API Gemini manquante."
    try:
        config = {"temperature": 0.0}
        response = client.models.generate_content(model="gemini-3.1-pro", contents=prompt, config=config)
        return response.text
    except Exception as e:
        try:
            config = {"temperature": 0.0}
            response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt, config=config)
            return response.text + "\n\n*(Note : Basculé sur Flash suite à la limite du modèle Pro)*"
        except Exception as e2:
            return f"Erreur IA Pro/Flash : {str(e2)}"

def get_ai_analysis(ticker, price, pct, rsi, drawdown):
    prompt = f"Analyse très courte du titre {ticker}. Prix: {price:.2f}$ ({pct:.2f}%), RSI: {rsi:.1f}, Baisse depuis le sommet (Drawdown): {drawdown:.1f}%. Tendance actuelle et conseil rapide."
    return call_flash_ai(prompt)

def get_macro_analysis(portfolio_data):
    prompt = f"Voici mon portefeuille boursier et ses métriques : {portfolio_data}. Fais un résumé global en 3-4 lignes maximum. Dis-moi ce qui est à risque (ex: RSI élevé, gros drawdown) et ce qui semble prêt à monter."
    return call_flash_ai(prompt)

def get_canadian_radar_tickers(sector):
    if not client: return []
    prompt = f"Donne-moi 10 actions canadiennes du secteur '{sector}'. UTILISE UNIQUEMENT DES TICKERS FINISSANT PAR .TO OU .V. Cherche des entreprises avec un bon potentiel à moyen terme. Réponds par une liste simple de symboles séparés par des virgules."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        tickers = re.findall(r'\b[A-Z0-9-]+\.(?:TO|V)\b', response.text)
        return list(set(tickers))
    except Exception: return []

def get_radar_explanation(ticker, sector):
    prompt = f"Analyse l'action canadienne {ticker} (secteur: {sector}) pour un investissement à moyen terme. 1) Explique concrètement pourquoi c'est un bon achat potentiel. 2) Évalue le niveau de risque en donnant un pourcentage clair (ex: 'Risque : 55%') et explique pourquoi. 3) Donne la perspective de croissance."
    return call_flash_ai(prompt)

# --- CALCUL DES INDICATEURS MATHÉMATIQUES ET TECHNIQUES AVANCÉS ---
def calculate_rsi(series, period=14):
    if len(series) < period: return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).iloc[-1]

def get_technical_metrics(ticker_symbol):
    """Calcule une matrice d'indicateurs quantitatifs complets en temps réel."""
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 50:
            return None

        close = hist['Close']
        volume = hist['Volume']
        
        current_price = close.iloc[-1]
        high_52 = close.max()
        drawdown = ((current_price - high_52) / high_52) * 100
        
        rsi = calculate_rsi(close)
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else sma50
        
        daily_returns = close.pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        avg_vol_20 = volume.rolling(20).mean().iloc[-1]
        vol_ratio = (volume.iloc[-1] / avg_vol_20) if avg_vol_20 > 0 else 1.0

        return {
            "Ticker": ticker_symbol, "Price": round(current_price, 2),
            "Drawdown": round(drawdown, 2), "RSI": round(rsi, 1),
            "SMA20": round(sma20, 2), "SMA50": round(sma50, 2),
            "SMA200": round(sma200, 2), "Volatility": round(volatility, 2),
            "Vol_Ratio": round(vol_ratio, 2)
        }
    except Exception:
        return None

# --- MOTEUR IA PRO AVEC DONNÉES TEMPS RÉEL YAHOO FINANCE ---
@st.cache_data(ttl=1800)
def get_pro_portfolio_allocation(budget, risk, duration, objective, nb_tickers, comments):
    # Étape 1 : Idéation de candidats ciblés via Gemini Flash
    prompt_candidates = f"""
    Suggère 15 à 20 tickers boursiers canadiens principaux (.TO ou .V) adaptés à :
    Risque: {risk}%, Objectif: {objective}, Secteurs/Notes: {comments}.
    Réponds UNIQUEMENT par les symboles séparés par des virgules (ex: VFV.TO, XEQT.TO, RY.TO). Aucun autre texte.
    """
    candidates_text = call_flash_ai(prompt_candidates)
    tickers = list(set(re.findall(r'\b[A-Z0-9-]+\.(?:TO|V)\b', candidates_text)))

    if not tickers:
        tickers = ["VFV.TO", "XEQT.TO", "XIU.TO", "VDY.TO", "TEC.TO", "RY.TO", "TD.TO", "CNR.TO", "ATD.TO"]

    # Étape 2 : Extraction et calcul des données techniques en direct via yfinance
    market_data_str = "TICKER | PRIX ($) | DRAWDOWN (%) | RSI(14) | SMA20 | SMA50 | SMA200 | VOLATILITÉ(%) | RATIO VOL.\n"
    market_data_str += "-"*95 + "\n"
    
    valid_count = 0
    for t in tickers:
        m = get_technical_metrics(t)
        if m:
            valid_count += 1
            market_data_str += f"{m['Ticker']:<8} | {m['Price']:<8} | {m['Drawdown']:<12} | {m['RSI']:<8} | {m['SMA20']:<6} | {m['SMA50']:<6} | {m['SMA200']:<6} | {m['Volatility']:<14} | {m['Vol_Ratio']}\n"

    if valid_count == 0:
        return "Erreur : Impossible de récupérer les données techniques de Yahoo Finance pour le moment.", []

    # Étape 3 : Arbitrage quantitatif déterministe basé strictement sur les chiffres du marché
    prompt_final = f"""
    Agis en tant que gestionnaire de patrimoine quantitatif senior pour un investisseur canadien. 
    Sélectionne les {nb_tickers} MEILLEURS titres PARMI LA MATRICE TECHNIQUE CI-DESSOUS pour un budget de {budget}$ CAD.

    DONNÉES TECHNIQUES EN TEMPS RÉEL (Yahoo Finance) :
    {market_data_str}

    PARAMÈTRES DE L'INVESTISSEUR :
    - Budget total : {budget}$ CAD
    - Tolérance au risque : {risk}%
    - Durée du placement : {duration}
    - Objectif : {objective}
    - Commentaires : {comments}

    RÈGLES D'ANALYSE STRICTES :
    1. Sélectionne uniquement parmi la liste ci-dessus (.TO / .V).
    2. Analyse les données techniques : privilégie les titres en tendance haussière (Prix > SMA50), avec un RSI sain (<70) et un profil de volatilité adapté au risque ({risk}%).
    3. Présente un tableau final clair comportant :
       - Ticker exact et nom du titre.
       - Montant ($) et allocation (%).
       - Justification quantique/technique basée sur les chiffres fournis (RSI, Drawdown, SMA).
       - Prix cible et niveau de stop-loss sous une SMA clé.
       
    4. OBLIGATOIRE POUR L'AUTOMATISATION : À la toute fin de ta réponse, ajoute exactement cette balise `[JSON]` suivie de ta recommandation en format JSON pur, puis termine par `[/JSON]`.
    Exemple de format attendu :
    [JSON]
    [
      {{"ticker": "VFV.TO", "montant": 2500}},
      {{"ticker": "RY.TO", "montant": 2500}}
    ]
    [/JSON]
    """
    response_text = call_pro_ai(prompt_final)
    
    # Extraction de la partie JSON pour le code Python
    portfolio_list = []
    try:
        match = re.search(r'\[JSON\](.*?)\[/JSON\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            # Nettoyage d'éventuelles balises markdown résiduelles
            json_str = json_str.replace('```json', '').replace('```', '')
            portfolio_list = json.loads(json_str)
    except Exception as e:
        pass # Échec silencieux, on retournera une liste vide
        
    # Nettoyage du texte d'affichage (on cache la balise JSON à l'utilisateur)
    display_text = re.sub(r'\[JSON\].*?\[/JSON\]', '', response_text, flags=re.DOTALL).strip()
    
    return display_text, portfolio_list

def get_pro_additional_funds_advice(extra_money, current_portfolio_summary):
    prompt = f"""
    J'ai un montant supplémentaire de {extra_money}$ CAD à placer. En te basant sur mon portefeuille actuel ({current_portfolio_summary}), indique de façon stable et logique où injecter cet argent pour respecter ma stratégie (uniquement des tickers canadiens .TO ou .V).
    """
    return call_pro_ai(prompt)

def get_pro_rebalancing_advice(current_portfolio_summary):
    prompt = f"""
    Analyse de manière objective la dérive de mon portefeuille : {current_portfolio_summary}.
    Fournis un plan de réajustement tactique constant et structuré (arbitrages, prises de profits, renforcements).
    """
    return call_pro_ai(prompt)

@st.cache_data(ttl=900)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y") 
        if hist.empty: return None
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
        daily_pct = ((current_price - prev_price) / prev_price) * 100
        high_52 = hist['Close'].max()
        drawdown = ((current_price - high_52) / high_52) * 100
        rsi = calculate_rsi(hist['Close'])
        sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        score = 50
        if pd.notna(sma20) and sma20 > 0:
            score = int(min(max((current_price / sma20) * 50, 0), 100))
        return {"current_price": current_price, "daily_pct": daily_pct, "high_52": high_52, "drawdown": drawdown, "rsi": rsi, "score": score}
    except Exception:
        return None

# --- INTERFACE PRINCIPALE ---
def show_system2():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    # --- EN-TÊTE AVEC NOTES GLOBALES (EN HAUT À DROITE) ---
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        st.title("📈 Suivi Boursier & IA")
    with header_col2:
        st.metric("🎯 Progrès Objectif", "82 / 100", delta="+4% ce mois")
    with header_col3:
        st.metric("⚡ Perf. Semaine", "+1.8%", delta="Bonne tenue")

    st.divider()
    
    # --- ONGLETS ---
    tab_view, tab_radar, tab_manage, tab_strategy = st.tabs([
        "📈 Mon Portefeuille", 
        "📡 Radar Sectoriel", 
        "⚙️ Gérer mes transactions", 
        "🎯 Stratégie & Allocation"
    ])
    
    df_trans = load_stock_transactions()
    my_trans = pd.DataFrame()
    if not df_trans.empty:
        my_trans = df_trans[df_trans['owner'] == st.session_state['username']]

    # --- TAB 1: VISUALISER ---
    with tab_view:
        if my_trans.empty:
            st.info("Aucune transaction. Ajoute des actions dans 'Gérer mes transactions' ou via la stratégie.")
        else:
            unique_tickers = my_trans['ticker'].unique()
            portfolio_details = []
            total_portfolio_value = 0
            weighted_daily_pct = 0
            
            for ticker in unique_tickers:
                ticker_data = my_trans[my_trans['ticker'] == ticker]
                info = get_stock_info(ticker)
                total_qty = sum([float(r['quantity']) if r.get('trans_type', 'Achat') == 'Achat' else -float(r['quantity']) for _, r in ticker_data.iterrows()])
                
                if info and total_qty > 0:
                    valeur_totale = total_qty * info['current_price']
                    total_portfolio_value += valeur_totale
                    portfolio_details.append({
                        "Ticker": ticker, "Valeur": valeur_totale, "RSI": info['rsi'],
                        "Drawdown": info['drawdown'], "Variation": info['daily_pct']
                    })

            if total_portfolio_value > 0:
                for item in portfolio_details:
                    poids = item["Valeur"] / total_portfolio_value
                    weighted_daily_pct += item["Variation"] * poids

            st.header("🌍 Vue Macro du Portefeuille")
            macro_col1, macro_col2 = st.columns([2, 1])
            
            with macro_col1:
                with st.container(border=True):
                    st.markdown("🤖 **L'Avis de l'IA sur l'ensemble de tes positions**")
                    if st.button("Générer la vue macro"):
                        with st.spinner("Analyse globale en cours..."):
                            st.write(get_macro_analysis(portfolio_details))
                    st.divider()
                    health_color = "#00CC96" if weighted_daily_pct >= 0 else "#EF553B"
                    st.markdown(f"**Santé du portefeuille aujourd'hui :** <span style='color:{health_color}; font-size:1.2em; font-weight:bold;'>{weighted_daily_pct:.2f}%</span>", unsafe_allow_html=True)

            with macro_col2:
                if portfolio_details:
                    fig_pie = px.pie(pd.DataFrame(portfolio_details), values='Valeur', names='Ticker', hole=0.45)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
                    fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)

            st.divider()
            st.subheader("Analyse détaillée par titre")
            
            for ticker in unique_tickers:
                ticker_data = my_trans[my_trans['ticker'] == ticker]
                info = get_stock_info(ticker)
                total_qty = sum([float(r['quantity']) if r.get('trans_type', 'Achat') == 'Achat' else -float(r['quantity']) for _, r in ticker_data.iterrows()])
                
                if info and not ticker_data.empty:
                    c_price, d_pct = info['current_price'], info['daily_pct']
                    rsi, drawdown = info['rsi'], info['drawdown']
                    color = "#00CC96" if d_pct >= 0 else "#EF553B"
                    
                    st.markdown(f"### {ticker} | 📦 {total_qty:.2f} actions")
                    st.markdown(f"Prix: **{c_price:.2f}$** <span style='color:{color}; font-weight:bold;'>({d_pct:.2f}%)</span>", unsafe_allow_html=True)
                    
                    with st.expander(f"📊 Graphiques & Indicateurs pour {ticker}"):
                        col_date1, col_date2 = st.columns(2)
                        with col_date1:
                            start_date = st.date_input("Depuis le :", value=datetime.today() - timedelta(days=365), key=f"start_{ticker}")
                        with col_date2:
                            end_date = st.date_input("Jusqu'au :", value=datetime.today(), key=f"end_{ticker}")

                        filtered_data = ticker_data[(ticker_data['date'] >= start_date.strftime("%Y-%m-%d")) & (ticker_data['date'] <= end_date.strftime("%Y-%m-%d"))]
                        plot_data = []
                        for _, row in filtered_data.iterrows():
                            t_price, qty = float(row['buy_price']), float(row['quantity'])
                            t_type, t_date = row.get('trans_type', 'Achat'), row['date']
                            if t_price > 0:
                                lot_pct = ((c_price - t_price) / t_price * 100) if t_type == "Achat" else ((t_price - c_price) / t_price * 100)
                                plot_data.append({"Lot": f"{t_type} ({t_date})", "Rendement (%)": lot_pct, "Type": t_type, "Qty": qty})
                        
                        if plot_data:
                            fig = px.bar(pd.DataFrame(plot_data), x="Lot", y="Rendement (%)", color="Type", 
                                         color_discrete_map={"Achat": "#00CC96", "Vente": "#AB63FA"}, text="Rendement (%)")
                            fig.update_traces(texttemplate='<b>%{text:.1f}%</b>', textposition='outside', marker_line_color='black', marker_line_width=1.5, opacity=0.9)
                            fig.update_layout(title_text=f"Rendement par lot pour {ticker}", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Rendement Actuel (%)", margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified", yaxis=dict(gridcolor="rgba(128,128,128,0.2)"))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Aucune transaction trouvée dans cette plage de dates.")
                            
                        st.divider()
                        ind_col1, ind_col2, ind_col3 = st.columns(3)
                        with ind_col1:
                            st.metric(label="RSI", value=f"{rsi:.1f}")
                        with ind_col2:
                            st.metric(label="Drawdown", value=f"{drawdown:.1f}%")
                        with ind_col3:
                            st.metric(label="Score Technique", value=info['score'])
                        
                        st.divider()
                        if st.button(f"🧠 Analyse IA pour {ticker}", key=f"ai_{ticker}"):
                            with st.spinner("Analyse technique en cours..."):
                                st.write(get_ai_analysis(ticker, c_price, d_pct, rsi, drawdown))

    # --- TAB 2: RADAR SECTORIEL ---
    with tab_radar:
        st.subheader("📡 Radar IA - Potentiel Moyen Terme (Canada uniquement)")
        sector_input = st.text_input("Secteur à surveiller", "Énergie, Automatisation, Technologie ou Finance")

        if st.button("Chercher des opportunités canadiennes"):
            st.session_state["radar_tickers"] = get_canadian_radar_tickers(sector_input)

        if "radar_tickers" in st.session_state and st.session_state["radar_tickers"]:
            for t in st.session_state["radar_tickers"]:
                try:
                    stock_data = yf.Ticker(t).fast_info
                    price = stock_data.get('lastPrice') or 0
                    if price > 0:
                        with st.expander(f"🇨🇦 **{t}** — Prix actuel : {price:.2f}$"):
                            if st.button(f"Pourquoi acheter {t} ?", key=f"btn_anal_{t}"):
                                with st.spinner(f"Analyse en cours pour {t}..."):
                                    st.session_state[f"expl_{t}"] = get_radar_explanation(t, sector_input)
                            if f"expl_{t}" in st.session_state:
                                st.write(st.session_state[f"expl_{t}"])
                except Exception: continue

    # --- TAB 3: GÉRER MES TRANSACTIONS ---
    with tab_manage:
        if not my_trans.empty:
            st.subheader("Mes Titres Actuels")
            for t in my_trans['ticker'].unique():
                df_t = my_trans[my_trans['ticker'] == t]
                total_qty = sum([float(r['quantity']) if r.get('trans_type') == 'Achat' else -float(r['quantity']) for _, r in df_t.iterrows()])
                
                with st.expander(f"📁 {t} - Total en main : {total_qty:.2f}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        action = st.selectbox("Type", ["Achat", "Vente"], key=f"act_{t}")
                        d = st.date_input("Date", key=f"date_{t}")
                        q = st.number_input("Qté", min_value=0.01, step=1.0, key=f"qty_{t}")
                        p = st.number_input("Prix", min_value=0.01, step=0.1, key=f"prc_{t}")
                        if st.button("Enregistrer", key=f"btn_{t}"):
                            add_stock_transaction(st.session_state['username'], t, d, q, p, action)
                            st.rerun()
                    with c2:
                        for _, row in df_t.sort_values(by="date", ascending=False).iterrows():
                            icon = '🟢' if row.get('trans_type', 'Achat') == 'Achat' else '🟣'
                            st.write(f"{icon} {row.get('trans_type', 'Achat')} | {row['date']} | {row['quantity']} à {row['buy_price']}$")
                            if st.button("Supprimer", key=f"del_{row['id']}"):
                                delete_stock_transaction(row['id'])
                                st.rerun()
        
        st.divider()
        st.subheader("Ajouter un TOUT NOUVEAU titre")
        with st.form("new_stock"):
            t = st.text_input("Symbole (ex: RY.TO, CSU.TO, CGNT.V)").upper()
            d = st.date_input("Date")
            q = st.number_input("Qté", min_value=0.01, step=1.0)
            p = st.number_input("Prix d'achat ($)", min_value=0.01, step=0.1)
            if st.form_submit_button("Ajouter"):
                if t:
                    add_stock_transaction(st.session_state['username'], t, d, q, p, "Achat")
                    st.rerun()

    # --- TAB 4: STRATÉGIE & ALLOCATION (TEMPS RÉEL & QUANTITATIF) ---
    with tab_strategy:
        st.subheader("🎯 Gestion & Stratégie de Portefeuille (Modèle Pro Quantitatif)")
        st.write("Allocation déterministe basée sur l'extraction en temps réel des données techniques Yahoo Finance (RSI, SMA, Volatilité).")

        with st.form("strategy_form"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                strat_budget = st.number_input("Montant d'argent à placer ($ CAD)", min_value=100.0, step=500.0, value=5000.0)
                strat_risk = st.slider("Tolérance au risque (%)", min_value=0, max_value=100, value=80, help="0% = Très sécuritaire, 100% = Croissance agressive")
                strat_duration = st.text_input("Durée du placement", "3 à 5 ans")
            with col_s2:
                strat_objective = st.text_input("Objectif du placement", "Maximiser la croissance du capital intelligemment")
                strat_nb_tickers = st.number_input("Nombre de titres différents souhaités", min_value=1, max_value=15, value=5)
            
            strat_comments = st.text_area("Commentaires / Infos additionnelles", "Je veux des choix constants, optimisés et comparés de manière stricte en CAD (.TO / .V).")
            
            submitted_strategy = st.form_submit_button("Générer la stratégie temps réel (IA Pro)")

        if submitted_strategy:
            with st.spinner("1. Extraction Yahoo Finance... 2. Calcul des métriques techniques... 3. Optimization IA..."):
                display_text, portfolio_data = get_pro_portfolio_allocation(strat_budget, strat_risk, strat_duration, strat_objective, strat_nb_tickers, strat_comments)
                st.session_state["last_strategy_text"] = display_text
                st.session_state["last_strategy_data"] = portfolio_data

        if "last_strategy_text" in st.session_state:
            st.markdown("### 📋 Résultat de la Stratégie Basée sur les Chiffres du Marché")
            st.write(st.session_state["last_strategy_text"])
            
            if st.session_state.get("last_strategy_data"):
                st.warning("⚠️ **Attention** : Accepter cette stratégie remplacera intégralement votre portefeuille actuel (toutes vos transactions existantes seront supprimées).")
                if st.button("✅ Accepter et remplacer mon portefeuille par cette stratégie"):
                    with st.spinner("Mise à jour du portefeuille en cours..."):
                        # 1. Supprimer l'ancien portefeuille
                        for _, row in my_trans.iterrows():
                            delete_stock_transaction(row['id'])
                            
                        # 2. Ajouter les nouvelles positions
                        for item in st.session_state["last_strategy_data"]:
                            ticker = item.get("ticker")
                            montant = float(item.get("montant", 0))
                            if ticker and montant > 0:
                                info = get_stock_info(ticker)
                                price = info['current_price'] if info else 1.0 # Fallback 
                                qty = montant / price if price > 0 else 0
                                add_stock_transaction(
                                    st.session_state['username'], 
                                    ticker, 
                                    datetime.today().date(), 
                                    round(qty, 4), 
                                    round(price, 2), 
                                    "Achat"
                                )
                        
                    st.success("Portefeuille remplacé avec succès !")
                    del st.session_state["last_strategy_text"]
                    del st.session_state["last_strategy_data"]
                    st.rerun()
            else:
                st.info("💡 (L'IA n'a pas pu formater les données pour l'automatisation. Veuillez ajouter ces titres manuellement via l'onglet 'Gérer mes transactions'.)")

        st.divider()
        st.subheader("➕ Ajouter des fonds supplémentaires")
        extra_budget = st.number_input("Montant d'argent supplémentaire à placer ($)", min_value=50.0, step=100.0, value=1000.0, key="extra_b")
        if st.button("Où placer ces nouveaux fonds de façon optimale ? (IA Pro)"):
            with st.spinner("Calcul d'optimisation d'apport..."):
                portfolio_summary = f"Portefeuille actuel : {unique_tickers if 'unique_tickers' in locals() else 'Vide'}"
                advice = get_pro_additional_funds_advice(extra_budget, portfolio_summary)
                st.write(advice)

        st.divider()
        st.subheader("⚖️ Réajuster mon portefeuille")
        if st.button("Lancer le réajustement tactique (IA Pro)"):
            with st.spinner("Calcul du rééquilibrage..."):
                portfolio_summary = f"Transactions actuelles : {my_trans.to_dict() if not my_trans.empty else 'Vide'}"
                rebal_advice = get_pro_rebalancing_advice(portfolio_summary)
                st.write(rebal_advice)
