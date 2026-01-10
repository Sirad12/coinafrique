import streamlit as st
import pandas as pd
import plotly.express as px
import requests 
from bs4 import BeautifulSoup

st.set_page_config(page_title="CoinAfrique App", layout="wide")


menu = st.sidebar.selectbox( 
    "Menu",
    ["Accueil", "Scraping", "Téléchargement brut", "Dashboard", "Évaluation"] 
)

# ---------------- ACCUEIL ----------------
if menu == "Accueil":
    st.title("📊 Application CoinAfrique")
    st.markdown("""
    ## 📌 Projet CoinAfrique – Data Collection & Analyse

    Cette application permet :
    - 📥 de visualiser les données collectées sur CoinAfrique 
    - 🧹 de scraper et nettoyer les données avec BeautifulSoup 
    - 🧾 de télécharger les données brutes via Web Scraper 
    - 📊 d’analyser les prix des annonces (données nettoyées) 
    - 📝 de recueillir l’avis des utilisateurs via un formulaire KoboToolbox 
    """)


# ---------------- SCRAPING ----------------
elif menu == "Scraping":

    st.title("🧹 Scraping des annonces")

    urls = {
        "Vêtements homme": "https://sn.coinafrique.com/categorie/vetements-homme",
        "Chaussures homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
        "Vêtements enfants": "https://sn.coinafrique.com/categorie/vetements-enfants",
        "Chaussures enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants"
    }

    categorie = st.selectbox("Choisir une catégorie", list(urls.keys()))
    nb_pages = st.number_input("Nombre de pages", min_value=1, max_value=10, value=3)

    if st.button("Scraper"):
        df = pd.DataFrame()

        with st.spinner("Scraping en cours..."):
            for page in range(1, nb_pages + 1):
                url = f"{urls[categorie]}?page={page}"
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")

                containers = soup.find_all("div", class_="col s6 m4 l3")
                data = []

                for c in containers:
                    try:
                        titre = c.find("p", class_="ad__card-description").text.strip()
                        
                        prix = c.find("p", class_="ad__card-price").text
                        prix = prix.replace("CFA", "").replace(" ", "").strip()
                        prix = int(prix)

                        adresse = c.find("p", class_="ad__card-location").span.text.strip()
                        
                        image = c.find("img", class_="ad__card-img")["src"]

                        d = {
                            "titre": titre,
                            "prix": prix,
                            "adresse": adresse,
                            "image": image
                        }
                        data.append(d)
                    except:
                        pass

                DF = pd.DataFrame(data)
                df = pd.concat([df, DF], axis=0).reset_index(drop=True)

        st.success("Scraping terminé ✅")
        st.dataframe(df)

        st.download_button(
            "📥 Télécharger le CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="coinafrique_scraped.csv",
            mime="text/csv"
        )


# ---------------- TÉLÉCHARGEMENT BRUT ----------------
elif menu == "Téléchargement brut": 
    st.title("📦 Données brutes issues de Web Scraper") 
    st.markdown("""Ces données ont été extraites sans nettoyage via l'outil Web Scraper.""")
    st.markdown("""
    - [Vêtements homme](https://sn.coinafrique.com/categorie/vetements-homme)  
    - [Chaussures homme](https://sn.coinafrique.com/categorie/chaussures-homme)  
    - [Vêtements enfants](https://sn.coinafrique.com/categorie/vetements-enfants)  
    - [Chaussures enfants](https://sn.coinafrique.com/categorie/chaussures-enfants)  
    """) 
    st.markdown("📥 Tu peux aussi télécharger le fichier brut exporté depuis Web Scraper :") 
    with open("data/coinafrique.csv", "rb") as f: 
        st.download_button("Télécharger le fichier brut", f, file_name="coinafrique.csv") 


