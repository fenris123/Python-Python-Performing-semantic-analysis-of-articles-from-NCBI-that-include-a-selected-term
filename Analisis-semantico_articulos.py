# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 20:26:12 2023

@author: GUILLERMO FERRER SÁNCHEZ DE MOVELLÁN
"""






#   LIBRERIAS A USAR

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
import json
from collections import Counter
import string
import nltk
from nltk.corpus import stopwords


#####   PRIMERA PARTE:
    
#####   CONSULTA usando ESearch:
#####   Aqui se introduciran los terminos a buscar, si se quiere buscar solo en el titulo o en el texto completo
#####   y el numero de resultados a obtener.  Devuelve la id de los articulos que tengan esos terminos.





#   URL base, y definicion o peticion de entrada  de los parametros.   

base_url_parteuno = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
database = "pubmed"


query  = input ("inserte los terminos a buscar")
buscar_titulo = input ("¿Buscar terminos solo en el titulo? (si/no)")
resultados = input ("numero de artículos a estudiar (MAXIMO 200)")

# Reemplazar los espacios en query por "+" (necesario en Entrez)
query = query.replace(" ", "+")



if int(resultados) > 200:
    print ("el numero de artículos no puede ser mayor de 200")
    input("Presione Enter para salir...")
    quit()
    





# Creacion de un diccionario con los parametros dados. 
parametros_parteuno =  {"db": database, "term": query, "retmax": resultados }

if buscar_titulo.lower() == "si":  # Convertir a minúsculas para asegurar comparación correcta
    parametros_parteuno["field"] = "title"



# Montar URL definitiva, y la prueba. (no deberia haber error, pero por si acaso)

url_parteuno = base_url_parteuno + urllib.parse.urlencode (parametros_parteuno)    
    



# preparamos una lista en blanco para las ID, cogemos la URL, la leemos, y montamos los arboles
# vamos a a las hojas "./IdList/Id".  obtenemos la id, y la añadimos a la lista


ListaID = []


try:
    
    print( f"Consultando la web {url_parteuno}. Espere, por favor.")
    
    with urllib.request.urlopen(url_parteuno) as response:
        consulta_parteuno = response.read ()
        arboles= ET.fromstring (consulta_parteuno)
        hojas = arboles.findall ("./IdList/Id")
        print ("numero de articulos encontrados:",len(hojas))
        
        
# aqui capturamos la id de cada uno de los articulos 
        
        for hoja in hojas:
            
            pubmedID = hoja.text
            direccionweb = "https://pubmed.ncbi.nlm.nih.gov/" + pubmedID   ###### ESTO LO PASAREMOS A ABAJO
            ListaID.append(pubmedID)
    
            
except Exception as error_parteuno:
    print(f"Hubo un error al realizar la solicitud: {error_parteuno}")
    input("Presione Enter para salir...")

ListaID = ",".join(ListaID)    








    
#####   SEGUNDA PARTE:
    
#####   CONSULTA USANDO ESummary:
#####   Aqui el programa usara los ID obtenidos para hacer con ellos una busqueda usando ESummary
#####   Con ello lograremos los datos del articulo.  Posteriormente los guardaremos en una tabla, y en un fichero excel.



# Consulta a esummary para obtener títulos y otros detalles
base_url_partedos = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
database = "pubmed"

parametros_partedos =  {"db": database, "id": ListaID, "retmode": "xml" }


url_partedos= base_url_partedos + urllib.parse.urlencode (parametros_partedos)



#  Preparamos una tabla en blanco para los datos. Cogemos la URL, la leemos y montamos el arbol.
#  Aqui cada "hoja" sera un <DocSum>, que dentro se subdivide un monton de informacion sobre cada articulo.
#  metemos esa informacion en variables, la añadimos como fila a la tabla, y pasamos al siguiente 


Tabla_datos = []

try:
    
    with urllib.request.urlopen(url_partedos) as response:
        consulta_partedos =  response.read()
        arboles_partedos= ET.fromstring (consulta_partedos)
        


    for hojas in arboles_partedos.findall("./DocSum"):
        
        Pubmed_id = hojas.find("./Id").text
        Titulo = hojas.find("./Item[@Name='Title']").text
        Autores = [author.text for author in hojas.findall("./Item[@Name='AuthorList']/Item")]
        Publicacion = hojas.find("./Item[@Name='Source']").text
        Fecha =  hojas.find("./Item[@Name='PubDate']").text
        Citas_en_PMC = hojas.find("./Item[@Name='PmcRefCount']").text
        
        # Agregar los datos del artículo a la lista
        Tabla_datos.append([Pubmed_id, Titulo, ', '.join(Autores), Publicacion, Fecha, Citas_en_PMC])
        
      
except Exception as error_partedos:
    
     print(f"Hubo un error al realizar la solicitud: {error_partedos}")
     input("Presione Enter para salir...")



if Tabla_datos == []:
    
    print ("no se encontraron resultados para su busqueda. Intente modificar los terminos introducidos")
    input("Presione Enter para salir...")
    quit()

    
    
    
# Crear un DataFrame de pandas con los datos
data_frame_datos = pd.DataFrame(Tabla_datos, columns=['PubMed ID', 'Título', 'Autores', 'Publicación', 'Fecha', 'Citas en PMC'])   


# Pedir el directorio para guardar la informacion, y el nombre base del fichero.
# Este nombre, modificado, se usara como base para todos los ficheros posteriores
directorio = input("Inserte el directorio donde se va a guardar el archivo\n(por ejemplo, C:/Usuarios/TuUsuario/Documentos): ").strip()
nombre_archivo = input("Inserte el nombre base para los archivos, (sin la extensión .xlsx): ").strip()


# Añadir la extensión .xlsx automáticamente
nombre_archivo_xlsx = nombre_archivo + ".xlsx"


# Creacion del excel con los datos del dataframe en el directorio especificado.
# os.path.join permite que el programa funcione en linux windows o mac, sin importar  si se usa "/" o "\"
ruta_completa = os.path.join(directorio, nombre_archivo_xlsx)
data_frame_datos.to_excel(ruta_completa, index=False, engine='openpyxl')






##### TERCERA PARTE.

##### CONSULTA USANDO Entrez 
##### Aqui lo que haremos sera una consulta distinta a Entrez, para obtener los abstract de los articulos
##### Los guardaremos en un fichero de formato JSON para su posterior analisis en la cuarta parte


# Crear una lista para almacenar los abstracts
abstracts = []


# URL base para la solicitud de efetch
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
parametros_partetres = {"db": "pubmed", "id": ListaID, "retmode": "xml", "rettype": "abstract"}
url = base_url + urllib.parse.urlencode(parametros_partetres)


try:
    
    with urllib.request.urlopen(url) as response:
        respuesta = response.read()
        root = ET.fromstring(respuesta)
    
    for article in root.findall(".//PubmedArticle"):
            
        try:
            pubmed_id = article.find(".//ArticleId[@IdType='pubmed']").text
            abstract = article.find(".//AbstractText").text
            abstracts.append({"PubMed ID": pubmed_id, "Abstract": abstract})
            
        except AttributeError:
             pubmed_id = article.find(".//ArticleId[@IdType='pubmed']").text
             abstracts.append({"PubMed ID": pubmed_id, "Abstract": None})
                
                
                
except Exception as error_partetres:
    
    print(f"Error al obtener abstracts: {error_partetres}")
    abstracts = [{"PubMed ID": id, "Abstract": None} for id in ListaID.split(",")]



# Creamos el archivo JSON.  El nombre base sera el ya definido en la segunda parte, pero añadiremos automaticamente "abstracts_text"
nombre_archivo_json = f"{nombre_archivo}_abstracts_text.json"
ruta_completa_json = os.path.join(directorio, nombre_archivo_json)

with open(ruta_completa_json, "w") as json_file:
    json.dump(abstracts, json_file, indent=4)






#### CUARTA PARTE
#### A partir del archivo creado, contamos cuantas veces aparece cada palabra.
#### Filtraremos determinantes, pronombres, etc, y el resultado lo guardamos en un fichero excel.



# Cargar el archivo JSON que contiene los abstracts
with open(ruta_completa_json, "r") as json_file:
    abstracts_data = json.load(json_file)


# Diccionario para almacenar la frecuencia de las palabras
frecuencia = Counter()


# Miraremos cada abstract en el fichero, y extraeremos el texto
try:
    
    for abstract_entry in abstracts_data:
    
        abstract_text = abstract_entry["Abstract"]
        if abstract_text:  # Verificar si el abstract no es None
        
            palabras = abstract_text.split()
            palabras = [palabra.lower().strip(string.punctuation) for palabra in palabras]
            frecuencia.update(palabras)

                
except Exception as error_partecuatro:
    
    print(f"Error al obtener abstracts: {error_partecuatro}")

# Opcionalmente, ordenar el diccionario por frecuencia
frecuencia_ordenada = dict(sorted(frecuencia.items(), key=lambda item: item[1], reverse=True))






#  AQUI VAMOS A FILTRAR LOS DETERMINANTES, PREPOSICIONES, PRONOMBRES, ECT


nltk.download("stopwords")

# Obtener la lista de stopwords en inglés
stopwords_en = set(stopwords.words("english"))

# Filtrar las palabras vacías del diccionario de frecuencia de palabras, y guardarlo en un dataframe
frecuencia_filtrada = {word: freq for word, freq in frecuencia_ordenada.items() if word not in stopwords_en}
dataframe_frecuencia = pd.DataFrame.from_dict(frecuencia_filtrada, orient="index", columns=["Frecuencia"])


# Ceamos el nombre del archivo de salida con el nombre base dado en la parte dos, modificado.
nombre_archivo_salida = "frecuencia de palabras_" + nombre_archivo + ".xlsx"

# Establecemos la ruta completa del archivo (directorio+nombre) y guardamos el dataframe con la informacion
ruta_completa_archivo = f"{directorio}/{nombre_archivo_salida}"
dataframe_frecuencia.to_excel(ruta_completa_archivo, index_label="Palabra")


print ("Programa finalizado. los archivos se encontraran en el directorio indicado")
input ("Pulse enter para salir.")

