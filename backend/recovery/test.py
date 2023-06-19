from DataRecovery import DataRecovery
import Postgres as pg
import time
from numpy import round_

#instanciacion de DataRecovery carga de datos
dataRecovery = DataRecovery()
#se tiene que volver a hacer la carga si se agrega o quita algun archivo de la carpeta data_in
#dataRecovery.load()

#carga de datos en PostgreSQL
#pg.load_data_in_postgres()

#definiendo parametros de busqueda, se escogio una query larga en lenguaje natural
#para probar la capacidad de los algoritmos implementados, y usaran distintos valores de k
query = "Urresti no es mejor que Beingolea para ser alcalde, no puede ser que un corrupto y homicida salga elegido"
k = 10

#realizando scoring del query y busqueda del top k con python, ademas de medir el tiempo que demora
tstart = time.time()
dataRecovery.score(query)
pyRetrieve = dataRecovery.retrieve_k_tweets(k)
tend = time.time()
pyTime = round_((tend - tstart)*1000, 3)

#realizando busqueda del top k con PostgreSQL
pgRetrieve, pgTime = pg.postgres_retrieve_k(query, k)

#imprimiendo resultados
print("tiempo de python: ", pyTime, " ms")
print("tiempo de postgres: ", pgTime, " ms")
#'''
print()
print("Resultados de Python: ", pyRetrieve)
print()
print("Resultados de PostgreSQL: ", pgRetrieve)
#'''