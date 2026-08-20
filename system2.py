import streamlit as st
import pandas as pd
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

def get_ai_analysis(ticker, price, pct, rsi, drawdown):
    if not client: return "Erreur : Clé API Gemini manquante."
    prompt = f"Analyse très courte du titre {ticker}. Prix: {price:.2f}$ ({pct:.2f}%), RSI: {rsi:.1f}, Baisse depuis le sommet (Drawdown): {drawdown:.1f}%. Tendance actuelle et conseil rapide."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text
    except Exception as e: return f"Erreur IA : {str(e)}"

def get_macro_analysis(portfolio_data):
    if not client: return "Analyse macro indisponible."
    prompt = f"Voici mon portefeuille boursier et ses métriques : {portfolio_data}. Fais un résumé global en 3-4 lignes maximum. Dis-moi ce qui est à risque (ex: RSI élevé, gros drawdown) et ce qui semble prêt à monter."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text
    except Exception as e: return "Impossible de générer l'analyse globale."

def get_canadian_radar_tickers(sector):
    if not client: return []
    prompt = f"Donne-moi 10 actions canadiennes du secteur '{sector}'. UTILISE UNIQUEMENT DES TICKERS FINISSANT PAR .TO OU .V. Cherche des entreprises avec un bon potentiel à moyen terme. Réponds par une liste simple de symboles séparés par des virgules."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        tickers = re.findall(r'\b[A-Z0-9-]+\.(?:TO|V)\b', response.text)
        return list(set(tickers))
    except Exception: return []

def get_radar_explanation(ticker, sector):
    if not client: return "Erreur IA."
    prompt = f"Analyse l'action canadienne {ticker} (secteur: {sector}) pour un investissement à moyen terme. 1) Explique concrètement pourquoi c'est un bon achat potentiel. 2) Évalue le niveau de risque en donnant un pourcentage clair (ex: 'Risque : 55%') et explique pourquoi. 3) Donne la perspective de croissance."
    try:
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text
    except Exception as e: return f"Erreur IA : {str(e)}"

# --- CALCUL DES INDICATEURS MATHÉMATIQUES ---
def calculate_rsi(series, period=14):
    if len(series) < period: return 50.0
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).iloc[-1]

# --- RÉCUPÉRATION DES DONNÉES BOURSIÈRES ---
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
            
        return {
            "current_price": current_price,
            "daily_pct": daily_pct,
            "high_52": high_52,
            "drawdown": drawdown,
            "rsi": rsi,
            "score": score
        }
    except Exception:
        return None

# --- INTERFACE PRINCIPALE ---
def show_system2():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    st.title("📈 Suivi Boursier & IA")
    
    tab_view, tab_radar, tab_manage = st.tabs(["📈 Mon Portefeuille", "📡 Radar Sectoriel", "⚙️ Gérer mes transactions"])
    
    df_trans = load_stock_transactions()
    my_trans = pd.DataFrame()
    if not df_trans.empty:
        my_trans = df_trans[df_trans['owner'] == st.session_state['username']]

    # --- TAB 1: VISUALISER ---
    with tab_view:
        if my_trans.empty:
            st.info("Aucune transaction. Ajoute des actions dans 'Gérer mes transactions'.")
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
                        "Ticker": ticker,
                        "Valeur": valeur_totale,
                        "RSI": info['rsi'],
                        "Drawdown": info['drawdown'],
                        "Variation": info['daily_pct']
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

                        filtered_data = ticker_data[(ticker_data['date'] >= start_date.strftime("%Y-%m-%d")) & 
                                                    (ticker_data['date'] <= end_date.strftime("%Y-%m-%d"))]
                        
                        plot_data = []
                        for _, row in filtered_data.iterrows():
                            t_price, qty = float(row['buy_price']), float(row['quantity'])
                            t_type, t_date = row.get('trans_type', 'Achat'), row['date']
                            
                            if t_price > 0:
                                lot_pct = ((c_price - t_price) / t_price * 100) if t_type == "Achat" else ((t_price - c_price) / t_price * 100)
                                plot_data.append({
                                    "Lot": f"{t_type} ({t_date})", 
                                    "Rendement (%)": lot_pct, 
                                    "Type": t_type,
                                    "Qty": qty
                                })
                        
                        if plot_data:
                            fig = px.bar(pd.DataFrame(plot_data), x="Lot", y="Rendement (%)", color="Type", 
                                         color_discrete_map={"Achat": "#00CC96", "Vente": "#AB63FA"},
                                         hover_data={"Qty": True, "Type": False},
                                         text="Rendement (%)")
                            fig.update_traces(texttemplate='<b>%{text:.1f}%</b>', textposition='outside', 
                                              marker_line_color='black', marker_line_width=1.5, opacity=0.9)
                            fig.update_layout(title_text=f"Rendement par lot pour {ticker}",
                                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                              xaxis_title="", yaxis_title="Rendement Actuel (%)",
                                              margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified",
                                              yaxis=dict(gridcolor="rgba(128,128,128,0.2)"))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Aucune transaction trouvée dans cette plage de dates.")
                            
                        st.divider()

                        ind_col1, ind_col2, ind_col3 = st.columns(3)
                        with ind_col1:
                            st.metric(label="RSI (Surchauffe/Survente)", value=f"{rsi:.1f}", delta="Suracheté (>70)" if rsi > 70 else "Survendu (<30)" if rsi < 30 else "Neutre", delta_color="inverse")
                        with ind_col2:
                            st.metric(label="Drawdown (Chute sommet)", value=f"{drawdown:.1f}%", delta=f"Sommet: {info['high_52']:.2f}$", delta_color="off")
                        with ind_col3:
                            st.metric(label="Score Technique / 100", value=info['score'])
                        
                        st.divider()
                        
                        if st.button(f"🧠 Analyse IA pour {ticker}", key=f"ai_{ticker}"):
                            with st.spinner("Analyse technique en cours..."):
                                st.write(get_ai_analysis(ticker, c_price, d_pct, rsi, drawdown))

    # --- TAB 2: RADAR SECTORIEL (CANADIEN / SANS CONVERSION) ---
    with tab_radar:
        st.subheader("📡 Radar IA - Potentiel Moyen Terme (Canada uniquement)")
        st.write("Titres cotés sur le TSX (`.TO`) ou la TSX Venture (`.V`) négociables en CAD sans frais de conversion.")
        
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
                            if st.button(f"Pourquoi acheter {t} ? (Risque & Potentiel)", key=f"btn_anal_{t}"):
                                with st.spinner(f"Analyse du risque et du potentiel pour {t}..."):
                                    explication = get_radar_explanation(t, sector_input)
                                    st.session_state[f"expl_{t}"] = explication
                            
                            if f"expl_{t}" in st.session_state:
                                st.write(st.session_state[f"expl_{t}"])
                except Exception: 
                    continue

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