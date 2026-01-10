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

    # Chargement et nettoyage
    df = pd.read_csv("data/coinafrique.csv")

    df["prix"] = (
        df["prix"]
        .astype(str)
        .str.replace("CFA", "")
        .str.replace(" ", "")
        .str.strip()
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

    colonnes_utiles = [col for col in ["titre", "prix", "adresse", "image"] if col in df.columns]
    df = df[colonnes_utiles].dropna()

    # Aperçu rapide
    st.markdown("### 🔍 Aperçu des annonces")
    st.dataframe(df.head())

    # Téléchargement
    st.download_button(
        "📥 Télécharger les données nettoyées",
        df.to_csv(index=False).encode("utf-8"),
        file_name="coinafrique_nettoye.csv",
        mime="text/csv"
    )

    # Indicateurs
    st.markdown("### 📌 Indicateurs clés")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("📦 Nombre d'annonces", len(df))
    col3.metric("📍 Villes uniques", df["adresse"].nunique())

    # Graphique 1 : Histogramme des prix
    st.markdown("### 📊 Distribution des prix")
    fig1 = px.histogram(df, x="prix", nbins=20, color_discrete_sequence=["#FF7F50"])
    st.plotly_chart(fig1, use_container_width=True)

    # Graphique 2 : Répartition par ville
    st.markdown("### 🗺️ Annonces par ville")
    fig2 = px.bar(
        df["adresse"].value_counts().reset_index(),
        x="index",
        y="adresse",
        labels={"index": "Ville", "adresse": "Nombre"},
        color_discrete_sequence=["#6A5ACD"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Aperçu visuel
    st.markdown("### 🖼️ Aperçu visuel")
    for i, row in df.head(6).iterrows():
        st.image(row["image"], width=150)
        st.write(f"**{row['titre']}** — {row['prix']:,.0f} FCFA")
        st.write(f"📍 {row['adresse']}")
        st.markdown("---")






# ---------------- ÉVALUATION ----------------
elif menu == "Évaluation": 
    st.title("Évaluation")
    st.markdown(""" 👉 Remplir le formulaire d’évaluation : 
    - [Formulaire KoboToolbox](https://ee.kobotoolbox.org/x/jfxd3Sgy) 
    - [Formulaire Google Forms](https://forms.gle/QU7EXeRpFEJwHAhD8) 
    """)












