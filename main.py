#import des packages
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from pathlib import Path

#Import de la fonction de scraping Books
from scrapers.books_scraper import scraper_books
from scrapers.gaaraas_scraper import scraper_gaaraas


#CONFIGURATION DE L'APPLICATION

st.set_page_config(
    page_title="Data Collection & Visualization",
    page_icon="D:\Mon programme de MASTER_DIT\Master 1\Cours\Data Collection\Seances\Projet\Projet_examen_data_collection\icones\surveiller.png",
    layout="wide"
)


#DEFINITION DES CHEMINS:

#1.Racine du projet
racine_projet = Path(__file__).resolve().parent

#2.Chemin vers la base SQLite
chemin_database = racine_projet / "database" / "data_collection.db"


#CHEMINS DES DONNEES NO-CODE
chemin_books_nocode = (racine_projet/ "data"/ "no_code"/ "books_webscraper.csv")
chemin_gaaraas_nocode = (racine_projet/ "data"/ "no_code"/ "gaaraas_webscraper.csv")


#CONNEXION A SQLITE
connexion = sqlite3.connect(chemin_database)


#LECTURE DES TABLES
df_books = pd.read_sql_query("SELECT * FROM books;",connexion)
df_gaaraas = pd.read_sql_query("SELECT * FROM gaaraas;",connexion)


#Fermeture de la connexion
connexion.close()


#Conversion de l'année en entier
df_gaaraas["Annee"] = df_gaaraas["Annee"].astype("Int64")

#TITRE DE L'APPLICATION

st.title("Application de collecte et visualisation des données")

st.write("""Application de web scraping, nettoyage, stockageet visualisation des données.""")

st.divider()


#MENU LATERAL

st.sidebar.title("Navigation")
source = st.sidebar.selectbox("Choisir une source de données",["Accueil","Books to Scrape","Gaaraas"])

#PAGE ACCUEIL

if source == "Accueil":

    st.header("Accueil")

    st.write(
        """
        Cette application permet d'explorer les données collectées
        à partir de deux sources :
        
        - **Books to Scrape**
        - **Gaaraas**
        
        Les données ont été collectées avec Selenium,
        nettoyées avec Pandas puis stockées dans une base SQLite.
        """
    )

    st.subheader("Vue d'ensemble")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(label="Nombre total de livres",value=len(df_books))

    with col2:

        st.metric(label="Nombre total de véhicules",value=len(df_gaaraas))



#PAGE BOOKS

