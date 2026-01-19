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

COLOR_PRIX = "#F4A7B9"       # rose
COLOR_VILLES = "#000080"     # bleu marine
COLOR_MOYEN = "#A8D5BA"      # vert menthe


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
    <p style="font-size:16px; color:#475569; margin-bottom:30px;">
        Bienvenue sur l'application CoinAfrique ! Explorez, analysez et partagez vos avis facilement.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="height:30px;"></div>
    """, unsafe_allow_html=True)


    # Première ligne
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("""
        <div style="background-color:#E0F2FE; border-radius:12px; padding:25px; margin-bottom:20px; text-align:center; color:#0F172A;">
            <h3>📥 Visualiser les annonces</h3>
            <p>Explorez facilement les annonces collectées sur CoinAfrique.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color:#FEF3C7; border-radius:12px; padding:25px; margin-bottom:20px; text-align:center; color:#0F172A;">
            <h3>🧹 Scraper les données</h3>
            <p>Récupérez automatiquement les annonces via BeautifulSoup.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background-color:#DCFCE7; border-radius:12px; padding:25px; margin-bottom:20px; text-align:center; color:#0F172A;">
            <h3>📄 Télécharger les données</h3>
            <p>Exportez les données brutes ou nettoyées en CSV.</p>
        </div>
        """, unsafe_allow_html=True)

    # Deuxième ligne
    col4, col5 = st.columns([1, 1])

    with col4:
        st.markdown("""
        <div style="background-color:#FECACA; border-radius:12px; padding:25px; margin-bottom:20px; text-align:center; color:#0F172A;">
            <h3>📊 Analyser les prix</h3>
            <p>Visualisez la répartition des prix et tendances par ville.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div style="background-color:#EDE9FE; border-radius:12px; padding:25px; margin-bottom:20px; text-align:center; color:#0F172A;">
            <h3>📝 Évaluer l'application</h3>
            <p>Partagez votre avis via KoboToolbox ou Google Forms.</p>
        </div>
        """, unsafe_allow_html=True)




    




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
            " 📥 Télécharger le fichier CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="coinafrique_scraped.csv",
            mime="text/csv"
        )








# ================= DONNEES =================
elif menu == "Téléchargement brut":
    st.title("Données brutes – Web Scraper")

    # Introduction
    st.markdown("""
    <p style="font-size:16px; color:#475569; margin-bottom:25px;">
        Ces données ont été extraites automatiquement depuis CoinAfrique, sans nettoyage.  
        Vous pouvez consulter les catégories disponibles ci-dessous ou télécharger le fichier CSV complet.
    </p>

    <style>
    .card-row {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: nowrap;
        margin-bottom: 30px;
    }
    .card {
        flex: 0 0 200px;
        min-width: 180px;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        background-color: #E0F2FE;
        color: #0F172A;
        font-weight: 500;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0px 6px 15px rgba(0,0,0,0.15);
    }
    .card a {
        text-decoration: none;
        color: #0F172A;
        display: block;
    }
    .card h3 {
        margin: 0;
        font-size: 16px;
        
    }
    </style>

    <div class="card-row">
        <div class="card">
            <a href="https://sn.coinafrique.com/categorie/vetements-homme" target="_blank">
                <h3>Vêtements homme</h3>
            </a>
        </div>
        <div class="card">
            <a href="https://sn.coinafrique.com/categorie/chaussures-homme" target="_blank">
                <h3>Chaussures homme</h3>
            </a>
        </div>
        <div class="card">
            <a href="https://sn.coinafrique.com/categorie/vetements-enfants" target="_blank">
                <h3>Vêtements enfants</h3>
            </a>
        </div>
        <div class="card">
            <a href="https://sn.coinafrique.com/categorie/chaussures-enfants" target="_blank">
                <h3>Chaussures enfants</h3>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Bouton de téléchargement
    st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
    with open("data/coinafrique.csv", "rb") as f:
        st.download_button(
            label=" 📥 Télécharger le fichier brut complet",
            data=f,
            file_name="coinafrique.csv",
            mime="text/csv",
            key="download_brut"
        )
    st.markdown("</div>", unsafe_allow_html=True)







