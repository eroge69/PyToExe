import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io
import base64
from datetime import datetime

def search_travel(destination, date_start, date_end):
    return [
        {"Type": "Vol", "De": "Genève", "Vers": destination, "Date": str(date_start), "Prix": 320, "CO2 (kg)": 220},
        {"Type": "Hôtel", "Ville": destination, "Dates": f"{date_start} → {date_end}", "Prix/Nuit": 140, "CO2 (kg)": 35},
    ]

def extract_text_from_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Erreur OCR : {e}"

def run_app():
    st.title("4T-Hub — Smart Travel. Real Impact.")
    st.sidebar.image("https://i.imgur.com/F28w3Ac.png", width=180)
    menu = ["Recherche de voyages", "Soumettre un reçu", "Dashboard dépenses & CO₂"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Recherche de voyages":
        st.subheader("Recherche de vols et hôtels")
        dest = st.text_input("Destination", "Paris")
        date_start = st.date_input("Date de départ", datetime.today())
        date_end = st.date_input("Date de retour", datetime.today())
        if st.button("Lancer la recherche"):
            results = search_travel(dest, date_start, date_end)
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)

    elif choice == "Soumettre un reçu":
        st.subheader("Téléversement d'un reçu")
        uploaded_file = st.file_uploader("Choisissez une image ou un PDF", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, width=300)
            with st.spinner("Lecture du reçu..."):
                text = extract_text_from_image(uploaded_file)
                st.text_area("Contenu OCR extrait :", text, height=200)
                if st.button("Ajouter au tableau de dépenses"):
                    st.session_state.setdefault("expenses", []).append({
                        "Date": str(datetime.today().date()),
                        "Montant estimé": "À vérifier",
                        "Détails OCR": text[:200]
                    })
                    st.success("Reçu ajouté.")

    elif choice == "Dashboard dépenses & CO₂":
        st.subheader("Vue d'ensemble des dépenses & CO₂")
        expenses = st.session_state.get("expenses", [])
        if expenses:
            df_exp = pd.DataFrame(expenses)
            st.dataframe(df_exp)

            st.markdown("#### Export Excel")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_exp.to_excel(writer, index=False, sheet_name="Dépenses")
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="depenses_4T-Hub.xlsx">Télécharger le fichier Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("Aucune donnée pour le moment.")

if __name__ == "__main__":
    run_app()
