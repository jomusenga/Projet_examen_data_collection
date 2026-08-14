#import des packages
import sqlite3
import pandas as pd
from pathlib import Path


#DEFINITION DES CHEMINS DU PROJET:

#Dossier contenant database.py
dossier_database = Path(__file__).resolve().parent

#Racine du projet:
racine_projet = dossier_database.parent

#Chemins des fichiers CSV nettoyés
chemin_books = racine_projet / "data" / "cleaner" / "books_cleaned.csv"
chemin_gaaraas = racine_projet / "data" / "cleaner" / "gaaraas_cleaned.csv"

#Chemin de la base SQLite
chemin_database = dossier_database / "data_collection.db"


#LECTURE DES FICHIERS CSV NETTOYES:
df_livres = pd.read_csv(chemin_books)
df_voitures = pd.read_csv(chemin_gaaraas)

print("Données Books chargées :", len(df_livres))
print("Données Gaaraas chargées :", len(df_voitures))

#CONNEXION A SQLITE:
connexion = sqlite3.connect(chemin_database)

#CREATION DE LA TABLE BOOKS:
df_livres.to_sql("books",connexion,if_exists="replace",index=False)

#CREATION DE LA TABLE GAARAAS:
df_voitures.to_sql("gaaraas",connexion,if_exists="replace",index=False)

#VERIFICATION DES TABLES:

tables = pd.read_sql_query("""SELECT name FROM sqlite_master WHERE type='table';""",connexion)

print("\nTables disponibles dans la base :")
print(tables)

#VERIFICATION DE LA TABLE BOOKS:

test_books = pd.read_sql_query("""SELECT* FROM books LIMIT 5;""",connexion)

print("\nAperçu de la table books :")
print(test_books)

#VERIFICATION DE LA TABLE GAARAAS:
test_gaaraas = pd.read_sql_query("""SELECT* FROM gaaraas LIMIT 5;""",connexion)

print("\nAperçu de la table gaaraas :")
print(test_gaaraas)

#NOMBRE DE LIGNES PAR TABLE:
nombre_books = pd.read_sql_query("SELECT COUNT(*) AS total FROM books;",connexion)

nombre_gaaraas = pd.read_sql_query("SELECT COUNT(*) AS total FROM gaaraas;",connexion)

print("\nNombre de lignes dans books :")
print(nombre_books)

print("\nNombre de lignes dans gaaraas :")
print(nombre_gaaraas)

#FERMETURE DE LA CONNEXION:
connexion.close()

print("\nBase SQLite créée et alimentée avec succès.")
print("Emplacement :", chemin_database)