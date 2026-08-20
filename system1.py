import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    get_gsheet_client, get_or_create_worksheet, file_to_base64,
    load_fit_items, load_fit_ratings, batch_update_fit_items,
    delete_fit_item, update_collection_recipients, delete_full_collection
)

def show_system1():
    if st.button("← Retour au tableau de bord"):
        st.session_state["current_page"] = "Accueil"
        st.rerun()
        
    st.title("👕 Fit-Note")
    
    tab_view, tab_rate, tab_add, tab_items, tab_collections = st.tabs(["👁️ Visualiser", "⭐ Noter", "➕ Ajouter", "👕 Pièces", "📁 Collections"])
    
    client = get_gsheet_client()
    items_df = load_fit_items()
    ratings_df = load_fit_ratings()

    # --- TAB AJOUTER ---
    with tab_add:
        st.subheader("Ajouter une pièce de linge")
        item_type = st.selectbox("Type de vêtement", ["Chandail (Haut)", "Pantalon (Bas)"])
        
        existing_cols = []
        if not items_df.empty:
            user_items_for_cols = items_df[items_df['owner'] == st.session_state['username']]
            existing_cols = sorted([c for c in user_items_for_cols['collection'].unique() if c.strip() != ""])
        
        col_choice_options = ["-- Aucune / Nouvelle collection --"] + existing_cols
        selected_col_option = st.selectbox("Sélectionner une collection existante", col_choice_options)
        
        if selected_col_option == "-- Aucune / Nouvelle collection --":
            item_col = st.text_input("Ou nom de la nouvelle collection")
        else:
            item_col = selected_col_option
            
        recipient = st.text_input("Partager avec (nom d'utilisateur, séparé par des virgules) :")
        item_file = st.file_uploader("📸 Image", type=["png", "jpg", "jpeg"], key="item_up")
        
        if st.button("Sauvegarder l'item"):
            if item_file and client:
                with st.spinner("Traitement..."):
                    img_b64 = file_to_base64(item_file)
                    type_val = "shirt" if "Chandail" in item_type else "pants"
                    col_normalized = item_col.strip().capitalize() if item_col else ""
                    new_id = int(datetime.now().timestamp())
                    
                    sheet_items = get_or_create_worksheet(client, "FitItems", ['id', 'owner', 'recipient', 'type', 'image_url', 'collection'])
                    sheet_items.append_row([str(new_id), st.session_state['username'], recipient.strip(), type_val, img_b64, col_normalized])
                    st.success("Enregistré !")
                    st.rerun()
            else:
                st.warning("Fichier manquant ou problème de connexion.")

    # --- TAB PIÈCES (AVEC BOUTON DE SAUVEGARDE GLOBALE) ---
    with tab_items:
        st.subheader("Gérer mes pièces de linge")
        if not items_df.empty:
            my_items = items_df[items_df['owner'] == st.session_state['username']]
            
            st.info("💡 Modifie tes collections et partages ci-dessous, puis clique sur ce bouton pour tout enregistrer d'un coup.")
            if st.button("💾 TOUT ENREGISTRER", type="primary", use_container_width=True):
                with st.spinner("Mise à jour globale en cours..."):
                    updates = []
                    for idx, row in my_items.iterrows():
                        item_id = row['id']
                        new_col = st.session_state.get(f"batch_col_{item_id}", row.get('collection', '')).strip().capitalize()
                        new_recip = st.session_state.get(f"batch_recip_{item_id}", row.get('recipient', '')).strip()
                        updates.append((item_id, new_recip, new_col))
                        
                    success, msg = batch_update_fit_items(updates)
                    if success:
                        st.success("Toutes les modifications ont été enregistrées !")
                        st.rerun()
                    else:
                        st.error(f"Erreur: {msg}")
            
            st.divider()

            for idx, row in my_items.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if row['image_url']: st.image(row['image_url'], width=150)
                    with col2:
                        st.write(f"**Type:** {'Chandail' if row['type'] == 'shirt' else 'Pantalon'}")
                        # On utilise les clés de session pour la sauvegarde par lot
                        st.text_input("Collection", value=row.get('collection', ''), key=f"batch_col_{row['id']}")
                        st.text_input("Partagé avec", value=row.get('recipient', ''), key=f"batch_recip_{row['id']}")
                        
                        if st.button("🗑️ Supprimer", key=f"del_{row['id']}"):
                            delete_fit_item(row['id'])
                            st.rerun()

    # --- TAB COLLECTIONS ---
    with tab_collections:
        st.subheader("Gérer mes collections")
        if not items_df.empty:
            my_items = items_df[items_df['owner'] == st.session_state['username']]
            my_collections = my_items[my_items['collection'].str.strip() != '']['collection'].unique()
            
            for col_name in my_collections:
                st.markdown(f"### 📁 Collection : {col_name}")
                col_items = my_items[my_items['collection'] == col_name]
                
                with st.expander(f"⚙️ Actions pour la collection '{col_name}'"):
                    new_col_recip = st.text_input("Partager avec :", key=f"share_col_{col_name}")
                    if st.button("Appliquer", key=f"btn_share_{col_name}"):
                        update_collection_recipients(col_name, st.session_state['username'], new_col_recip)
                        st.rerun()
                    if st.button("🚨 Supprimer la collection complète", key=f"btn_del_col_{col_name}"):
                        delete_full_collection(col_name, st.session_state['username'])
                        st.rerun()
                
                for idx, row in col_items.iterrows():
                    colA, colB = st.columns([1, 4])
                    with colA:
                        if row['image_url']: st.image(row['image_url'], width=80)
                    with colB:
                        st.write(f"**{'Chandail' if row['type'] == 'shirt' else 'Pantalon'}**")
                        if st.button("Retirer", key=f"rm_col_{row['id']}"):
                            batch_update_fit_items([(row['id'], row['recipient'], "")])
                            st.rerun()
                st.divider()

    # --- TAB VISUALISER ---
    with tab_view:
        st.subheader("Mes combinaisons")
        if not items_df.empty:
            my_items = items_df[items_df['owner'] == st.session_state['username']]
            unique_collections = sorted([c for c in my_items['collection'].unique() if c.strip() != ""])
            
            if "selected_tag_filter" not in st.session_state:
                st.session_state["selected_tag_filter"] = "Tous"
            
            st.markdown("**Filtrer par collection :**")
            cols_tag = st.columns(len(unique_collections) + 1)
            with cols_tag[0]:
                if st.button("🌟 Tous", use_container_width=True):
                    st.session_state["selected_tag_filter"] = "Tous"
            for idx, c_tag in enumerate(unique_collections):
                with cols_tag[idx + 1]:
                    if st.button(f"🏷️ {c_tag}", use_container_width=True, key=f"tag_btn_{c_tag}"):
                        st.session_state["selected_tag_filter"] = c_tag
            
            st.write("")
            all_my_cols = my_items['collection'].unique()
            
            for col_name in all_my_cols:
                display_name = col_name if str(col_name).strip() != "" else "Général (Sans collection)"
                current_filter = st.session_state["selected_tag_filter"]
                
                if current_filter != "Tous" and display_name != current_filter:
                    continue
                    
                col_items = my_items[my_items['collection'] == col_name]
                shirts = col_items[col_items['type'] == 'shirt'].to_dict('records')
                pants = col_items[col_items['type'] == 'pants'].to_dict('records')
                
                if shirts and pants:
                    st.markdown(f"### 📁 {display_name}")
                    for s in shirts:
                        for p in pants:
                            combo_id = f"S{s['id']}_P{p['id']}"
                            combo_ratings = ratings_df[ratings_df['combo_id'] == combo_id] if not ratings_df.empty else pd.DataFrame()
                                
                            if not combo_ratings.empty:
                                avg = pd.to_numeric(combo_ratings['rating'], errors='coerce').mean()
                                rating_txt = f"⭐ Note moyenne des partages : **{avg:.1f}/100** ({len(combo_ratings)} avis)"
                            else:
                                rating_txt = "⭐ Note : **Aucune note reçue**"

                            with st.container(border=True):
                                if s['image_url']: st.image(s['image_url'], width=350)
                                if p['image_url']: st.image(p['image_url'], width=350)
                                st.markdown(rating_txt)
                                if not combo_ratings.empty:
                                    for _, r in combo_ratings.iterrows():
                                        if str(r['notes']).strip():
                                            st.caption(f"💬 `{r['rater']}` : *{r['notes']}*")
                    st.write("")

    # --- TAB NOTER ---
    with tab_rate:
        st.subheader("🗄️ Archive des partages (Noter)")
        st.write("Ici apparaissent les combinaisons des vêtements qui t'ont été partagés (ou partagés à toi-même).")
        
        if not items_df.empty:
            shared_with_me = items_df[items_df['recipient'].str.contains(st.session_state['username'], na=False)]
            
            if shared_with_me.empty:
                st.info("Aucun vêtement ne t'a été partagé pour le moment.")
            else:
                unique_owners = shared_with_me['owner'].unique()
                for owner in unique_owners:
                    st.markdown(f"#### 👤 Vestiaire de `{owner}`")
                    owner_items = shared_with_me[shared_with_me['owner'] == owner]
                    
                    shirts = owner_items[owner_items['type'] == 'shirt'].to_dict('records')
                    pants = owner_items[owner_items['type'] == 'pants'].to_dict('records')
                    
                    if not shirts or not pants: continue
                        
                    for s in shirts:
                        for p in pants:
                            combo_id = f"S{s['id']}_P{p['id']}"
                            my_rate_row = pd.DataFrame()
                            if not ratings_df.empty:
                                my_rate_row = ratings_df[(ratings_df['combo_id'] == combo_id) & (ratings_df['rater'] == st.session_state['username'])]
                                
                            if not my_rate_row.empty:
                                current_rate = int(pd.to_numeric(my_rate_row.iloc[0]['rating'], errors='coerce'))
                                current_note = str(my_rate_row.iloc[0]['notes'])
                            else:
                                current_rate, current_note = 0, ""

                            with st.expander(f"Combinaison de {owner}"):
                                if s['image_url']: st.image(s['image_url'], width=300)
                                if p['image_url']: st.image(p['image_url'], width=300)
                                    
                                new_rating = st.number_input("Ma note /100", min_value=0, max_value=100, value=current_rate, key=f"rate_{combo_id}")
                                new_note = st.text_input("Mon commentaire", value=current_note, key=f"note_{combo_id}")
                                
                                if st.button("Enregistrer ma note", key=f"save_{combo_id}"):
                                    if client:
                                        sheet_ratings = get_or_create_worksheet(client, "FitRatings", ['combo_id', 'rater', 'rating', 'notes'])
                                        rows = sheet_ratings.get_all_values()
                                        headers = rows[0]
                                        
                                        try: c_i, r_i, rat_i, n_i = headers.index('combo_id'), headers.index('rater'), headers.index('rating'), headers.index('notes')
                                        except ValueError: c_i, r_i, rat_i, n_i = 0, 1, 2, 3
                                            
                                        found_row = None
                                        for idx, r in enumerate(rows[1:], start=2):
                                            while len(r) < len(headers): r.append("")
                                            if r[c_i] == combo_id and r[r_i] == st.session_state['username']:
                                                found_row = idx
                                                break
                                        
                                        if found_row:
                                            sheet_ratings.update_cell(found_row, rat_i + 1, str(new_rating))
                                            sheet_ratings.update_cell(found_row, n_i + 1, str(new_note))
                                        else:
                                            new_r = [""] * len(headers)
                                            new_r[c_i], new_r[r_i], new_r[rat_i], new_r[n_i] = combo_id, st.session_state['username'], str(new_rating), str(new_note)
                                            sheet_ratings.append_row(new_r)
                                            
                                        st.success("Note sauvegardée !")
                                        st.rerun()