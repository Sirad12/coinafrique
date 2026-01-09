import streamlit as st
import pandas as pd
import plotly.express as px




st.title("📊 Application CoinAfrique")

menu = st.sidebar.selectbox(
    "Menu",
    ["Accueil", "Données", "Dashboard", "Évaluation"]
)

if menu == "Accueil":
    st.markdown("""
    ## 📌 Projet CoinAfrique – Data Collection & Analyse

    Cette application permet :
    - 📥 de visualiser les données collectées sur CoinAfrique
    - 📊 d’analyser les prix des annonces
    - 📝 de recueillir l’avis des utilisateurs via un formulaire KoboToolbox
    """)

elif menu == "Données":
    import pandas as pd
    df = pd.read_csv("data/coinafrique.csv")
    st.dataframe(df.head())
    st.download_button("📥 Télécharger les données", df.to_csv(index=False).encode("utf-8"), file_name="coinafrique.csv", mime="text/csv")


elif menu == "Dashboard":
    df = pd.read_csv("data/coinafrique.csv")

    st.subheader("📈 Analyse des prix")

    col1, col2 = st.columns(2)
    col1.metric("💰 Prix moyen", f"{df['prix'].mean():,.0f} FCFA")
    col2.metric("📦 Nombre d'annonces", len(df))

    fig = px.histogram(df, x="prix", nbins=20, title="Distribution des prix")
    st.plotly_chart(fig)


elif menu == "Évaluation":
    st.markdown(
        "👉 Remplir le formulaire d’évaluation 
        [https://ee.kobotoolbox.org/x/jfxd3Sgy]
        [https://forms.gle/QU7EXeRpFEJwHAhD8]"
    )










