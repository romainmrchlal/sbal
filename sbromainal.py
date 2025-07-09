import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Self-billing AL")

uploaded_file = st.file_uploader("Uploader un fichier XLSX", type=['xlsx'])

if uploaded_file:
    # Lire le fichier
    df = pd.read_excel(uploaded_file)

    if 'Printing Location' in df.columns:
        unique_locations = sorted(df['Printing Location'].dropna().unique())

        # Expander + multiselect
        with st.expander("Sélectionnez les marques à GARDER"):
            brands_to_keep = st.multiselect(
                "Marques disponibles :",
                options=unique_locations
            )

        # Bouton pour lancer le nettoyage
        if st.button("✅ Nettoyer le fichier"):
            if not brands_to_keep:
                st.warning("Veuillez sélectionner au moins une marque.")
            else:
                def clean_excel(df, brands_to_keep):
                    # Supprimer doublons Shift Code
                    if 'Shift Code' in df.columns:
                        df = df.drop_duplicates(subset=['Shift Code'])

                    # Filtrer Printing Location
                    pattern = '|'.join(brands_to_keep)
                    mask = df['Printing Location'].str.contains(pattern, case=False, na=False)
                    df = df[mask]

                    # Remplacer Ge Simons par Schenk Papendrecht
                    df['Printing Location'] = df['Printing Location'].str.replace(
                        r'(?i)Ge Simons', 'Schenk Papendrecht', regex=True
                    )

                    # Colonnes Date / Time
                    for col in ['Start Date', 'End Date']:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            df[f'{col} Only Date'] = df[col].dt.date
                            df[f'{col} Only Time'] = df[col].dt.time

                    # Supprimer lignes SR-ALFI-LIN
                    if 'Tractor' in df.columns:
                        df = df[~df['Tractor'].str.contains('SR-ALFI-LIN', na=False)]

                    # trailer vides → Operation maintenance
                    if 'trailer' in df.columns:
                        df['trailer'] = df['trailer'].fillna('Operation maintenance')

                    return df

                cleaned_df = clean_excel(df, brands_to_keep)

                st.success("✅ Fichier nettoyé :")
                st.dataframe(cleaned_df)

                # ✅ Nouvelle version correcte : Excel → BytesIO
                @st.cache_data
                def convert_df(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    output.seek(0)
                    return output

                output = convert_df(cleaned_df)

                st.download_button(
                    label="📥 Télécharger le fichier nettoyé",
                    data=output,
                    file_name='fichier_nettoye.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    else:
        st.error("❌ La colonne 'Printing Location' est introuvable dans le fichier.")
