#import des packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
from pathlib import Path
import pandas as pd


#Fonction principale de scraping
def scraper_gaaraas(nombre_pages):

    #Configuration du navigateur
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    options.binary_location="/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    #Lancement du navigateur
    driver2 = webdriver.Chrome(options=options)

    #Délai maximal de chargement
    driver2.set_page_load_timeout(120)

    #Liste pour stocker toutes les annonces
    data_Voitures = []

    #Boucle sur le nombre de pages demandé
    for page in range(1, nombre_pages + 1):

        print(f"Scraping de la page N°{page}...")

        #Construction dynamique de l'URL
        url2 = f"https://www.gaaraas.com/fr/users/dakar-auto?page={page}"

        try:
            driver2.get(url2)

        except Exception as e:
            print(f"ERREUR DE CHARGEMENT PAGE {page} :", e)
            continue

        #Attendre que les annonces soient présentes
        try:
            WebDriverWait(driver2, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "common-ad-card")))

        except Exception as e:
            print(f"Aucune annonce trouvée sur la page {page} :", e)
            continue

        #Container des véhicules de la page
        Voitures = driver2.find_elements(By.CLASS_NAME,"common-ad-card")

        print(f"Nombre des véhicules trouvés sur la page {page} :",len(Voitures))

        for voiture in Voitures:

            try:

                #Titre complet
                titre_complet = voiture.find_element(By.CSS_SELECTOR,"h4").get_attribute("title")

                #Séparation du titre
                parties = titre_complet.split()

                #Année
                if len(parties) > 0 and parties[0].isdigit() and len(parties[0]) == 4:

                    annee = parties[0]
                    reste = parties[1:]

                else:

                    annee = ""
                    reste = parties

                #Marques composées
                if len(reste) >= 2 and reste[0] == "Land" and reste[1] == "Rover":

                    marque = "Land Rover"
                    modele = " ".join(reste[2:])

                elif len(reste) >= 1 and reste[0].startswith("Mercedes"):

                    marque = reste[0]
                    modele = " ".join(reste[1:])

                else:

                    marque = reste[0] if len(reste) > 0 else ""
                    modele = " ".join(reste[1:]) if len(reste) > 1 else ""

                #Prix
                prix = voiture.find_element(By.CLASS_NAME,"price").text

                #Kilométrage
                kilometrage = voiture.find_element(By.CSS_SELECTOR,".ad-vehicle-mileage .value").text

                #Région
                region = voiture.find_element(By.CLASS_NAME,"location").text

                #Boîte de vitesse
                boite_vitesse = voiture.find_element(By.CSS_SELECTOR,".transmission span").text

                #Création du dictionnaire
                dic = {
                    "Marque": marque,
                    "Modele": modele,
                    "Annee": annee,
                    "Prix": prix,
                    "Kilometrage": kilometrage,
                    "Boite_vitesse": boite_vitesse,
                    "Region": region
                }

                #Ajout dans la liste
                data_Voitures.append(dic)

            except Exception as e:

                print(f"ERREUR SUR UNE ANNONCE PAGE {page} :", e)

    #Fermeture du navigateur
    driver2.quit()

    #Transformation en DataFrame
    df_voitures = pd.DataFrame(data_Voitures)

    #Affichage
    print("=" * 50)
    print("Nombre total des véhicules récupérés :",len(data_Voitures))
    print("=" * 50)

    print(df_voitures.head())

    #NETTOYAGE DES DONNEES:

    #Copie des données brutes
    df_voitures_brut = df_voitures.copy()

    #NETTOYAGE DES DONNEES GAARAAS:

    #1. Nettoyage du Prix
    df_voitures["Prix"] = df_voitures["Prix"].str.replace(" ", "", regex=False)

    df_voitures["Prix"] = pd.to_numeric(df_voitures["Prix"],errors="coerce")

    #2. Nettoyage du Kilométrage
    df_voitures["Kilometrage"] = df_voitures["Kilometrage"].str.replace("KM", "", regex=False).str.replace("km", "", regex=False).str.replace(" ", "", regex=False).str.strip()

    df_voitures["Kilometrage"] = pd.to_numeric(df_voitures["Kilometrage"],errors="coerce")

    #3. Conversion de l'année en valeur numérique
    df_voitures["Annee"] = pd.to_numeric(df_voitures["Annee"],errors="coerce").astype("Int64")

    #4. Nettoyage des variables texte
    df_voitures["Marque"] = df_voitures["Marque"].str.strip()

    df_voitures["Modele"] = df_voitures["Modele"].str.strip()

    df_voitures["Boite_vitesse"] = df_voitures["Boite_vitesse"].str.strip()

    df_voitures["Region"] = df_voitures["Region"].str.strip()

    #5. Vérification des valeurs manquantes
    print("\nValeurs manquantes par colonne :")
    print(df_voitures.isnull().sum())

    #6. Vérification des doublons
    print("\nNombre de doublons :",df_voitures.duplicated().sum())

    #7. Suppression des doublons
    df_voitures = df_voitures.drop_duplicates()

    #8. Vérification des types
    print("\nTypes des variables :")
    print(df_voitures.dtypes)

    #9. Dimensions du DataFrame
    print("\nDimensions du DataFrame :",df_voitures.shape)

    #10. Aperçu des données nettoyées
    print("\nAperçu des données nettoyées :")
    print(df_voitures.head())

    #Sauvegarde des fichiers:

    #Définition du chemin racine du projet
    racine_projet = Path(__file__).resolve().parent.parent

    #Définition des dossiers de sauvegarde
    dossier_raw = racine_projet / "data" / "raw"
    dossier_cleaner = racine_projet / "data" / "cleaner"

    #Création des dossiers s'ils n'existent pas
    dossier_raw.mkdir(parents=True, exist_ok=True)
    dossier_cleaner.mkdir(parents=True, exist_ok=True)

    #Sauvegarde des données brutes
    df_voitures_brut.to_csv(dossier_raw / "gaaraas_raw.csv",index=False,encoding="utf-8-sig")

    #Sauvegarde des données nettoyées
    df_voitures.to_csv(dossier_cleaner / "gaaraas_cleaned.csv",index=False,encoding="utf-8-sig")

    print("\nFichiers CSV sauvegardés avec succès.")

    #Retour du DataFrame vers Streamlit
    return df_voitures

#EXECUTION DIRECTE DU FICHIER
if __name__=="__main__":

    #Scraping des 100 pages demandées
    df_voitures = scraper_gaaraas(100)

    print(df_voitures.head())