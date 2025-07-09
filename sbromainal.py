import streamlit as st
import pandas as pd

def clean_excel(file, brands_to_keep):
    # Charger le fichier Excel
    df = pd.read_excel(file)

    # Supprimer doublons basés sur Shift Code
    if 'Shift Code' in df.columns:
        df = df.drop_duplicates(subset=['Shift Code'])

    # Filtrer Printing Location selon marques choisies
    if 'Printing Location' in df.columns:
        pattern = '|'.join(brands_to_keep)
        mask = df['Printing Location'].str.contains(pattern, case=False, na=False)
        df = df[mask]

        # Remplacer Ge Simons par Schenk Papendrecht
        df['Printing Location'] = df['Printing Location'].str.replace(
            r'(?i)Ge Simons', 'Schenk Papendrecht', regex=True
        )

    # Créer colonnes Date/Time séparées
    for col in ['Start Date', 'End Date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[f'{col} Only Date'] = df[col].dt.date
            df[f'{col} Only Time'] = df[col].dt.time

    # Supprimer lignes avec SR-ALFI-LIN dans Tractor
    if 'Tractor' in df.columns:
        df = df[~df['Tractor'].str.contains('SR-ALFI-LIN', na=False)]

    # Remplacer vides dans trailer par Operation maintenance
    if 'trailer' in df.columns:
        df['trailer'] = df['trailer'].fillna('Operation maintenance')

    return df

st.title("Nettoyage de fichier XLSX")

uploaded_file = st.file_uploader("Uploader un fichier XLSX", type=['xlsx'])

# ✅ Zone de sélection dynamique
brands_default = ["Schenk", "Jongeneel"]
brands_to_keep = st.multiselect(
    "Marques à garder dans Printing Location :",
    options=["Schenk", "Jongeneel", "AutreMarque1", "AutreMarque2"],
    default=brands_default
)

if uploaded_file and brands_to_keep:
    cleaned_df = clean_excel(uploaded_file, brands_to_keep)
    st.write("Aperçu du fichier nettoyé :")
    st.dataframe(cleaned_df)

    # Bouton pour télécharger
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
