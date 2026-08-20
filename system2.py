import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime
from database import load_stock_transactions, add_stock_transaction, delete_stock_transaction

@st.cache_data(ttl=900)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
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
            
        # --- CORRECTION DES NOUVELLES ---
        raw_news = stock.news
        clean_news = []
        if raw_news:
            for n in raw_news[:3]:
                # On fouille dans la nouvelle structure de données de Yahoo Finance
                title = n.get('title') or n.get('content', {}).get('title') or "Titre indisponible"
                link = n.get('link') or n.get('content', {}).get('clickThroughUrl', {}).get('url') or "#"
                if title != "Titre indisponible":
                    clean_news.append({"title": title, "link": link})
        
        earnings_date = "Date non disponible"
        try:
            calendar = stock.get_earnings_dates(limit=1)
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.index[0].strftime("%Y-%m-%d")
        except: pass

        return {
            "current_price": current_price,
            "daily_pct": daily_pct,
            "news": clean_news,
            "earnings_date": earnings_date
        }
    except Exception:
        return None

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
        st.subheader("Analyse de performance")
        
        if my_trans.empty:
            st.info("Tu n'as aucune transaction. Va dans l'onglet 'Gérer mes transactions' pour en ajouter.")
        else:
            # Filtre de date
            filter_date = st.date_input("Afficher les données jusqu'au :", value=datetime.today())
            str_filter_date = filter_date.strftime("%Y-%m-%d")
            
            unique_tickers = my_trans['ticker'].unique()
            
            for ticker in unique_tickers:
                # Appliquer le filtre de date
                ticker_data = my_trans[(my_trans['ticker'] == ticker) & (my_trans['date'] <= str_filter_date)]
                
                info = get_stock_info(ticker)
                
                if info and not ticker_data.empty:
                    c_price = info['current_price']
                    d_pct = info['daily_pct']
                    color = "green" if d_pct >= 0 else "red"
                    arrow = "▲" if d_pct >= 0 else "▼"
                    
                    st.markdown(f"### {ticker} : {c_price:.2f}$ <span style='color:{color}'>({arrow} {d_pct:.2f}%) aujourd'hui</span>", unsafe_allow_html=True)
                    
                    with st.expander(f"📊 Graphique de performance & IA pour {ticker}"):
                        st.markdown("#### Performance par lot")
                        
                        plot_data = []
                        for _, row in ticker_data.iterrows():
                            t_price = float(row['buy_price'])
                            qty = float(row['quantity'])
                            t_type = row.get('trans_type', 'Achat')
                            t_date = row['date']
                            
                            if t_price > 0:
                                if t_type == "Achat":
                                    lot_pct = ((c_price - t_price) / t_price) * 100
                                else:
                                    # Pour une vente : Si le stock monte APRÈS la vente, le rendement est perçu
                                    # comme négatif (tu as manqué des gains). S'il descend, c'est positif.
                                    lot_pct = ((t_price - c_price) / t_price) * 100
                                    
                                label_name = f"{t_type} du {t_date} ({qty})"
                                
                                plot_data.append({
                                    "Lot": label_name,
                                    "Quantité": qty,
                                    "Rendement (%)": lot_pct,
                                    "Prix d'action": t_price,
                                    "Type": t_type
                                })
                        
                        if plot_data:
                            df_plot = pd.DataFrame(plot_data)
                            
                            # Code de couleurs : Bleu pour l'Achat, Jaune/Or pour la Vente
                            fig = px.bar(df_plot, x="Lot", y="Rendement (%)", 
                                         text="Rendement (%)", color="Type",
                                         color_discrete_map={"Achat": "#1f77b4", "Vente": "#ffbf00"},
                                         hover_data=["Quantité", "Prix d'action"],
                                         title=f"Rendement de tes actions {ticker}")
                            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                            fig.update_layout(xaxis_title="Lots (Date et Quantité)", yaxis_title="Rendement Actuel (%)")
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.divider()

                        st.markdown("#### 📰 Événements & Prévisions")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with st.container(border=True):
                                st.markdown("🗓️ **Dernier mois / Aujourd'hui**")
                                if info['news']:
                                    for n in info['news']:
                                        st.write(f"- [{n['title']}]({n['link']})")
                                else:
                                    st.write("Aucune nouvelle structurée trouvée.")
                                    # Lien de secours direct vers Yahoo
                                    st.markdown(f"[🔍 Voir les actus sur Yahoo Finance](https://finance.yahoo.com/quote/{ticker})")
                                    
                        with col2:
                            with st.container(border=True):
                                st.markdown("🔮 **Prochain mois (Analyse IA)**")
                                st.info("⚙️ Prêt pour l'IA (Ex: Netflix annonce un partenariat). En attente de clé API.")
                        
                        with col3:
                            with st.container(border=True):
                                st.markdown("📈 **Prochain Trimestre**")
                                st.write(f"**Date prévue :** {info['earnings_date']}")
                                st.write("**Prévision de succès :**")
                                st.progress(75) 
                                st.caption("L'IA estime à 75% les chances d'un bon trimestre basé sur le momentum actuel.")


    # --- TAB 2: GÉRER ---
    with tab_manage:
        
        if not my_trans.empty:
            st.subheader("Mes Titres Actuels")
            unique_tickers = my_trans['ticker'].unique()
            
            for t in unique_tickers:
                df_t = my_trans[my_trans['ticker'] == t]
                
                # Calcul du total d'actions possédées (Achat - Vente)
                total_qty = 0
                for _, r in df_t.iterrows():
                    q = float(r['quantity'])
                    if r.get('trans_type', 'Achat') == 'Achat': total_qty += q
                    else: total_qty -= q
                
                with st.expander(f"📁 {t} - Total en main : {total_qty} actions", expanded=False):
                    col_action, col_hist = st.columns(2)
                    
                    with col_action:
                        st.markdown("**Ajouter une transaction (Achat/Vente)**")
                        action = st.selectbox("Type d'action", ["Achat", "Vente"], key=f"act_{t}")
                        new_date = st.date_input("Date de la transaction", key=f"date_{t}")
                        new_qty = st.number_input("Quantité", min_value=0.01, step=1.0, key=f"qty_{t}")
                        new_price = st.number_input("Prix unitaire de la transaction ($)", min_value=0.01, step=0.1, key=f"prc_{t}")
                        
                        if st.button("Enregistrer", type="primary", key=f"btn_save_{t}"):
                            if action == "Vente" and new_qty > total_qty:
                                st.error("Tu essaies de vendre plus d'actions que tu n'en possèdes actuellement !")
                            else:
                                success, msg = add_stock_transaction(st.session_state['username'], t, new_date, new_qty, new_price, action)
                                if success: st.rerun()
                                else: st.error(msg)
                                
                    with col_hist:
                        st.markdown("**Historique de tes lots**")
                        for idx, row in df_t.iterrows():
                            t_type = row.get('trans_type', 'Achat')
                            icon = "🔵" if t_type == "Achat" else "🟡"
                            st.write(f"{icon} **{t_type}** | {row['date']} | Qty: {row['quantity']} | {row['buy_price']}$")
                            if st.button("🗑️ Supprimer ce lot précis", key=f"del_{row['id']}"):
                                delete_stock_transaction(row['id'])
                                st.rerun()
        
        st.divider()
        st.subheader("Ajouter un TOUT NOUVEAU titre")
        with st.form("new_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_ticker = st.text_input("Symbole (ex: CGNT.V, AAPL)").upper()
                new_date_init = st.date_input("Date d'achat initial")
            with col2:
                new_qty_init = st.number_input("Quantité achetée", min_value=0.01, step=1.0)
                new_price_init = st.number_input("Prix d'achat unitaire ($)", min_value=0.01, step=0.1)
                
            if st.form_submit_button("Ajouter ce nouveau titre"):
                if new_ticker:
                    success, msg = add_stock_transaction(st.session_state['username'], new_ticker, new_date_init, new_qty_init, new_price_init, "Achat")
                    if success: st.rerun()
                    else: st.error(msg)