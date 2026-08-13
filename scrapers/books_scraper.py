#import des packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
import pandas as pd

#Url source1
url1="https://books.toscrape.com/catalogue/page-1.html"

#Lancement du navigateur:
driver1=webdriver.Chrome()

#Ouverture du site1
driver1.get(url1)

data_Livres=[]

num_page=1

while True:

    print(f"Scraping de la page N°{num_page}...")

    #Creation d'un container Livres pour contenir tous les livres.
    Livres=driver1.find_elements(By.CLASS_NAME,"product_pod")

    #Nombre de produits présents sur la page
    nombre_produits=len(Livres)

    for livre in Livres:
        try:

            #Récupération du lien de la fiche détaillée du livre
            lien_livre=livre.find_element(
                By.CSS_SELECTOR,"h3 a"
            ).get_attribute("href")


            #Informations disponibles directement sur la page catalogue
            titre=livre.find_element(
                By.CSS_SELECTOR,"h3 a"
            ).get_attribute("title")

            prix=livre.find_element(
                By.CLASS_NAME,"price_color"
            ).text

            disponibilite=livre.find_element(
                By.CLASS_NAME,"instock"
            ).text

            note=livre.find_element(
                By.CLASS_NAME,"star-rating"
            ).get_attribute("class")


            #Ouverture de la fiche détaillée dans un nouvel onglet
            driver1.execute_script(
                "window.open(arguments[0]);",
                lien_livre
            )

            #Passage vers le nouvel onglet
            driver1.switch_to.window(driver1.window_handles[-1])


            #Nombre de reviews
            try:
                nombre_reviews=driver1.find_element(
                    By.XPATH,
                    "//th[text()='Number of reviews']/following-sibling::td"
                ).text
            except:
                nombre_reviews=""


            #Description
            try:
                description=driver1.find_element(
                    By.CSS_SELECTOR,
                    "#product_description + p"
                ).text
            except:
                description=""


            #Type de produit / Catégorie
            try:
                breadcrumb=driver1.find_elements(
                    By.CSS_SELECTOR,
                    "ul.breadcrumb li a"
                )

                categorie=breadcrumb[-1].text

            except:
                categorie=""


            #Tax
            try:
                tax=driver1.find_element(
                    By.XPATH,
                    "//th[text()='Tax']/following-sibling::td"
                ).text
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


    #Vérification de l'existance d'une page suivante pour la parcourir
    try:
        bouton_suivant=driver1.find_element(
            By.CSS_SELECTOR,
            "li.next a"
        )

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