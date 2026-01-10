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

COLOR_PRIX = "#F4A7B9"     # rose
COLOR_VILLES = "#000080"     # bleu marine
COLOR_MOYEN = "#A8D5BA"     # vert menthe


PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#0F172A", size=14),
    title=dict(
        font=dict(size=18, color="#0F172A"),
        x=0.02
    ),
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
    nb_pages = st.number_input(
        "Nombre de pages à scraper",
        min_value=1,
        max_value=10,
        value=3
    )

    if st.button("Lancer le scraping"):
        df = pd.DataFrame()
        progress = st.progress(0)

        for page in range(1, nb_pages + 1):
            url = f"{urls[categorie]}?page={page}"
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            soup = BeautifulSoup(response.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3")

            data = []

            for c in containers:
                try:
                    titre = c.find(
                        "p", class_="ad__card-description"
                    ).text.strip()

                    prix = c.find(
                        "p", class_="ad__card-price"
                    ).text.replace("CFA", "").replace(" ", "").strip()
                    prix = int(prix)

                    adresse = c.find(
                        "p", class_="ad__card-location"
                    ).span.text.strip()

                    image = c.find(
                        "img", class_="ad__card-img"
                    )["src"]

                    data.append({
                        "titre": titre,
                        "prix": prix,
                        "adresse": adresse,
                        "image": image
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

    - Vêtements homme  
    - Chaussures homme  
    - Vêtements enfants  
    - Chaussures enfants  
    """)

    with open("data/coinafrique.csv", "rb") as f:
        st.download_button(
            "Télécharger le fichier brut",
            f,
            file_name="coinafrique.csv"
        )

# ================= DASHBOARD =================
elif menu == "Dashboard":
    st.title("Dashboard – Données nettoyées")

    df = pd.read_csv("data/coinafrique.csv")

    df["prix"] = (
        df["prix"]
        .astype(str)
        .str.replace("CFA", "")
        .str.replace(" ", "")
        .str.strip()
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

    df = df[df["prix"] < 1_000_000]
    df = df[["titre", "prix", "adresse", "image"]].dropna()

    st.subheader("Aperçu des annonces")
    st.dataframe(df.head())

    st.download_button(
        "Télécharger les données nettoyées",
        df.to_csv(index=False).encode("utf-8"),
        file_name="coinafrique_nettoye.csv",
        mime="text/csv"
    )

    st.subheader("Indicateurs clés")
    col1, col2, col3 = st.columns(3)

    col1.metric("Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("Nombre d'annonces", len(df))
    col3.metric("Villes uniques", df["adresse"].nunique())

    st.subheader("Distribution des prix")
    fig1 = px.histogram(
        df,
        x="prix",
        nbins=30,
        color_discrete_sequence=[COLOR_PRIX],
        title="Distribution des prix"
    )
    fig1.update_layout(bargap=0.2)
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Nombre d'annonces par ville")
    ville_counts = df["adresse"].value_counts().reset_index()
    ville_counts.columns = ["Ville", "Nombre"]

    fig2 = px.bar(
        ville_counts,
        x="Ville",
        y="Nombre",
        color_discrete_sequence=[COLOR_VILLES],
        title="Annonces par ville"
    )
    fig2.update_layout(**PLOTLY_LAYOUT)
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Prix moyen par ville")
    prix_ville = df.groupby("adresse")["prix"].mean().reset_index()

    fig3 = px.bar(
        prix_ville,
        x="adresse",
        y="prix",
        color_discrete_sequence=[COLOR_MOYEN],
        title="Prix moyen par ville"
    )
    fig3.update_layout(**PLOTLY_LAYOUT)
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)

# ================= ÉVALUATION =================
elif menu == "Évaluation":
    st.title("Évaluation de l'application")

    st.markdown("""
    <p style="
        font-size:16px;
        color:#475569;
        margin-bottom:25px;
    ">
        Vous pouvez choisir librement le formulaire avec lequel vous êtes le plus à l’aise
        pour partager votre avis.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(""" 
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#F1F5F9;  text-align:center"> 
        <h4>📋 Formulaire KoboToolbox</h4> 
        <a href="https://ee.kobotoolbox.org/x/jfxd3Sgy" target="_blank" style="font-size:16px; font-weight:bold; color:#1E3A8A"> 
          Accéder au formulaire KoboToolbox </a> 
        </div> """, unsafe_allow_html=True)

    with col2:
        st.markdown(""" 
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#F1F5F9; text-align:center"> 
        <h4>📋 Formulaire Google Forms</h4> 
        <a href="https://forms.gle/SE3yPxVg8Zu8FwHp9" target="_blank" style="font-size:16px; font-weight:bold; color:#1E3A8A"> 
          Accéder au formulaire google forms </a> 
        </div> """, unsafe_allow_html=True)


















