import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import re
from datetime import datetime, timedelta
from google import genai
from database import load_stock_transactions, add_stock_transaction, delete_stock_transaction

# --- CONFIGURATION IA (GEMINI) ---
secrets = st.secrets
if "GEMINI_API_KEY" in secrets:
    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
else:
    client = None

# Modèle sélectionné (Change pour "gemini-3.1-pro" si ton quota est réinitialisé)
SELECTED_MODEL = "gemini-3.6-flash"

def call_flash_ai(prompt):
    if not client: return "Erreur : Clé API Gemini manquante."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text
    except Exception as e: return f"Erreur IA Flash : {str(e)}"

def call_pro_ai(prompt):
    if not client: return "Erreur : Clé API Gemini manquante."
    try:
        config = {"temperature": 0.0}
        response = client.models.generate_content(model=SELECTED_MODEL, contents=prompt, config=config)
        return response.text
    except Exception as e:
        return f"Erreur IA avec {SELECTED_MODEL} : {str(e)}"

# --- CALCULS INDICATEURS TECHNIQUES AVANCÉS ---
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
    """Télécharge 1 an d'historique et calcule un profil quantitatif complet."""
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
        
        # Indicateurs
        rsi = calculate_rsi(close)
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else sma50
        
        # Volatilité annualisée (Écart-type des rendements quotidiens * sqrt(252))
        daily_returns = close.pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Ratio de volume (Volume du jour / Volume moyen 20 jours)
        avg_vol_20 = volume.rolling(20).mean().iloc[-1]
        vol_ratio = (volume.iloc[-1] / avg_vol_20) if avg_vol_20 > 0 else 1.0

        return {
            "Ticker": ticker_symbol,
            "Price": round(current_price, 2),
            "Drawdown": round(drawdown, 2),
            "RSI": round(rsi, 1),
            "SMA20": round(sma20, 2),
            "SMA50": round(sma50, 2),
            "SMA200": round(sma200, 2),
            "Volatility": round(volatility, 2),
            "Vol_Ratio": round(vol_ratio, 2)
        }
    except Exception:
        return None

# --- MOTEUR DE RECHERCHE ET STRATÉGIE QUANTITATIVE EN TEMPS RÉEL ---
def get_live_pro_portfolio_allocation(budget, risk, duration, objective, nb_tickers, comments):
    # ÉTAPE 1 : Identification de tickers pertinents via Gemini
    prompt_candidates = f"""
    Suggère 15 à 20 tickers boursiers canadiens de premier plan (.TO ou .V) adaptés à :
    Tolérance risque: {risk}%, Objectif: {objective}, Secteurs privilégiés: {comments}.
    Réponds UNIQUEMENT par les symboles séparés par des virgules (ex: VFV.TO, XEQT.TO, RY.TO). Aucun autre texte.
    """
    candidates_text = call_flash_ai(prompt_candidates)
    tickers = list(set(re.findall(r'\b[A-Z0-9-]+\.(?:TO|V)\b', candidates_text)))

    if not tickers:
        # Tickers de secours au cas où l'étape 1 échoue
        tickers = ["VFV.TO", "XEQT.TO", "VEQT.TO", "XIU.TO", "VDY.TO", "TEC.TO", "RY.TO", "TD.TO", "CNR.TO", "ATD.TO", "CSU.TO", "AEM.TO"]

    # ÉTAPE 2 : Acquisition et calcul des métriques quantitatives sur Yahoo Finance
    market_data_str = "TICKER | PRIX ($) | DRAWDOWN (%) | RSI (14) | SMA20 | SMA50 | SMA200 | VOLATILITÉ (%) | RATIO VOL.\n"
    market_data_str += "-"*90 + "\n"
    
    valid_count = 0
    for t in tickers:
        m = get_technical_metrics(t)
        if m:
            valid_count += 1
            market_data_str += f"{m['Ticker']:<8} | {m['Price']:<8} | {m['Drawdown']:<12} | {m['RSI']:<8} | {m['SMA20']:<6} | {m['SMA50']:<6} | {m['SMA200']:<6} | {m['Volatility']:<14} | {m['Vol_Ratio']}\n"

    if valid_count == 0:
        return "Erreur lors de la récupération des données en direct depuis Yahoo Finance."

    # ÉTAPE 3 : Arbitrage quantitatif rigoureux par l'IA Pro / Déterministe
    prompt_final = f"""
    Agis en tant que gestionnaire de portefeuille quantitatif senior.
    Sélectionne les {nb_tickers} MEILLEURS titres PARMI LA MATRICE CI-DESSOUS pour construire un portefeuille optimal.

    DONNÉES QUANTITATIVES EN TEMPS RÉEL (Yahoo Finance) :
    {market_data_str}

    PARAMÈTRES INVESTISSEUR :
    - Budget : {budget}$ CAD
    - Tolérance Risque : {risk}%
    - Horizon : {duration}
    - Objectif : {objective}
    - Notes : {comments}

    RÈGLES D'ANALYSE AVANCÉE :
    1. Analyse les convergences techniques : Privilégie les titres où le prix est au-dessus des SMA (tendance haussière), avec un RSI non suracheté (<70) et un risque maîtrisé (volatilité adaptée au profil).
    2. En cas de FNB similaires (ex: VFV vs XEQT/VEQT), compare la volatilité et l'exposition géographique pour justifier le choix exact.
    3. Présente un tableau final clair : Ticker, Allocation ($ et %), Justification quantique/technique stricte basée sur les chiffres fournis, Prix cible et Stop-Loss calculé sous la SMA50 ou SMA200.
    """
    return call_pro_ai(prompt_final)