elif source == "Books to Scrape":

    st.header("Dashboard Books to Scrape")

    #SCRAPING SELENIUM BOOKS
    st.subheader("Scraping Selenium Books")
    st.write("""Cette section permet de lancer directement un scrapingde Books to Scrape sur plusieurs pages.""")

    #Choix du nombre de pages
    nombre_pages_books = st.number_input("Nombre de pages à scraper",min_value=1,max_value=50,value=2,step=1)

    #Bouton de lancement du scraping
    if st.button("Lancer le scraping Books",type="primary"):
        try:

            with st.spinner(f"Scraping de {nombre_pages_books} page(s) en cours..."):

                df_scraping_books = scraper_books(int(nombre_pages_books))

                #Sauvegarde du résultat dans la session Streamlit
                st.session_state["df_scraping_books"] = df_scraping_books

            st.success(f"Scraping terminé avec succès : "f"{len(df_scraping_books)} livres récupérés.")

        except Exception as e:
            st.error(f"Une erreur est survenue pendant le scraping : {e}")

    #Affichage du dernier résultat du scraping
    if "df_scraping_books" in st.session_state:

        df_scraping_books = st.session_state["df_scraping_books"]
        st.write("Nombre de livres récupérés :",len(df_scraping_books))
        st.dataframe(df_scraping_books,use_container_width=True)

    st.divider()

    #FILTRES BOOKS

    st.sidebar.subheader("Filtres Books")

    #Filtre catégorie
    categories = st.sidebar.multiselect("Catégorie",options=sorted(df_books["Categorie"].dropna().unique()),default=[])

    #Filtre note
    notes = st.sidebar.multiselect("Note",options=sorted(df_books["Note"].dropna().unique()),default=[])

    #Valeurs minimum et maximum du prix
    prix_min_books = float(df_books["Prix"].min())
    prix_max_books = float(df_books["Prix"].max())

    #Filtre prix
    plage_prix_books = st.sidebar.slider("Plage de prix (£)",min_value=prix_min_books,max_value=prix_max_books,value=(prix_min_books,prix_max_books))

    #CREATION DU DATAFRAME FILTRE BOOKS

    df_books_filtre = df_books.copy()


    #Filtre catégorie
    if categories:

        df_books_filtre = df_books_filtre[df_books_filtre["Categorie"].isin(categories)]

    #Filtre note
    if notes:

        df_books_filtre = df_books_filtre[df_books_filtre["Note"].isin(notes)]

    #Filtre prix
    df_books_filtre = df_books_filtre[
        (df_books_filtre["Prix"]>= plage_prix_books[0])&(df_books_filtre["Prix"]<= plage_prix_books[1])]

    #KPI BOOKS

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(label="Nombre de livres",value=len(df_books_filtre))

    with col2:

        prix_moyen_books = (df_books_filtre["Prix"].mean()
            if len(df_books_filtre) > 0
            else 0
        )

        st.metric(label="Prix moyen",value=f"{prix_moyen_books:.2f} £")

    with col3:

        note_moyenne = (df_books_filtre["Note"].mean()
            if len(df_books_filtre) > 0
            else 0
        )

        st.metric(label="Note moyenne",value=f"{note_moyenne:.2f}/5")

    with col4:

        st.metric(label="Nombre de catégories",value=df_books_filtre["Categorie"].nunique())

    st.divider()

    #GRAPHIQUES BOOKS

    st.subheader("Visualisations")

    if len(df_books_filtre) > 0:

        #LIGNE 1 DES GRAPHIQUES

        col1, col2 = st.columns(2)

        #Nombre de livres par catégorie
        with col1:

            books_par_categorie = (df_books_filtre["Categorie"].value_counts().reset_index())
            books_par_categorie.columns = ["Categorie","Nombre"]
            fig1 = px.bar(books_par_categorie.head(15),x="Categorie",y="Nombre",title="Nombre de livres par catégorie")
            st.plotly_chart(fig1,use_container_width=True)


        #Répartition des notes
        with col2:

            notes_books = (df_books_filtre["Note"].value_counts().sort_index().reset_index())
            notes_books.columns = ["Note","Nombre"]
            fig2 = px.bar(notes_books,x="Note",y="Nombre",title="Répartition des livres par note")
            st.plotly_chart(fig2,use_container_width=True)

        #PRIX MOYEN PAR CATEGORIE

        prix_categorie = (df_books_filtre.groupby("Categorie")["Prix"].mean().reset_index().sort_values("Prix",ascending=False))
        fig3 = px.bar(prix_categorie.head(15),x="Categorie",y="Prix",title="Prix moyen par catégorie")
        st.plotly_chart(fig3,use_container_width=True)

    else:

        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")

    st.divider()

    #TABLEAU BOOKS

    st.subheader("Données Books")
    st.write("Nombre de lignes affichées :",len(df_books_filtre))
    st.dataframe(df_books_filtre,use_container_width=True)


#PAGE GAARAAS

