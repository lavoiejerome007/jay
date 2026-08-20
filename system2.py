import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta
from google import genai
from database import load_stock_transactions, add_stock_transaction, delete_stock_transaction

# --- CONFIGURATION IA (GEMINI) ---
secrets = st.secrets
if "GEMINI_API_KEY" in secrets:
    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
else:
    client = None

def get_ai_analysis(ticker, price, pct):
    if not client:
        return "Erreur : La clé API Gemini est manquante dans les secrets."
    
    prompt = f"Fais une analyse très courte et directe du titre {ticker}. Le prix actuel est de {price:.2f}$ avec une variation de {pct:.2f}% aujourd'hui. Donne-moi ton avis sur la tendance actuelle et un conseil rapide pour un investisseur."
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur lors de l'analyse IA : {str(e)}"

# --- RÉCUPÉRATION DES DONNÉES BOURSIÈRES ---
@st.cache_data(ttl=900)
def get_stock_info(ticker):
    current_price = 0.0
    daily_pct = 0.0
    clean_news = []
    earnings_date = "N/A"
    score = 50 # Score par défaut
    
    try:
        stock = yf.Ticker(ticker)
        # On récupère sur 1 mois pour pouvoir calculer un score (moyenne mobile)
        hist = stock.history(period="1mo") 
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            
            if len(hist) >= 2:
                prev_price = hist['Close'].iloc[-2]
                daily_pct = ((current_price - prev_price) / prev_price) * 100
            
            # Calcul du score (0 à 100) basé sur la position du prix face à sa moyenne mensuelle
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            if pd.notna(sma20) and sma20 > 0:
                # Si le prix est au-dessus de la moyenne, le score monte vers 100, sinon descend vers 0
                raw_score = (current_price / sma20) * 50
                score = int(min(max(raw_score, 0), 100))
        else:
            return None # Impossible de trouver le prix, on ignore
    except Exception:
        return None

    # Nouvelles (ne bloque pas si erreur)
    try:
        raw_news = stock.news
        if raw_news:
            for n in raw_news[:3]:
                title = n.get('title') or n.get('content', {}).get('title') or "Titre indisponible"
                link = n.get('link') or n.get('content', {}).get('clickThroughUrl', {}).get('url') or "#"
                if title != "Titre indisponible":
                    clean_news.append({"title": title, "link": link})
    except Exception:
        pass

    # Trimestre (ne bloque pas si erreur)
    try:
        calendar = stock.get_earnings_dates(limit=1)
        if calendar is not None and not calendar.empty:
            earnings_date = calendar.index[0].strftime("%Y-%m-%d")
    except Exception:
        pass

    return {
        "current_price": current_price,
        "daily_pct": daily_pct,
        "news": clean_news,
        "earnings_date": earnings_date,
        "score": score
    }

# --- INTERFACE PRINCIPALE ---
def show_system2():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    st.title("📈 Suivi Boursier & IA")
    
    tab_view, tab_manage = st.tabs(["📈 Mon Portefeuille", "⚙️ Gérer mes transactions"])
    
    df_trans = load_stock_transactions()
    my_trans = pd.DataFrame()
    if not df_trans.empty:
        my_trans = df_trans[df_trans['owner'] == st.session_state['username']]

    # --- TAB 1: VISUALISER ---
    with tab_view:
        st.subheader("Analyse de performance par titre")
        
        if my_trans.empty:
            st.info("Aucune transaction enregistrée. Va dans l'onglet 'Gérer mes transactions'.")
        else:
            unique_tickers = my_trans['ticker'].unique()
            
            for ticker in unique_tickers:
                ticker_data = my_trans[my_trans['ticker'] == ticker]
                info = get_stock_info(ticker)
                
                # Calcul total en main global pour ce titre
                total_qty = 0
                for _, r in ticker_data.iterrows():
                    q = float(r['quantity'])
                    if r.get('trans_type', 'Achat') == 'Achat': total_qty += q
                    else: total_qty -= q
                
                if info and not ticker_data.empty:
                    c_price = info['current_price']
                    d_pct = info['daily_pct']
                    color = "green" if d_pct >= 0 else "red"
                    arrow = "▲" if d_pct >= 0 else "▼"
                    
                    st.markdown("---")
                    st.markdown(f"### {ticker} | 📦 Total en main : **{total_qty:.2f}** actions")
                    st.markdown(f"Prix actuel : **{c_price:.2f}$** <span style='color:{color}'>({arrow} {d_pct:.2f}%) aujourd'hui</span>", unsafe_allow_html=True)
                    
                    with st.expander(f"📊 Graphiques & Infos pour {ticker}"):
                        # Filtres de dates spécifiques au graphique
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
                            
                            # Si c'est un achat, (Prix Actuel - Prix Achat) / Prix Achat. 
                            # Si c'est une vente, on inverse la logique pour voir si c'était un bon "move" de vendre.
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
                                         color_discrete_map={"Achat": "#1f77b4", "Vente": "#ffbf00"},
                                         title=f"Performance des transactions {ticker}", hover_data=["Qty"])
                            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Aucune transaction trouvée dans cette plage de dates.")
                        
                        # Section Informations (Nouvelles, IA, Score)
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with st.container(border=True):
                                st.markdown("📰 **Actualités**")
                                if info['news']:
                                    for n in info['news']: st.write(f"- [{n['title']}]({n['link']})")
                                else: st.write("Aucune news trouvée.")
                        
                        with col2:
                            with st.container(border=True):
                                st.markdown("🔮 **Analyse IA (Gemini)**")
                                if st.button(f"🧠 Analyser {ticker}", key=f"ai_{ticker}"):
                                    with st.spinner("Réflexion en cours..."):
                                        resultat = get_ai_analysis(ticker, c_price, d_pct)
                                        st.write(resultat)
                        
                        with col3:
                            with st.container(border=True):
                                st.markdown("📈 **Prochain Trimestre**")
                                st.write(f"**Date prévue :** {info['earnings_date']}")
                                st.metric(label="Score technique de confiance", value=f"{info['score']}/100")
                                st.progress(info['score'] / 100)
                                st.caption("Basé sur la moyenne mobile des 20 derniers jours.")

    # --- TAB 2: GÉRER ---
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
                            icon = '🔵' if row.get('trans_type', 'Achat') == 'Achat' else '🟡'
                            st.write(f"{icon} {row.get('trans_type', 'Achat')} | {row['date']} | {row['quantity']} à {row['buy_price']}$")
                            if st.button("Supprimer", key=f"del_{row['id']}"):
                                delete_stock_transaction(row['id'])
                                st.rerun()
        
        st.divider()
        st.subheader("Ajouter un TOUT NOUVEAU titre")
        with st.form("new_stock"):
            t = st.text_input("Symbole (ex: AAPL, CGNT.V)").upper()
            d = st.date_input("Date")
            q = st.number_input("Qté", min_value=0.01, step=1.0)
            p = st.number_input("Prix d'achat ($)", min_value=0.01, step=0.1)
            if st.form_submit_button("Ajouter"):
                if t:
                    add_stock_transaction(st.session_state['username'], t, d, q, p, "Achat")
                    st.rerun()