import streamlit as st
import pandas as pd

def clean_excel(file):
    # Charger le fichier Excel
    df = pd.read_excel(file)

    # Supprimer les doublons basés sur 'Shift Code'
    if 'Shift Code' in df.columns:
        df = df.drop_duplicates(subset=['Shift Code'])

    # Supprimer les lignes où 'Printing Location' ne contient pas Schenk ou Jongeneel (insensible à la casse)
    if 'Printing Location' in df.columns:
        mask = df['Printing Location'].str.contains('Schenk|Jongeneel', case=False, na=False)
        df = df[mask]

        # Remplacer 'Ge Simons' par 'Schenk Papendrecht'
        df['Printing Location'] = df['Printing Location'].str.replace(
            r'(?i)Ge Simons', 'Schenk Papendrecht', regex=True
        )

    # Créer nouvelles colonnes pour Start Date, Start Time, End Date, End Time
    for col in ['Start Date', 'End Date']:
        if col in df.columns:
            # Convertir en datetime si ce n’est pas déjà fait
            df[col] = pd.to_datetime(df[col], errors='coerce')

            # Créer les colonnes Date et Time
            df[f'{col} Only Date'] = df[col].dt.date
            df[f'{col} Only Time'] = df[col].dt.time

    # Supprimer les lignes où 'Tractor' contient 'SR-ALFI-LIN'
    if 'Tractor' in df.columns:
        df = df[~df['Tractor'].str.contains('SR-ALFI-LIN', na=False)]

    # Remplacer les vides dans 'trailer' par 'Operation maintenance'
    if 'trailer' in df.columns:
        df['trailer'] = df['trailer'].fillna('Operation maintenance')

    return df

st.title("Self-billing")

uploaded_file = st.file_uploader("Uploader un fichier XLSX", type=['xlsx'])

if uploaded_file:
    cleaned_df = clean_excel(uploaded_file)
    st.write("Aperçu du fichier nettoyé :")
    st.dataframe(cleaned_df)

    # Bouton pour télécharger le fichier nettoyé
    @st.cache_data
    def convert_df(df):
        return df.to_excel(index=False, engine='openpyxl')

    output = convert_df(cleaned_df)

    st.download_button(
        label="Télécharger le fichier nettoyé",
        data=output,
        file_name='fichier_nettoye.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
