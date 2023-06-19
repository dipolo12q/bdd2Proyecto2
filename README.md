# bdd2Proyecto2

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
El dataset contiene información sobre un conjunto muy grande de artículos académicos de los cuales solo extraeremos los más importantes correspondientes a una query
El dataset fue obtenido de: [![Dataset]()](https://onedrive.live.com/?authkey=%21AARlFTKCCvDtnOQ&id=C2923DF9F1F816F%2150804&cid=0C2923DF9F1F816F)
El nombre del archivo utilizado (en caso sea actualizado) es: "tweets_2018.json"
Metadata del archivo de datos escogido:
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
Sin embargo, la data más relevante corresponde a los campos "id" y "text" que son las utilizadas en el caso de este proyecto.

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
Esta función procesa todos los datos del json. Extrae todos los términos importantes evitando todos los stopwords de la lista dada y va generando índice para cada término el cual contiene todo los tweets que lo contienen y su frecuencia respectiva. Estos diccionarios tienen un límite de tamaño, el cual si es superado pasa a memoria secundaria guardando en archivos secundarios y durante el procesamiento se va guardando la norma de estos términos.

Finalmente  se realiza el merge de los archivos auxiliares creados que posteriormente elimina y finalmente este merge lo coloca en un Priority Queue. Estos datos dependiendo de los parámetros que inserte el usuario posteriormente nos serán útiles para retornar los primeros k resultados más similares a una query. 

```python
def load(self):
```

### Función score
Esta función descarta los stopwords antes procesados por el constructor y traerá los documentos científicos más parecidos a la query. Luego utilizaremos la  función tf_idf_weight_and_cosine_score para devolver un ranking de estos mismos documentos.
```python
def score(self, query):
```

### Función retrieve
Finalmente esta función retorna solo los k documentos más parecidos a la query.
```python
def retrieve_k_tweets(self, k):
```

# Frontend
Para el frontend se utilizó html y bootstrap. También se utilizó el motor de plantillas de jinja2 para poder manejar la cantidad de documentos similares a la consulta del usuario. 

## Comparación de tiempo
Para esta sección nos apoyamos de las variables que usamos en nuestra clase de indice invertido, con el print de estas variables obtuvimos datos relevantes como accesos a memoria en general y tiempo, de acuerdo al siguiente query obtuvimos los siguientes resultados:

Posteriormente a esto guardaremos los datos de tiempo y cantidad de datos, esto nos ayudará a ver una comparativa entre el índice invertido en python y el de GIN de postgres.

![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/Resultado3.PNG)

Para la creación de la gráfica usamos el logaritmo de los valores para tener un gráfico más apreciable. Finalmente podemos notar que, para el query analizado, el índice invertido realizado en python es mejor para datos pequeños, pasada una cantidad de datos de 90 000 aproximadamente (inflexión), el indice GIN de postgres empieza a tener un mejor rendimiento en adelante.

# Video
[carpeta](https://drive.google.com/drive/folders/1XmRxondQuUs3ywY7qSe2BCrGSxdJkapz?usp=sharing)
