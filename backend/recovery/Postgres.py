import psycopg2
import json
import io
from os import listdir, remove, getcwd
from os.path import isfile, join

#reemplazar con la ruta en su computador
path = "D:\\UTEC\Base de Datos 2\proyecto2\\backend\\recovery\data\data_in"

def load_data_in_postgres():
    try:
        conection = psycopg2.connect(host="localhost", database="proyecto2BD2", user="postgres", password="Franco71422229")
        cursor = conection.cursor()

        cursor.execute('DROP TABLE IF EXISTS tweets')
        cursor.execute('''CREATE TABLE tweets(
                            t_id BIGINT,
                            t_date TEXT,
                            t_text TEXT,
                            user_id BIGINT,
                            user_name TEXT)
                        ''')

        cursor.execute("SET enable_seqscan = off") #sirve para que la query sea mas rapida

        for f in listdir(path):
            file_in = join(path, f)
            if isfile(file_in):
                with open(file_in, 'r', encoding="utf-8") as file_to_load:
                    for tweet in file_to_load: # a line is a document
                        tweet = tweet.rstrip()
                        json_tweet = json.load(io.StringIO(tweet))
                        tweet_id = json_tweet.get("id")
                        tweet_date = json_tweet.get("date")
                        tweet_text = json_tweet.get("text").lower() if json_tweet.get(
                            "RT_text") == None else json_tweet.get("RT_text").lower()
                        tweet_uid = json_tweet.get("user_id")
                        tweet_uname = json_tweet.get("user_name")

                        postgres_insert_query = '''INSERT INTO tweets (t_id,
                                                                        t_date,
                                                                        t_text,
                                                                        user_id,
                                                                        user_name) 
                                                    VALUES (%s,%s,%s,%s,%s)'''
                        record_to_insert = (tweet_id, tweet_date, tweet_text, tweet_uid, tweet_uname)
                        cursor.execute(postgres_insert_query, record_to_insert)

        cursor.execute("ALTER TABLE tweets ADD COLUMN search_text tsvector")

        cursor.execute('''update tweets set 
                            search_text = X.weight 
                            from (
                                select t_id, 
                                        setweight(to_tsvector('spanish', coalesce(t_text, '')), 'A') 
                                        as weight 
                                from tweets
                            ) as X 
                            where X.t_id = tweets.t_id;
                        ''')

        cursor.execute('DROP INDEX IF EXISTS tweet_idx_search')
        cursor.execute("create index tweet_idx_search on tweets using GIN (search_text);")

        conection.commit()
        cursor.close()
        conection.close()
        print("Datos cargados e indice GIN creado en una tabla PostgreSQL")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conection is not None:
            conection.close()
            print('conexion terminada')


def postgres_retrieve_k(query, k):
    # process query
    query = query.replace(" ", " or ")
    documents_to_retrieve = []

    try:
        conection = psycopg2.connect(host="localhost", database="proyecto2BD2", user="postgres", password="Franco71422229")
        cursor = conection.cursor()

        postgres_insert_query = '''select t_id,
                                            t_text, 
                                            ts_rank_cd(search_text, query) as score 
                                        from tweets, 
                                                websearch_to_tsquery('english', %s) query 
                                        where query @@ search_text 
                                        order by score 
                                        desc limit %s;'''
        record_to_insert = (query, str(k))
        cursor.execute(postgres_insert_query, record_to_insert)

        list_of_tuples = cursor.fetchall()

        postgres_insert_query = '''explain analyze select t_id,
                                            t_text, 
                                            ts_rank_cd(search_text, query) as score 
                                        from tweets, 
                                                websearch_to_tsquery('english', %s) query 
                                        where query @@ search_text 
                                        order by score 
                                        desc limit %s;'''
        record_to_insert = (query, str(k))
        cursor.execute(cursor.mogrify(postgres_insert_query, record_to_insert))

        analyzed_fetched = cursor.fetchall()

        execution_time1 = analyzed_fetched[-1]
        planning_time1 = analyzed_fetched[-2]

        execution_time = execution_time1[0].replace("Execution Time: ", "")
        execution_time = execution_time.replace(" ms", "")

        for tup in list_of_tuples:
            temp_doc = {}
            temp_doc["tweet_id"]      = tup[0]
            temp_doc["text"]   = tup[1]
            temp_doc["score"]   = tup[2]
            documents_to_retrieve.append(temp_doc)

        conection.commit()
        cursor.close()
        conection.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conection is not None:
            conection.close()
            print('conexion terminada')
            return documents_to_retrieve, execution_time
