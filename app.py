import streamlit as st 
import pandas as pd
import plotly.express as px
import requests 
from bs4 import BeautifulSoup

st.set_page_config(page_title="CoinAfrique App", layout="wide")

# ---------------- CSS GLOBAL ----------------
st.markdown("""
<style>
/* Fond et texte global */
body {
    background-color: #f8f9fa;
    color: #333333;
    font-family: 'Segoe UI', sans-serif;
}

/* Titres */
h1, h2, h3 {
    color: #2E8B57;
}

/* DataFrames stylés */
.stDataFrame div.row_widget.st-cm div.stDataFrameWidget {
    border-radius: 12px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
}

/* Boutons */
.stButton>button {
    background-color: #2E8B57;
    color: white;
    border-radius: 10px;
    padding: 0.5em 1.5em;
    font-weight: bold;
    border: none;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #246b45;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f0f0f0;
}

/* Liens formulaires */
a {
    text-decoration: none;
}
a:hover {
    opacity: 0.8;
}

/* Cards pour formulaires */
.form-card {
    border:1px solid #ccc; 
    padding:15px; 
    border-radius:10px; 
    background-color:#f9f9f9;
    transition: 0.3s;
}
.form-card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox( 
    "Menu",
    ["Accueil", "Scraping", "Téléchargement brut", "Dashboard", "Évaluation"] 
)

# ---------------- ACCUEIL ----------------
if menu == "Accueil":
    st.markdown("""
    <div style="text-align:center; margin-bottom:30px;">
        <h1>📊 CoinAfrique App</h1>
        <p style="font-size:18px; color:#555;">Projet de collecte et d'analyse des annonces</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ## 📌 Fonctionnalités

    Cette application permet :
    - 📥 Visualiser les données collectées sur CoinAfrique 
    - 🧹 Scraper et nettoyer les données avec BeautifulSoup 
    - 🧾 Télécharger les données brutes via Web Scraper 
    - 📊 Analyser les prix des annonces (données nettoyées) 
    - 📝 Recueillir l’avis des utilisateurs via un formulaire KoboToolbox ou Google Forms
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
        progress_bar = st.progress(0)
        status_text = st.empty()

        for page in range(1, nb_pages + 1):
            status_text.text(f"Scraping page {page} / {nb_pages} ...")
            url = f"{urls[categorie]}?page={page}"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3")
            data = []

            for c in containers:
                try:
                    titre = c.find("p", class_="ad__card-description").text.strip()
                    prix = c.find("p", class_="ad__card-price").text
                    prix = int(prix.replace("CFA", "").replace(" ", "").strip())
                    adresse = c.find("p", class_="ad__card-location").span.text.strip()
                    image = c.find("img", class_="ad__card-img")["src"]
                    data.append({"titre": titre, "prix": prix, "adresse": adresse, "image": image})
                except:
                    pass

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
            progress_bar.progress(page / nb_pages)

        status_text.text("Scraping terminé ✅")
        st.success(f"{len(df)} annonces récupérées !")

        # Affichage des annonces avec image
        for i, row in df.iterrows():
            col1, col2 = st.columns([1,3])
            with col1:
                st.image(row['image'], width=100)
            with col2:
                st.markdown(f"**{row['titre']}**\n\n💰 {row['prix']} FCFA\n📍 {row['adresse']}")

        st.download_button(
            "📥 Télécharger le CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="coinafrique_scraped.csv",
            mime="text/csv"
        )


# ---------------- TÉLÉCHARGEMENT BRUT ----------------
elif menu == "Téléchargement brut": 
    st.title("📦 Données brutes issues de Web Scraper") 
    st.markdown("Ces données ont été extraites sans nettoyage via l'outil Web Scraper.")
    st.markdown("""
    - [Vêtements homme](https://sn.coinafrique.com/categorie/vetements-homme)  
    - [Chaussures homme](https://sn.coinafrique.com/categorie/chaussures-homme)  
    - [Vêtements enfants](https://sn.coinafrique.com/categorie/vetements-enfants)  
    - [Chaussures enfants](https://sn.coinafrique.com/categorie/chaussures-enfants)  
    """) 
    st.markdown("📥 Tu peux aussi télécharger le fichier brut exporté depuis Web Scraper :") 
    with open("data/coinafrique.csv", "rb") as f: 
        st.download_button("Télécharger le fichier brut", f, file_name="coinafrique.csv") 


# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":
    st.markdown("## 📊 Dashboard des données nettoyées")

    df = pd.read_csv("data/coinafrique.csv")
    df["prix"] = pd.to_numeric(df["prix"].astype(str).str.replace("CFA","").str.replace(" ","").str.strip(), errors="coerce")
    df = df[df["prix"] < 1_000_000]
    df = df[["titre","prix","adresse","image"]].dropna()

    # --- Aperçu ---
    st.markdown("### 🔍 Aperçu des annonces")
    st.dataframe(df.head())

    # --- Metrics ---
    st.markdown("### 📌 Indicateurs clés")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("📦 Nombre d'annonces", len(df))
    col3.metric("📍 Villes uniques", df["adresse"].nunique())

    # --- Graphiques ---
    fig1 = px.histogram(df, x="prix", nbins=30, color_discrete_sequence=["#FF7F50"], title="Répartition des prix")
    fig2 = px.bar(df["adresse"].value_counts().reset_index().rename(columns={"index":"Ville","adresse":"Nombre d'annonces"}), 
                  x="Ville", y="Nombre d'annonces", color_discrete_sequence=["#6A5ACD"], title="Nombre d'annonces par ville")
    fig3 = px.bar(df.groupby("adresse")["prix"].mean().reset_index(), x="adresse", y="prix",
                  color_discrete_sequence=["#2E8B57"], title="Prix moyen par ville")

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

    # --- Téléchargement ---
    st.download_button(
        "📥 Télécharger les données nettoyées",
        df.to_csv(index=False).encode("utf-8"),
        file_name="coinafrique_nettoye.csv",
        mime="text/csv"
    )


# ---------------- ÉVALUATION ----------------
elif menu == "Évaluation":
    st.markdown("## 📝 Évaluation de l'application")
    st.markdown("Merci de prendre quelques instants pour nous donner ton avis sur cette application. Ton retour est précieux !")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="form-card">
            <h3>📋 Formulaire KoboToolbox</h3>
            <p>Rapide et anonyme pour recueillir ton ressenti.</p>
            <a href="https://ee.kobotoolbox.org/x/jfxd3Sgy" target="_blank" style="font-size:16px; font-weight:bold; color:#007BFF">
            👉 Accéder au formulaire KoboToolbox
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="form-card">
            <h3>🧾 Formulaire Google Forms</h3>
            <p>Une autre version du formulaire est disponible via Google Forms.</p>
            <a href="https://forms.gle/QU7EXeRpFEJwHAhD8" target="_blank" style="font-size:16px; font-weight:bold; color:#28A745">
            👉 Accéder au formulaire Google Forms
            </a>
        </div>
        """, unsafe_allow_html=True)


