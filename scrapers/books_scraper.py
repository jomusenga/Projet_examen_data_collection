#import des packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from pprint import pprint
import pandas as pd
from pathlib import Path
import os


#Fonction principale de scraping
def scraper_books(nombre_pages):

    #Configuration du navigateur
    options=webdriver.ChromeOptions()

    #Mode headless pour permettre l'exécution depuis Streamlit
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    #Configuration spécifique pour Streamlit Cloud
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location="/usr/bin/chromium"

    #Lancement du navigateur:
    if os.path.exists("/usr/bin/chromedriver"):
        service=Service("/usr/bin/chromedriver")
        driver1=webdriver.Chrome(service=service,options=options)
    else:
        driver1=webdriver.Chrome(options=options)

    #Url source1
    url1="https://books.toscrape.com/catalogue/page-1.html"

    #Ouverture du site1
    driver1.get(url1)

    data_Livres=[]

    num_page=1

    while num_page<=nombre_pages:

        print(f"Scraping de la page N°{num_page}...")

        #Creation d'un container Livres pour contenir tous les livres.
        Livres=driver1.find_elements(By.CLASS_NAME,"product_pod")

        #Nombre de produits présents sur la page
        nombre_produits=len(Livres)

        for livre in Livres:
            try:

                #Récupération du lien de la fiche détaillée du livre
                lien_livre=livre.find_element(By.CSS_SELECTOR,"h3 a").get_attribute("href")


                #Informations disponibles directement sur la page catalogue
                titre=livre.find_element(By.CSS_SELECTOR,"h3 a").get_attribute("title")

                prix=livre.find_element(By.CLASS_NAME,"price_color").text

                disponibilite=livre.find_element(By.CLASS_NAME,"instock").text

                note=livre.find_element(By.CLASS_NAME,"star-rating").get_attribute("class")


                #Ouverture de la fiche détaillée dans un nouvel onglet
                driver1.execute_script("window.open(arguments[0]);",lien_livre)

                #Passage vers le nouvel onglet
                driver1.switch_to.window(driver1.window_handles[-1])


                #Nombre de reviews
                try:
                    nombre_reviews=driver1.find_element(By.XPATH,"//th[text()='Number of reviews']/following-sibling::td").text
                except:
                    nombre_reviews=""


                #Description
                try:
                    description=driver1.find_element(By.CSS_SELECTOR,"#product_description + p").text
                except:
                    description=""


                #Type de produit / Catégorie
                try:
                    breadcrumb=driver1.find_elements(By.CSS_SELECTOR,"ul.breadcrumb li a")

                    categorie=breadcrumb[-1].text

                except:
                    categorie=""


                #Tax
                try:
                    tax=driver1.find_element(By.XPATH,"//th[text()='Tax']/following-sibling::td").text
                except:
                    tax=""


                #Creation du dictionnaire
                dic={

                    'Titre': titre,
                    'Prix': prix,
                    'Disponibilité': disponibilite,
                    'Nombre_produits': nombre_produits,
                    'Note': note,
                    'Nombre_reviews': nombre_reviews,
                    'Description': description,
                    'Categorie': categorie,
                    'Tax': tax
                }


                data_Livres.append(dic)


                #Fermeture de la fiche détaillée
                driver1.close()

                #Retour vers la page catalogue
                driver1.switch_to.window(driver1.window_handles[0])


            except Exception as e:
                print("ERREUR :", e)

                #Sécurité : revenir sur l'onglet principal si nécessaire
                if len(driver1.window_handles)>1:
                    driver1.close()
                    driver1.switch_to.window(driver1.window_handles[0])


        #Arrêt si le nombre de pages demandé est atteint
        if num_page>=nombre_pages:
            break


        #Vérification de l'existance d'une page suivante pour la parcourir
        try:
            bouton_suivant=driver1.find_element(By.CSS_SELECTOR,"li.next a")

            lien_suivant=bouton_suivant.get_attribute("href")

            driver1.get(lien_suivant)

            num_page += 1

        except:
            print("Dernière page atteinte.")
            break


    #Affichage des données
    for livre in data_Livres:
        pprint(livre)


    print("=" * 50)
    print("Nombre total des livres récupérés:",len(data_Livres))
    print("=" * 50)


    #Fermeture du navigateur
    driver1.quit()


    #Création du DataFrame pour sauvegarder les données brutes extraites de Source 1 — Books to Scrape
    df_livres=pd.DataFrame(data_Livres)

    df_livres_brutes=df_livres.copy()


    #NETTOYAGE DES DONNEES:

    #1.Nettoyage de la colonne Prix
    df_livres["Prix"]=df_livres["Prix"].str.replace("£","",regex=False)

    df_livres["Prix"]=pd.to_numeric(df_livres["Prix"],errors="coerce")


    #2.Nettoyage de la colonne Note
    df_livres["Note"]=df_livres["Note"].str.replace("star-rating ","",regex=False)

    conversion_notes={
        "One":1,
        "Two":2,
        "Three":3,
        "Four":4,
        "Five":5
    }

    df_livres["Note"]=df_livres["Note"].map(conversion_notes)


    #3.Conversion du nombre de reviews en valeur numérique
    df_livres["Nombre_reviews"]=pd.to_numeric(df_livres["Nombre_reviews"],errors="coerce")


    #4. Nettoyage de Tax
    df_livres["Tax"]=df_livres["Tax"].str.replace("£","",regex=False)

    df_livres["Tax"]=pd.to_numeric(df_livres["Tax"],errors="coerce")


    #5. Nettoyage de la disponibilité
    df_livres["Disponibilité"]=df_livres["Disponibilité"].str.strip()


    #6. Nettoyage des variables texte
    df_livres["Titre"]=df_livres["Titre"].str.strip()

    df_livres["Description"]=df_livres["Description"].str.strip()

    df_livres["Categorie"]=df_livres["Categorie"].str.strip()


    #7. Vérification des valeurs manquantes
    print("\nValeurs manquantes par colonne :")
    print(df_livres.isnull().sum())


    #8. Vérification des doublons
    print("\nNombre de doublons :",df_livres.duplicated().sum())


    #9. Suppression des doublons
    df_livres=df_livres.drop_duplicates()


    #10. Vérification des types de données
    print("\nTypes des variables :")
    print(df_livres.dtypes)


    #11. Affichage des premières lignes nettoyées
    print("\nAperçu des données nettoyées :")
    print(df_livres.head())


    #Définition du chemin racine du projet
    racine_projet=Path(__file__).resolve().parent.parent

    #Définition des dossiers de sauvegarde
    dossier_raw=racine_projet / "data" / "raw"

    dossier_cleaner=racine_projet / "data" / "cleaner"


    #Création des dossiers s'ils n'existent pas
    dossier_raw.mkdir(parents=True,exist_ok=True)

    dossier_cleaner.mkdir(parents=True,exist_ok=True)


    #Sauvegarde des données brutes
    df_livres_brutes.to_csv(dossier_raw / "books_raw.csv",index=False,encoding="utf-8-sig")

    #Sauvegarde des données nettoyées
    df_livres.to_csv(dossier_cleaner / "books_cleaned.csv",index=False,encoding="utf-8-sig")

    #Retour du DataFrame vers Streamlit
    return df_livres

#EXECUTION DIRECTE DU FICHIER
if __name__=="__main__":
    #Scraping de toutes les pages du catalogue
    df_livres=scraper_books(50)

    print(df_livres.head())