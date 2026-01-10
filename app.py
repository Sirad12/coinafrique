import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CoinAfrique App",
    layout="wide"
)

COLORS = {
    "blue": "#1E3A8A",
    "green": "#2E7D32",
    "purple": "#6D28D9",
    "orange": "#D97706"
}

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#0F172A", size=14),
    title=dict(font=dict(size=18), x=0.02),
    margin=dict(l=40, r=40, t=60, b=40)
)

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Menu",
    ["Accueil", "Scraping", "Téléchargement brut", "Dashboard", "Évaluation"]
)

# ================= ACCUEIL =================
if menu == "Accueil":
    st.title("Application CoinAfrique")

    st.markdown("""
    ### Collecte et analyse de données

    Cette application permet :
    - Visualiser les annonces collectées sur CoinAfrique
    - Scraper les données avec BeautifulSoup
    - Télécharger les données brutes
    - Analyser les prix des annonces nettoyées
    - Recueillir l’avis des utilisateurs
    """)

# ================= SCRAPING =================
elif menu == "Scraping":
    st.title("Scraping des annonces")

    urls = {
        "Vêtements homme": "https://sn.coinafrique.com/categorie/vetements-homme",
        "Chaussures homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
        "Vêtements enfants": "https://sn.coinafrique.com/categorie/vetements-enfants",
        "Chaussures enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants"
    }

    categorie = st.selectbox("Catégorie", list(urls.keys()))
    nb_pages = st.number_input("Nombre de pages à scraper", 1, 10, 3)

    if st.button("Lancer le scraping"):
        df = pd.DataFrame()
        progress = st.progress(0)

        for page in range(1, nb_pages + 1):
            url = f"{urls[categorie]}?page={page}"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3")

            data = []

            for c in containers:
                try:
                    data.append({
                        "titre": c.find("p", class_="ad__card-description").text.strip(),
                        "prix": int(
                            c.find("p", class_="ad__card-price")
                            .text.replace("CFA", "").replace(" ", "").strip()
                        ),
                        "adresse": c.find("p", class_="ad__card-location").span.text.strip(),
                        "image": c.find("img", class_="ad__card-img")["src"]
                    })
                except:
                    pass

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            progress.progress(page / nb_pages)

        st.success(f"{len(df)} annonces récupérées")
        st.dataframe(df)

        st.download_button(
            "Télécharger le CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="coinafrique_scraped.csv",
            mime="text/csv"
        )

# ================= DONNÉES BRUTES =================
elif menu == "Téléchargement brut":
    st.title("Données brutes – Web Scraper")

    st.markdown("""
    Ces données ont été extraites sans nettoyage.
    """)

    with open("data/coinafrique.csv", "rb") as f:
        st.download_button("Télécharger le fichier brut", f, "coinafrique.csv")

# ================= DASHBOARD =================
elif menu == "Dashboard":
    st.title("Dashboard – Données nettoyées")

    df = pd.read_csv("data/coinafrique.csv")

    df["prix"] = (
        df["prix"].astype(str)
        .str.replace("CFA", "")
        .str.replace(" ", "")
        .str.strip()
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

    df = df[df["prix"] < 1_000_000]
    df = df[["titre", "prix", "adresse", "image"]].dropna()

    st.subheader("Indicateurs clés")
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("Nombre d'annonces", len(df))
    col3.metric("Villes uniques", df["adresse"].nunique())

    # Distribution des prix (bleu)
    fig1 = px.histogram(
        df, x="prix", nbins=30,
        title="Distribution des prix",
        color_discrete_sequence=[COLORS["blue"]]
    )
    fig1.update_layout(bargap=0.2)
    st.plotly_chart(fig1, use_container_width=True)

    # Annonces par ville (vert)
    ville_counts = df["adresse"].value_counts().reset_index()
    ville_counts.columns = ["Ville", "Nombre"]

    fig2 = px.bar(
        ville_counts, x="Ville", y="Nombre",
        title="Annonces par ville",
        color_discrete_sequence=[COLORS["green"]]
    )
    fig2.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

    # Prix moyen par ville (violet)
    prix_ville = df.groupby("adresse")["prix"].mean().reset_index()

    fig3 = px.bar(
        prix_ville, x="adresse", y="prix",
        title="Prix moyen par ville",
        color_discrete_sequence=[COLORS["purple"]]
    )
    fig3.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

# ================= ÉVALUATION =================
elif menu == "Évaluation":
    st.title("Évaluation de l'application")

    st.markdown("Merci de prendre quelques instants pour donner ton avis.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Formulaire KoboToolbox")
        st.markdown("""
        Ce formulaire permet de recueillir l’avis des utilisateurs.
        """)
        st.link_button(
            "Accéder au formulaire",
            "https://ee.kobotoolbox.org/x/jfxd3Sgy"
        )

    with col2:
        st.subheader("Formulaire Google Forms")
        st.markdown("""
        Ce formulaire est destiné à l’évaluation académique.
        """)
        st.link_button(
            "Accéder au formulaire",
            "https://forms.gle/QU7EXeRpFEJwHAhD8"
        )
