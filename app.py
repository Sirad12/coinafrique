import streamlit as st
import pandas as pd
import plotly.express as px
import requests 
from bs4 import BeautifulSoup

st.set_page_config(page_title="CoinAfrique App", layout="wide")
st.title("📊 Application CoinAfrique")

menu = st.sidebar.selectbox( 
    "Menu",
    ["Accueil", "Scraping", "Téléchargement brut", "Données", "Dashboard", "Évaluation"] 
)

#Accueil
if menu == "Accueil":
    st.markdown("""
    ## 📌 Projet CoinAfrique – Data Collection & Analyse

    Cette application permet :
    - 📥 de visualiser les données collectées sur CoinAfrique 
    - 🧹 de scraper et nettoyer les données avec BeautifulSoup 
    - 🧾 de télécharger les données brutes via Web Scraper 
    - 📊 d’analyser les prix des annonces 
    - 📝 de recueillir l’avis des utilisateurs via un formulaire KoboToolbox 
    """)



# ---------------- SCRAPING ----------------
elif menu == "Scraping":

    st.subheader("🧹 Scraping des annonces")

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
                            "type": titre,
                            "prix": prix,
                            "adresse": adresse,
                            "image_lien": image
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





# 3. Téléchargement brut (Web Scraper) 
elif menu == "Téléchargement brut": 
    st.subheader("📦 Données brutes issues de Web Scraper") 
    st.markdown(""" Ces données ont été extraites sans nettoyage via l'outil Web Scraper.
    
    - [Vêtements homme](https://sn.coinafrique.com/categorie/vetements-homme) 
    - [Chaussures homme](https://sn.coinafrique.com/categorie/chaussures-homme) 
    - [Vêtements enfants](https://sn.coinafrique.com/categorie/vetements-enfants) 
    - [Chaussures enfants](https://sn.coinafrique.com/categorie/chaussures-enfants) """) 
    st.markdown("📥 Tu peux aussi télécharger le fichier brut exporté depuis Web Scraper :") 
    with open("data/coinafrique.csv", "rb") as f: 
        st.download_button("Télécharger le fichier brut", f, file_name="coinafrique.csv") 
        


# 4. Données nettoyées 
elif menu == "Données":
    st.subheader("📄 Données nettoyées – aperçu")
    df = pd.read_csv("data/coinafrique.csv")

    st.write("Dimensions :", df.shape)
    st.write("Colonnes :", list(df.columns))
    st.dataframe(df)

# 5. Dashboard 
elif menu == "Dashboard":
    df = pd.read_csv("data/coinafrique.csv") 
    st.subheader("📈 Analyse des prix") 
    
    col1, col2 = st.columns(2) 
    col1.metric("💰 Prix moyen", f"{df['prix'].mean():,.0f} FCFA") 
    col2.metric("📦 Nombre d'annonces", len(df)) 
    
    fig = px.histogram(df, x="prix", nbins=20, title="Distribution des prix") 
    st.plotly_chart(fig) 
    

# 6. Évaluation 
elif menu == "Évaluation": 
    st.markdown(""" 👉 Remplir le formulaire d’évaluation : 
    - [Formulaire KoboToolbox](https://ee.kobotoolbox.org/x/jfxd3Sgy) 
    - [Formulaire Google Forms](https://forms.gle/QU7EXeRpFEJwHAhD8) 
    """)