def get_macro_analysis(portfolio_data):
    prompt = f"Voici un portefeuille et ses données : {portfolio_data}. Analyse macro en 3-4 lignes max : risques immédiats (RSI/Drawdown) et opportunités."
    return call_flash_ai(prompt)

def get_ai_analysis(ticker, price, pct, rsi, drawdown):
    prompt = f"Analyse courte de {ticker}. Prix: {price:.2f}$, RSI: {rsi:.1f}, Drawdown: {drawdown:.1f}%. Tendance et signal technique immédiat."
    return call_flash_ai(prompt)

@st.cache_data(ttl=900)
def get_stock_info(ticker):
    m = get_technical_metrics(ticker)
    if not m: return None
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    daily_pct = 0.0
    if len(hist) >= 2:
        daily_pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
    
    score = int(min(max((m['Price'] / m['SMA20']) * 50, 0), 100)) if m['SMA20'] > 0 else 50
    return {
        "current_price": m['Price'], "daily_pct": daily_pct, "high_52": m['Price'] / (1 + (m['Drawdown']/100)),
        "drawdown": m['Drawdown'], "rsi": m['RSI'], "score": score
    }

# --- INTERFACE STREAMLIT ---
def show_system2():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    st.title("📈 Suivi Boursier Quantitatif & IA")
    st.caption(f"Moteur IA connecté aux flux Yahoo Finance (Modèle : {SELECTED_MODEL})")
    st.divider()
    
    tab_view, tab_manage, tab_strategy = st.tabs([
        "📈 Mon Portefeuille", 
        "⚙️ Gérer mes transactions", 
        "🎯 Stratégie Quantitativée"
    ])
    
    df_trans = load_stock_transactions()
    my_trans = pd.DataFrame()
    if not df_trans.empty:
        my_trans = df_trans[df_trans['owner'] == st.session_state['username']]

    # TAB 1: VISUALISATION
    with tab_view:
        if my_trans.empty:
            st.info("Aucune transaction enregistrée.")
        else:
            unique_tickers = my_trans['ticker'].unique()
            portfolio_details = []
            total_val = 0
            
            for ticker in unique_tickers:
                t_data = my_trans[my_trans['ticker'] == ticker]
                info = get_stock_info(ticker)
                total_qty = sum([float(r['quantity']) if r.get('trans_type', 'Achat') == 'Achat' else -float(r['quantity']) for _, r in t_data.iterrows()])
                
                if info and total_qty > 0:
                    val = total_qty * info['current_price']
                    total_val += val
                    portfolio_details.append({"Ticker": ticker, "Valeur": val, "RSI": info['rsi'], "Drawdown": info['drawdown']})

            if portfolio_details:
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button("Générer l'analyse Macro IA"):
                        st.write(get_macro_analysis(portfolio_details))
                with col2:
                    fig = px.pie(pd.DataFrame(portfolio_details), values='Valeur', names='Ticker', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)

    # TAB 2: GESTION
    with tab_manage:
        st.subheader("Ajouter une transaction")
        with st.form("add_tx"):
            t = st.text_input("Symbole (.TO ou .V)").upper()
            d = st.date_input("Date")
            q = st.number_input("Quantité", min_value=0.01)
            p = st.number_input("Prix ($)", min_value=0.01)
            if st.form_submit_button("Sauvegarder"):
                if t:
                    add_stock_transaction(st.session_state['username'], t, d, q, p, "Achat")
                    st.rerun()

    # TAB 3: STRATÉGIE QUANTITATIVE
    with tab_strategy:
        st.subheader("🎯 Générateur d'Allocation basé sur Données Temps Réel")
        
        with st.form("strat_form"):
            col1, col2 = st.columns(2)
            with col1:
                b = st.number_input("Budget ($ CAD)", min_value=100.0, value=5000.0, step=500.0)
                r = st.slider("Risque (%)", 0, 100, 70)
                dur = st.text_input("Horizon", "3 à 5 ans")
            with col2:
                obj = st.text_input("Objectif", "Croissance équilibrée")
                n = st.number_input("Nombre de titres", 1, 10, 5)
            
            comm = st.text_area("Préférences / Secteurs", "Privilégier les FNB à faibles frais ou actions à fort momentum.")
            
            if st.form_submit_button("Lancer l'analyse quantitative complète"):
                with st.spinner("1. Extraction Yahoo Finance... 2. Calcul des indicateurs techniques... 3. Optimisation IA..."):
                    res = get_live_pro_portfolio_allocation(b, r, dur, obj, n, comm)
                    st.session_state["quant_strat_res"] = res

        if "quant_strat_res" in st.session_state:
            st.markdown("### 📋 Stratégie Générée")
            st.write(st.session_state["quant_strat_res"])