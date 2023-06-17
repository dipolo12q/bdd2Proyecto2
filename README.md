# bdd2Proyecto2

<img src="https://upload.wikimedia.org/wikipedia/commons/7/7a/UTEC.jpg" width="200">

# **Integrantes**
* Franco Pacheco Espino
* Nincol Abraham Quiroz Maquin
* Johannes Albert Segundo Loayza Huamán
* Fabian Martin Alvarado Vargas


# Tabla de contenido
- [Cuadro de Participación](#Cuadro-de-Participación)
- [Objetivo](#Objetivo)
- [Backend](#Backend)
  * [Dataset](#Dataset)
  * [Inverted index](#Inverted-index)
  * [Funciones importantes](#Funciones-importantes)
    + [Clase principal](#Clase-principal)
    + [Función load](#Función-load)
    + [Función score](#Función-score)
    + [Función retrieve](#Función-retrieve)
- [Frontend](#Frontend)
  * [Comparación de tiempo](#Comparación-de-tiempo)


# Cuadro de Participación:

<table>
  <tbody>
    <tr>
      <th>Integrantes</th>
      <th align="center">Participación</th>
    </tr>
    <tr>
      <td>Franco Pacheco Espino</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Nincol Abraham Quiroz Maquin</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Johannes Albert Segundo Loayza Huamán</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Fabian Martin Alvarado Vargas</td>
      <td align="center">100%</td>
    </tr>
  </tbody>
</table>

# Objetivo:
En este proyecto buscamos crear un motor de busqueda que pueda recibir una query textual en lenguaje natural y usarla para buscar textos similares en nuestra base de datos tweets en formato JSON proporcionados por el profesor, rankeando los resultados mediante un score. Este proceso se dará aplicando los conceptos aprendidos en clase como el índice invertido, similitud de cosenos, normalización de términos, SPIMI, entre otros. Y finalmente vamos a medir el tiempo que tarda esta filtración de información aplicada con código en Python y lo compararemos con el tiempo que tarda hacerlo el gestor de bases de datos PostgreSQL.



# Backend

## Dataset
El dataset contiene una coleccion de 479945 tweets (casi medo millón) proporcionados por el profesor, de los cuales recuperaremos los mas relevantes que se asemejen a una query dada por un usuario. El dataset fue obtenido de: [![Dataset]()](https://onedrive.live.com/?authkey=%21AARlFTKCCvDtnOQ&id=C2923DF9F1F816F%2150804&cid=0C2923DF9F1F816F)
El nombre del archivo utilizado (en caso sea actualizado) es: "dataset.zip" y consta de
59 archivos en formato JSON que contienen la cantidad de tweets mencionada.

Campos del archivo de datos escogido:
* id
* date
* text
* user_id
* user_name
* location
* retweeted

Y dependiendo si retweeted es verdadero o falso, también:
* RT_text
* RT_user_id
* RT_user_name


## Inverted index
Es un método para estructurar la información más importante de un texto completo. La composición se da mediante un documento el cual tiene términos con una determinada frecuencia. En el caso del proyecto la información de la base de datos es organizada para retornar datos de una forma rápida y óptima. La consulta enviada también se procesa y organiza de la misma manera, posteriormente se genera un score de similitud con todos los documentos de la base de datos antes descritos. Finalmente se devuelven los documentos con mayor score los cuales se consideran más importantes.

## Funciones importantes
A continuación explicaremos brevemente las funciones más importantes de nuestra implementación.

### Clase principal
Es una clase que contiene todas las funciones necesarias para procesar la query los archivos de datos de tweeter y crear los archivos de metadata.
```python
class DataRecovery():
```

### Función init
El constructor en primera instancia lo que hará es leer los stopwords de un archivo de texto.
```python
def __init__(self):
```


### Función load
Esta función procesa todos los datos de los archivos JSON y se basa en algoritmo SPIMI (Single Pass In Memory Indexing). Extrae todos los términos importantes evitando todos los stopwords de la lista dada y va generando un índice para cada término el cual contiene todos los tweets que lo contienen con su frecuencia respectiva, y posteriormente su IDF. Estos diccionarios tienen un límite de tamaño, el cual si es superado pasa a memoria secundaria guardando en archivos auxiliares. Finalmente  se realiza el merge de los archivos auxiliares creados que posteriormente elimina y coloca en un Priority Queue que luego unificará en un archivo con el indice invertido completo (big index), eliminando los archivos auxiliares, además durante el procesamiento se va guardando la norma de estos términos en otro archivo en memoria secundaria.

```python
def load(self):
```

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/load.jpeg)

### Función score
Esta función descarta los stopwords y aplica el stemmer en la query para obtener sus terminos raiz que se podrian encontrar en el indice invertido, utilizando los valores TF IDF de los terminos y la similitud de coseno traerá los tweets más parecidos a la query. Luego utilizaremos la  función retrieve_k_tweets para devolver un ranking top k de estos mismos tweets.

```python
def score(self, query):
```

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/score.jpeg)

### Función retrieve
Finalmente esta función retorna solo los k tweets más parecidos a la query.

```python
def retrieve_k_tweets(self, k):
```

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/retrieve.jpeg)

# Frontend
Para el frontend se utilizó html, css (bootstrap) y javascript. La aplicación web tiene dos vistas: una principal (index.html) que solo recibe la query y el valor de k (cantidad de resultados que se van a recuperar), y otra que es la que muestra los resultados tanto del codigo python como de postgres y sus respectivos tiempos (retrieve.html).

### Imagen de la vista principal:

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/frontend1.png)

### Imagenes de la vista retrieve:

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/frontend2.png)

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/frontend3.png)

## Diseño de indice PostgreSQL
### Función load_data_in_postgres
Se utilizó la librería de Python psycopg2 para la creación de la tabla he indice GIN en una base de datos llamada proyecto2BD2 en postgreSQL.

Primero se crea una conección con el nombre de la base de datos (proyecto2BD2) y el usuario de postgres y su contraseña (que se deben de modificar manualmente en el archivo Postgres.py), luego los datos se crea la tabla tweets con los campos: t_id BIGINT, t_date TEXT, t_text TEXT, user_id BIGINT, user_name TEXT. Se copian los datos de los archivos JSON, y luego de agrega la columna search_text de tipo tsvector que se hará update para cada fila de la tabla tweets. Finalmente se crea el indice GIN tweet_idx_search con los valores de la columna search_text para la tabla tweets.
```python
def load_data_in_postgres():
```

### Función postgres_retrieve_k
Crea una conección con la base de datos igual que la función anterior y solo ejecuta una consulta que hace uso del indice GIN creado y devuelve los k tweets con mayor score según el indice para una query, devuelve sus campos t_id, t_text y ts_rank_cd que es como su score, luego ejecuta explain analyze para tambien retornar cuanto tiempo demora la consulta.
```python
def postgres_retrieve_k(query, k):
```

## Comparación de tiempo
Se hicieron pruebas experimentales con diferentes querys en lenguaje natural y diferentes valores de k de la cantidad de resultados aproximados a retornar para ambas implementaciones en python y postgreSQL.

Las querys utilizadas (todas tienen que ver con el tema recurrente de los tweets, que era las elecciones municipales de 2018) fueron las siguientes:
```python
query1 = "Que buena la de Velarde. Ojala lo impulse hacia arriba en las encuestas, aunque quiza ya sea tarde, una pena"
query2 = "Estas próximas elecciones es la mejor oportunidad para sacar a los corruptos de la administración pública"
query3 = "Ese Reggiardo de alto al crimen fue fujimorista y el hijo de Castañeda debe ser tan corrupto como su viejo"
query4 = "Yo voy a votar por Jorge Munoz ahora con mas ganas luego de ver lo soberbio, patan e intolerante de Urresti"
query5 = "Urresti no es mejor que Beingolea para ser alcalde, no puede ser que un corrupto y homicida salga elegido"
```

Y se tomó valores de k en escala logaritmica, lo que dió los siguientes resultados:

![Image text](https://github.com/dipolo12q/bdd2Proyecto2/blob/main/src/cuadro.jpg)

Se puede apreciar que el rendimiento de PostgreSQL es mejor en general. También se notó que algunos resultados de ambas implementaciones retornaban tweets que solo contenían el término más común de la query. 

# Video
[carpeta](https://drive.google.com/drive/folders/1XmRxondQuUs3ywY7qSe2BCrGSxdJkapz?usp=sharing)