# ================= DASHBOARD =================
elif menu == "Dashboard":

    st.markdown("""
    <h1 style="color:#1E293B; font-size:32px;">Dashboard – Données nettoyées</h1>
    <p style="color:#475569; font-size:16px;">
        Vue synthétique des prix et des annonces collectées.
    </p>
    """, unsafe_allow_html=True)

    df = pd.read_csv("data/coinafrique.csv")

    df["prix"] = (
        df["prix"].astype(str)
        .str.replace("CFA", "")
        .str.replace(" ", "")
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df = df[df["prix"] < 1_000_000]
    df = df[["titre", "prix", "adresse", "image"]].dropna()

    # --- Aperçu rapide ---
    st.markdown("<h2 style='color:#475569;'>Aperçu des annonces</h2>", unsafe_allow_html=True)
    st.dataframe(df.head())

    st.download_button(
        "📥 Télécharger les données nettoyées",
        df.to_csv(index=False).encode("utf-8"),
        file_name="coinafrique_nettoye.csv",
        mime="text/csv"
    )

    # --- Indicateurs clés ---
st.markdown("<h2 style='color:#475569;'>Indicateurs clés</h2>", unsafe_allow_html=True)

# CSS pour les blocs
st.markdown("""
<style>
.indicator-row {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
}
.indicator-card {
    flex: 0 0 200px;
    min-width: 180px;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    background-color: #E0F2FE;
    color: #0F172A;
    font-weight: 500;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.indicator-card h3 {
    margin: 0;
    font-size: 16px;
    color: #475569;
}
.indicator-card p {
    margin: 5px 0 0;
    font-size: 18px;
    font-weight: bold;
    color: #0F172A;
}
</style>
""", unsafe_allow_html=True)

# Bloc HTML avec les valeurs dynamiques
prix_moyen = f"{df['prix'].mean():,.0f} FCFA"
nb_annonces = len(df)
nb_villes = df["adresse"].nunique()

st.markdown(f"""
<div class="indicator-row">
    <div class="indicator-card">
        <h3>Prix moyen</h3>
        <p>{prix_moyen}</p>
    </div>
    <div class="indicator-card">
        <h3>Nombre d'annonces</h3>
        <p>{nb_annonces}</p>
    </div>
    <div class="indicator-card">
        <h3>Villes uniques</h3>
        <p>{nb_villes}</p>
    </div>
</div>
""", unsafe_allow_html=True)


    # --- Graphique 1 : Distribution des prix ---
    st.markdown("<h2 style='color:#475569;'>Distribution des prix</h2>", unsafe_allow_html=True)
    fig1 = px.histogram(
        df,
        x="prix",
        nbins=30,
        color_discrete_sequence=[COLOR_PRIX],
        title=None
    )
    fig1.update_layout(bargap=0.2)
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

    # --- Graphique 2 : Annonces par ville ---
    st.markdown("<h2 style='color:#475569;'>Annonces par ville</h2>", unsafe_allow_html=True)
    ville_counts = df["adresse"].value_counts().reset_index()
    ville_counts.columns = ["Ville", "Nombre"]

    fig2 = px.bar(
        ville_counts,
        x="Ville",
        y="Nombre",
        color_discrete_sequence=[COLOR_VILLES],
        title=None
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

    # --- Graphique 3 : Prix moyen par ville ---
    st.markdown("<h2 style='color:#475569F;'>Prix moyen par ville</h2>", unsafe_allow_html=True)
    prix_ville = df.groupby("adresse")["prix"].mean().reset_index()

    fig3 = px.bar(
        prix_ville,
        x="adresse",
        y="prix",
        color_discrete_sequence=[COLOR_MOYEN],
        title=None
    )
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
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
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#E0F2FE;  text-align:center"> 
        <h4>📋 Formulaire KoboToolbox</h4> 
        <a href="https://ee.kobotoolbox.org/x/jfxd3Sgy" target="_blank" style="font-size:16px; font-weight:bold; color:#1E3A8A"> 
          Accéder au formulaire KoboToolbox </a> 
        </div> """, unsafe_allow_html=True)

    with col2:
        st.markdown(""" 
        <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#E0F2FE; text-align:center"> 
        <h4>📋 Formulaire Google </h4> 
        <a href="https://forms.gle/SE3yPxVg8Zu8FwHp9" target="_blank" style="font-size:16px; font-weight:bold; color: #1E3A8A"> 
          Accéder au formulaire google </a> 
        </div> """, unsafe_allow_html=True)




























