elif source == "Gaaraas":

    st.header("Dashboard Gaaraas")

        #SCRAPING SELENIUM GAARAAS

    st.subheader("Scraping Selenium Gaaraas")

    st.write(
        """
        Cette section permet de lancer directement un scraping
        de Gaaraas sur plusieurs pages.
        """
    )

    #Choix du nombre de pages
    nombre_pages_gaaraas = st.number_input("Nombre de pages à scraper",min_value=1,max_value=100,value=2,step=1,key="nombre_pages_gaaraas")

    #Bouton de lancement du scraping
    if st.button("Lancer le scraping Gaaraas",type="primary"):

        try:

            with st.spinner(f"Scraping de {nombre_pages_gaaraas} page(s) en cours..."):

                df_scraping_gaaraas = scraper_gaaraas(int(nombre_pages_gaaraas))

                #Sauvegarde du résultat dans la session Streamlit
                st.session_state["df_scraping_gaaraas"] = df_scraping_gaaraas

            st.success(f"Scraping terminé avec succès : {len(df_scraping_gaaraas)} véhicules récupérés.")

        except Exception as e:

            st.error(f"Une erreur est survenue pendant le scraping : {e}")

    #Affichage du dernier résultat du scraping
    if "df_scraping_gaaraas" in st.session_state:

        df_scraping_gaaraas = st.session_state["df_scraping_gaaraas"]

        st.write("Nombre de véhicules récupérés :",len(df_scraping_gaaraas))

        st.dataframe(df_scraping_gaaraas,use_container_width=True)

    st.divider()

    #FILTRES GAARAAS

    st.sidebar.subheader("Filtres Gaaraas")

    #Filtre marque
    marques = st.sidebar.multiselect("Marque",options=sorted(df_gaaraas["Marque"].dropna().unique()),default=[])



    #Filtre boîte de vitesse
    boites = st.sidebar.multiselect("Boîte de vitesse",options=sorted(df_gaaraas["Boite_vitesse"].dropna().unique()),default=[])


    #Filtre région
    regions = st.sidebar.multiselect("Région",options=sorted(df_gaaraas["Region"].dropna().unique()),default=[])

    #Filtre année sans .0
    annees_disponibles = sorted(df_gaaraas["Annee"].dropna().astype(int).unique())

    annees = st.sidebar.multiselect("Année",options=annees_disponibles,default=[])

    #Valeur minimum du prix
    prix_min_gaaraas = int(df_gaaraas["Prix"].min())


    #Valeur maximum du prix
    prix_max_gaaraas = int(df_gaaraas["Prix"].max())


    #Filtre prix
    plage_prix_gaaraas = st.sidebar.slider("Plage de prix (FCFA)",min_value=prix_min_gaaraas,max_value=prix_max_gaaraas,value=(prix_min_gaaraas,prix_max_gaaraas))

    #CREATION DU DATAFRAME FILTRE GAARAAS

    df_gaaraas_filtre = df_gaaraas.copy()


    #Filtre marque
    if marques:

        df_gaaraas_filtre = df_gaaraas_filtre[df_gaaraas_filtre["Marque"].isin(marques)]

    #Filtre boîte de vitesse
    if boites:

        df_gaaraas_filtre = df_gaaraas_filtre[
            df_gaaraas_filtre["Boite_vitesse"].isin(boites)]

    #Filtre région
    if regions:

        df_gaaraas_filtre = df_gaaraas_filtre[df_gaaraas_filtre["Region"].isin(regions)]

    #Filtre année
    if annees:

        df_gaaraas_filtre = df_gaaraas_filtre[df_gaaraas_filtre["Annee"].isin(annees)]

    #Filtre prix
    df_gaaraas_filtre = df_gaaraas_filtre[(df_gaaraas_filtre["Prix"]>= plage_prix_gaaraas[0])&(df_gaaraas_filtre["Prix"]<= plage_prix_gaaraas[1])]

    #KPI GAARAAS
    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(label="Nombre de véhicules",value=len(df_gaaraas_filtre))

    with col2:

        prix_moyen_gaaraas = (df_gaaraas_filtre["Prix"].mean()if len(df_gaaraas_filtre) > 0else 0)

        st.metric(label="Prix moyen",value=f"{prix_moyen_gaaraas:,.0f} FCFA")

    with col3:

        kilometrage_moyen = (df_gaaraas_filtre["Kilometrage"].mean()
            if len(df_gaaraas_filtre) > 0
            else 0
        )

        st.metric(label="Kilométrage moyen",value=f"{kilometrage_moyen:,.0f} KM")

    with col4:

        st.metric(label="Nombre de marques",value=df_gaaraas_filtre["Marque"].nunique())

    st.divider()

    #GRAPHIQUES GAARAAS

    st.subheader("Visualisations")

    if len(df_gaaraas_filtre) > 0:

        #LIGNE 1

        col1, col2 = st.columns(2)

        #Nombre de véhicules par marque
        with col1:

            voitures_marque = (df_gaaraas_filtre["Marque"].value_counts().reset_index())
            voitures_marque.columns = ["Marque","Nombre"]
            fig4 = px.bar(voitures_marque.head(15),x="Marque",y="Nombre",title="Nombre de véhicules par marque")
            st.plotly_chart(fig4,use_container_width=True)


        #Répartition par boîte de vitesse
        with col2:

            boite_distribution = (df_gaaraas_filtre["Boite_vitesse"].value_counts().reset_index())
            boite_distribution.columns = ["Boite_vitesse","Nombre"]
            fig5 = px.pie(boite_distribution,names="Boite_vitesse",values="Nombre",title="Répartition par boîte de vitesse")
            st.plotly_chart(fig5,use_container_width=True)

        #PRIX MOYEN PAR MARQUE

        prix_marque = (df_gaaraas_filtre.groupby("Marque")["Prix"].mean().reset_index().sort_values("Prix",ascending=False))
        fig6 = px.bar(prix_marque.head(15),x="Marque",y="Prix",title="Prix moyen par marque")
        st.plotly_chart(fig6,use_container_width=True)

        #VEHICULES PAR ANNEE

        vehicules_annee = (df_gaaraas_filtre.dropna(subset=["Annee"]).groupby("Annee").size().reset_index(name="Nombre").sort_values("Annee"))


        fig7 = px.line(vehicules_annee,x="Annee",y="Nombre",markers=True,title="Nombre de véhicules par année")
        st.plotly_chart(fig7,use_container_width=True)


    else:

        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")


    st.divider()


    #TABLEAU GAARAAS

    st.subheader("Données Gaaraas")
    st.write("Nombre de lignes affichées :",len(df_gaaraas_filtre))
    st.dataframe(df_gaaraas_filtre,use_container_width=True)

