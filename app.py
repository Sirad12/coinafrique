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




# Scraping 
elif menu == "Scraping":
    st.subheader("🧹 Scraping des données nettoyées")

    urls = { 
        "Vêtements homme": "https://sn.coinafrique.com/categorie/vetements-homme", 
        "Chaussures homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
        "Vêtements enfants": "https://sn.coinafrique.com/categorie/vetements-enfants", 
        "Chaussures enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants" 
    }

    def scrape_pages(base_url, nb_pages=1):
        all_data = []
        for i in range(1, nb_pages+1):
            url = f"{base_url}?page={i}"
            response = requests.get(url) 
            soup = BeautifulSoup(response.text, "html.parser") 
            annonces = soup.find_all("div", class_="classified") 
            
            for a in annonces: 
                titre = a.find("h2").text if a.find("h2") else "N/A" 
                prix = a.find("span", class_="price").text if a.find("span", class_="price") else "N/A" 
                adresse = a.find("span", class_="location").text if a.find("span", class_="location") else "N/A" 
                image = a.find("img")["src"] if a.find("img") else "N/A" 
                all_data.append({"type": titre, "prix": prix, "adresse": adresse, "image_lien": image})
        return pd.DataFrame(all_data)

    
    choix = st.selectbox("Choisir une catégorie", list(urls.keys())) 
    nb_pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=10, value=3)

    if st.button("Scraper"): 
        df_scraped = scrape_pages(urls[choix], nb_pages) 
        st.dataframe(df_scraped) 
        st.download_button("📥 Télécharger", df_scraped.to_csv(index=False).encode("utf-8"), file_name=f"{choix}.csv", mime="text/csv")




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
    df = pd.read_csv("data/coinafrique.csv") 
    st.dataframe(df.head()) 
    st.download_button("📥 Télécharger les données", df.to_csv(index=False).encode("utf-8"), file_name="coinafrique.csv", mime="text/csv") 
    

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