# ---------------- DASHBOARD (NETTOYÉ) ----------------
elif menu == "Dashboard":
    st.markdown("## 📊 Dashboard des données nettoyées")

    # --- Chargement et nettoyage ---
    df = pd.read_csv("data/coinafrique.csv")

    # Nettoyage du prix
    df["prix"] = (
        df["prix"].astype(str)
        .str.replace("CFA", "")
        .str.replace(" ", "")
        .str.strip()
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

    # Suppression des valeurs aberrantes (ex. > 1 million FCFA)
    df = df[df["prix"] < 1_000_000]

    # Colonnes utiles
    colonnes_utiles = [col for col in ["titre", "prix", "adresse", "image"] if col in df.columns]
    df = df[colonnes_utiles].dropna()

    # --- Aperçu rapide ---
    st.markdown("### 🔍 Aperçu des annonces")
    st.dataframe(df.head())

    # Bouton de téléchargement
    st.download_button(
        "📥 Télécharger les données nettoyées",
        df.to_csv(index=False).encode("utf-8"),
        file_name="coinafrique_nettoye.csv",
        mime="text/csv"
    )

    # --- Indicateurs clés ---
    st.markdown("### 📌 Indicateurs clés")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("📦 Nombre d'annonces", len(df))
    col3.metric("📍 Villes uniques", df["adresse"].nunique())

    # --- Graphique 1 : Histogramme des prix ---
    st.markdown("### 📊 Distribution des prix")
    fig1 = px.histogram(
    df, x="prix", nbins=30,
    color_discrete_sequence=["#FF7F50"],
    title="Répartition des prix des annonces"
    )
    fig1.update_layout(bargap=0.2)  # 0.2 = 20% d’espace entre les barres
    st.plotly_chart(fig1, use_container_width=True)


    # --- Graphique 2 : Annonces par ville ---
    st.markdown("### 🗺️ Annonces par ville")
    if not df.empty and "adresse" in df.columns:
        ville_counts = df["adresse"].value_counts().reset_index()
        ville_counts.columns = ["Ville", "Nombre d'annonces"]

        fig2 = px.bar(
            ville_counts, x="Ville", y="Nombre d'annonces",
            color_discrete_sequence=["#6A5ACD"],
            title="Nombre d'annonces par ville"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Graphique 3 : Prix moyen par ville ---
    st.markdown("### 🧮 Prix moyen par localisation")
    if not df.empty and "adresse" in df.columns:
        prix_par_ville = df.groupby("adresse")["prix"].mean().reset_index()
        fig3 = px.bar(
            prix_par_ville, x="adresse", y="prix",
            color_discrete_sequence=["#2E8B57"],
            title="Prix moyen par ville"
        )
        st.plotly_chart(fig3, use_container_width=True)




# ---------------- ÉVALUATION ----------------
elif menu == "Évaluation":
    st.markdown("## 📝 Évaluation de l'application")

    st.markdown("""
    Merci de prendre quelques instants pour nous donner ton avis sur cette application.  
    Ton retour est précieux pour améliorer l'expérience et l'impact du projet CoinAfrique.
    """)

    # Deux colonnes côte à côte
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Formulaire KoboToolbox")
        st.markdown("""
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#f9f9f9">
            <p>Ce formulaire est rapide et anonyme. Il permet de recueillir ton ressenti sur l'utilisation de l'app.</p>
            <a href="https://ee.kobotoolbox.org/x/jfxd3Sgy" target="_blank" style="font-size:16px; font-weight:bold; color:#007BFF">
            👉 Accéder au formulaire KoboToolbox
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🧾 Formulaire Google Forms")
        st.markdown("""
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#f1f1f1">
            <p>Une autre version du formulaire est disponible via Google Forms. Tu peux choisir celui que tu préfères.</p>
            <a href="https://forms.gle/QU7EXeRpFEJwHAhD8" target="_blank" style="font-size:16px; font-weight:bold; color:#28A745">
            👉 Accéder au formulaire Google Forms
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🙏 Merci pour ta participation ! Ton avis compte vraiment.")