#TELECHARGEMENT DES DONNEES

st.divider()

st.subheader("Téléchargement des données brutes")


if chemin_gaaraas_nocode.exists():

    with open(chemin_gaaraas_nocode,"rb") as fichier:

        st.download_button(label="Télécharger les données brutes Web Scraper - Gaaraas",data=fichier,file_name="gaaraas_webscraper.csv",mime="text/csv")

else:

    st.warning("Le fichier brut Web Scraper Gaaraas est introuvable.")


if chemin_books_nocode.exists():

    with open(chemin_books_nocode,"rb") as fichier:

        st.download_button(label="Télécharger les données brutes Web Scraper - Books",data=fichier,file_name="books_webscraper.csv",mime="text/csv")


else:

    st.warning("Le fichier brut Web Scraper Books est introuvable.")



#EVALUATION DE L'APPLICATION Via formulaire KoboToolbox ou Google Forms

st.subheader("FORMULAIRES D'EVALUATION DE L'APPLICATION")


st.link_button("Évaluer via KoboToolbox","https://ee-eu.kobotoolbox.org/x/BWx3Lswi")
st.link_button("Évaluer via Google Forms","https://docs.google.com/forms/d/e/1FAIpQLScTsGZlmdGrqGtW9ojOImLQlzLt4YMnta9EGb5CtWzla3pcrQ/viewform")