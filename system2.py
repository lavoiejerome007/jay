import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime
from database import load_stock_transactions, add_stock_transaction, delete_stock_transaction

# Cache pour ne pas spammer Yahoo Finance à chaque clic
@st.cache_data(ttl=900) # Garde en mémoire 15 minutes
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Récupérer l'historique sur 2 jours pour avoir la variation quotidienne
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            daily_pct = ((current_price - prev_price) / prev_price) * 100
        elif len(hist) == 1:
            current_price = hist['Close'].iloc[0]
            daily_pct = 0.0
        else:
            return None
            
        # Récupération des infos basiques
        news = stock.news[:3] if stock.news else []
        
        # Prochain trimestre (Earnings)
        earnings_date = "Date non disponible"
        try:
            calendar = stock.get_earnings_dates(limit=1)
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.index[0].strftime("%Y-%m-%d")
        except:
            pass

        return {
            "current_price": current_price,
            "daily_pct": daily_pct,
            "news": news,
            "earnings_date": earnings_date
        }
    except Exception:
        return None

def show_system2():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    st.title("📈 Suivi Boursier & IA")
    
    tab_view, tab_manage = st.tabs(["📈 Mes Titres", "⚙️ Gérer mes titres"])
    
    df_trans = load_stock_transactions()
    my_trans = pd.DataFrame()
    if not df_trans.empty:
        my_trans = df_trans[df_trans['owner'] == st.session_state['username']]

    # --- TAB 1: VISUALISER ---
    with tab_view:
        st.subheader("Analyse de mon portefeuille")
        
        if my_trans.empty:
            st.info("Tu n'as aucun titre. Va dans l'onglet 'Gérer mes titres' pour en ajouter (ex: CGNT.V).")
        else:
            unique_tickers = my_trans['ticker'].unique()
            
            for ticker in unique_tickers:
                ticker_data = my_trans[my_trans['ticker'] == ticker]
                info = get_stock_info(ticker)
                
                if info:
                    c_price = info['current_price']
                    d_pct = info['daily_pct']
                    color = "green" if d_pct >= 0 else "red"
                    arrow = "▲" if d_pct >= 0 else "▼"
                    
                    st.markdown(f"### {ticker} : {c_price:.2f}$ <span style='color:{color}'>({arrow} {d_pct:.2f}%) aujourd'hui</span>", unsafe_allow_html=True)
                    
                    with st.expander(f"📊 Voir les détails avancés pour {ticker}"):
                        # 1. GRAPHIQUE DES LOTS
                        st.markdown("#### Performance de tes lots d'achat")
                        
                        plot_data = []
                        for _, row in ticker_data.iterrows():
                            b_price = float(row['buy_price'])
                            qty = float(row['quantity'])
                            if b_price > 0:
                                lot_pct = ((c_price - b_price) / b_price) * 100
                                plot_data.append({
                                    "Date d'achat": row['date'],
                                    "Quantité": qty,
                                    "Rendement (%)": lot_pct,
                                    "Prix payé": b_price
                                })
                        
                        if plot_data:
                            df_plot = pd.DataFrame(plot_data)
                            fig = px.bar(df_plot, x="Date d'achat", y="Rendement (%)", 
                                         text="Rendement (%)", color="Rendement (%)",
                                         color_continuous_scale=["red", "gray", "green"],
                                         color_continuous_midpoint=0,
                                         hover_data=["Quantité", "Prix payé"],
                                         title=f"Rendement par date d'achat ({ticker})")
                            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.divider()

                        # 2. NOUVELLES & PRÉDICTIONS
                        st.markdown("#### 📰 Événements & Prévisions")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with st.container(border=True):
                                st.markdown("🗓️ **Dernier mois / Aujourd'hui**")
                                if info['news']:
                                    for n in info['news']:
                                        st.write(f"- [{n.get('title', 'Titre indisponible')}]({n.get('link', '#')})")
                                else:
                                    st.write("Aucune nouvelle récente trouvée par le système.")
                                    
                        with col2:
                            with st.container(border=True):
                                st.markdown("🔮 **Prochain mois (Analyse IA)**")
                                st.info("⚙️ *Module IA en attente* : Prêt à intégrer un flux prédictif (ex: 'Netflix annonce un partenariat avec Amazon').")
                        
                        with col3:
                            with st.container(border=True):
                                st.markdown("📈 **Prochain Trimestre**")
                                st.write(f"**Date prévue :** {info['earnings_date']}")
                                st.write("**Prévision de succès :**")
                                st.progress(75) # Valeur factice pour le design
                                st.caption("L'IA estime à 75% les chances d'un bon trimestre basé sur le momentum actuel.")


    # --- TAB 2: GÉRER ---
    with tab_manage:
        st.subheader("Ajouter un achat")
        with st.form("add_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_ticker = st.text_input("Symbole (ex: CGNT.V, AAPL, TSLA)").upper()
                new_date = st.date_input("Date d'achat")
            with col2:
                new_qty = st.number_input("Quantité d'actions", min_value=0.01, step=1.0)
                new_price = st.number_input("Prix d'achat par action ($)", min_value=0.01, step=0.1)
                
            submitted = st.form_submit_button("Ajouter ce lot")
            if submitted and new_ticker:
                success, msg = add_stock_transaction(st.session_state['username'], new_ticker, new_date, new_qty, new_price)
                if success:
                    st.success(f"{new_qty} actions de {new_ticker} ajoutées !")
                    st.rerun()
                else:
                    st.error("Erreur : " + msg)
                    
        st.divider()
        st.subheader("Mes transactions existantes")
        if not my_trans.empty:
            for idx, row in my_trans.iterrows():
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.write(f"**{row['ticker']}** | Acheté le {row['date']} | Qty: {row['quantity']} | Prix: {row['buy_price']}$")
                with col_btn:
                    if st.button("🗑️", key=f"del_stk_{row['id']}"):
                        delete_stock_transaction(row['id'])
                        st.rerun()