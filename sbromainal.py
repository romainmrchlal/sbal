import streamlit as st
import pandas as pd

st.title("Self-billing AL")

uploaded_file = st.file_uploader("Uploader un fichier XLSX", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'Printing Location' in df.columns:
        unique_locations = sorted(df['Printing Location'].dropna().unique())

        st.subheader("👉 Cochez les marques à GARDER")

        # ✅ FORM pour valider d'un coup
        with st.form("filter_form"):
            selected_brands = []
            for location in unique_locations:
                if st.checkbox(location, value=False):
                    selected_brands.append(location)

            submit_button = st.form_submit_button("✅ Appliquer le filtre")

        if submit_button:
            if not selected_brands:
                st.warning("Veuillez cocher au moins une marque.")
            else:
                # Appliquer le nettoyage
                def clean_excel(df, brands_to_keep):
                    if 'Shift Code' in df.columns:
                        df = df.drop_duplicates(subset=['Shift Code'])

                    pattern = '|'.join(brands_to_keep)
                    mask = df['Printing Location'].str.contains(pattern, case=False, na=False)
                    df = df[mask]

                    df['Printing Location'] = df['Printing Location'].str.replace(
                        r'(?i)Ge Simons', 'Schenk Papendrecht', regex=True
                    )

                    for col in ['Start Date', 'End Date']:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            df[f'{col} Only Date'] = df[col].dt.date
                            df[f'{col} Only Time'] = df[col].dt.time

                    if 'Tractor' in df.columns:
                        df = df[~df['Tractor'].str.contains('SR-ALFI-LIN', na=False)]

                    if 'trailer' in df.columns:
                        df['trailer'] = df['trailer'].fillna('Operation maintenance')

                    return df

                cleaned_df = clean_excel(df, selected_brands)

                st.success("✅ Fichier nettoyé :")
                st.dataframe(cleaned_df)

                @st.cache_data
                def convert_df(df):
                    return df.to_excel(index=False, engine='openpyxl')

                output = convert_df(cleaned_df)

                st.download_button(
                    label="📥 Télécharger le fichier nettoyé",
                    data=output,
                    file_name='fichier_nettoye.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    else:
        st.error("❌ La colonne 'Printing Location' est introuvable dans le fichier.")
