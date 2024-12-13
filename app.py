import streamlit as st
import pandas as pd
import io

def validate_csv(df):
    expected_columns = [
        'Paese',
        '% IVA applicata',  # Modificato da '$ IVA applicata'
        'Rate Name',
        'Totale vendite lordo',
        'Totale netto prodotti',
        'Totale netto spedizioni',
        'Totale IVA prodotti',
        'Totale IVA spedizioni',
        'Totale IVA'
    ]
    return list(df.columns) == expected_columns

def process_csv(df):
    # Rimuove la colonna Rate Name
    df = df.drop('Rate Name', axis=1)
    
    # Gestisce i numeri convertendo le virgole in punti
    numeric_columns = [
        'Totale vendite lordo',
        'Totale netto prodotti',
        'Totale netto spedizioni',
        'Totale IVA prodotti',
        'Totale IVA spedizioni',
        'Totale IVA'
    ]
    
    for col in numeric_columns:
        df[col] = df[col].str.replace(',', '.').astype(float)
    
    # Raggruppa per paese e calcola le somme
    grouped = df.groupby('Paese').agg({
        '% IVA applicata': 'first',  # Prende solo il primo valore
        'Totale vendite lordo': 'sum',
        'Totale netto prodotti': 'sum',
        'Totale netto spedizioni': 'sum',
        'Totale IVA prodotti': 'sum',
        'Totale IVA spedizioni': 'sum',
        'Totale IVA': 'sum'
    }).reset_index()
    
    # Formatta i numeri con la virgola come separatore decimale
    for col in numeric_columns:
        grouped[col] = grouped[col].round(2).apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    return grouped

# Configurazione della pagina
st.set_page_config(page_title="Processore CSV Vendite", layout="wide")

# Titolo dell'applicazione
st.title("Processore CSV Vendite")

# Istruzioni
st.write("""
### Istruzioni:
1. Carica un file CSV che usa ';' come separatore
2. Il file deve contenere le seguenti colonne:
   - Paese
   - % IVA applicata
   - Rate Name
   - Totale vendite lordo
   - Totale netto prodotti
   - Totale netto spedizioni
   - Totale IVA prodotti
   - Totale IVA spedizioni
   - Totale IVA
""")

# Upload del file
uploaded_file = st.file_uploader("Carica il tuo file CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # Legge il file CSV
        df = pd.read_csv(uploaded_file, sep=';')
        
        # Valida la struttura del CSV
        if not validate_csv(df):
            st.error(f"Le colonne del CSV non corrispondono al formato atteso!\nColonne trovate: {list(df.columns)}\nColonne attese: {expected_columns}")
        else:
            # Processa il file
            result_df = process_csv(df)
            
            # Mostra i risultati
            st.success("File elaborato con successo!")
            st.write("### Risultati:")
            st.dataframe(result_df)
            
            # Prepara il file per il download
            csv = result_df.to_csv(sep=';', index=False)
            st.download_button(
                label="Scarica il file elaborato",
                data=csv,
                file_name="risultati_elaborati.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'elaborazione: {str(e)}")
