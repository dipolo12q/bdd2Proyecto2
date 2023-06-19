import numpy as np
import pandas as pd
import json
import io
from os import listdir, remove
from os.path import isfile, join
import linecache
from queue import PriorityQueue
from nltk.tokenize.toktok import ToktokTokenizer #tokenizador que ya puede filtrar simbolos y caracteres raros
from nltk.stem.snowball import SnowballStemmer

# for backend:
path_data = "recovery/data/"
# for test:
#path_data = "data/"

path_file_data = path_data + "data.json"
path_data_in = path_data + "data_in/"
path_stop_list = path_data + "stoplist.txt"
MAX_TERMS_IN_MAP = 1000000
MAX_SIZE_OF_PAGE = 10
path_data_aux = path_data + "data_aux/"
path_file_aux = path_data + "data_aux/aux"
path_file_aux_end = ".json"
path_norm_doc = path_data + "norm.json"


def process_word(word):
    letras = "abcdefghijklmnopqrstuvwxyzñáéíóú"
    new_word = ""
    for c in word:
        if c in letras:
            new_word = new_word + c
        else:
            new_word = new_word + '.'
    return new_word.strip('.')


class DataRecovery():
    stopList = []
    stemmer = SnowballStemmer('spanish')
    tokenizer = ToktokTokenizer()
    N = 0  # Cantidad de tweets
    Nterms = 0  # Cantidad de terminos

    map_score = {}
    list_keys = []
    map_tweets = {}

    def __init__(self):
        self.stopList.clear()
        with open(path_stop_list, 'r', encoding="latin-1") as file:
            self.stopList = [line.lower().strip() for line in file]
        with open(path_norm_doc, 'r', encoding="utf-8") as file:
            self.N = sum(1 for line in file)
        with open(path_file_data, 'r', encoding="utf-8") as file:
            self.Nterms = sum(1 for line in file)

    def ini(self):
        return "Hay en memoria " + str(self.Nterms) + " términos y " + str(self.N) + " tweets procesados"

    def __getStem(self, word):
        return self.stemmer.stem(word.lower())

    def __save_in_file_aux(self, local_map, path):
        local_map_keys = local_map.keys()
        local_map_keys = sorted(local_map_keys)
        with open(path, 'w', encoding="utf-8") as file_aux_out:
            for key in local_map_keys:
                file_aux_out.write(json.dumps(
                    {key: local_map[key]}, ensure_ascii=False))
                file_aux_out.write("\n")

    def __save_in_file_norm(self, frecuency_map, id):
        with open(path_norm_doc, 'a', encoding="utf-8") as file_norm_out:
            values=[]
            for key, val in frecuency_map.items():
                values.append(val)
            norm = np.linalg.norm(values)
            file_norm_out.write(json.dumps({id: norm}, ensure_ascii=False))
            file_norm_out.write("\n")

    def __get_item_from_json_line(self, line):
        item_json = json.load(io.StringIO(line))
        keys = list(item_json.keys())
        return [keys[0], list(item_json.get(keys[0]).items())]

    def load(self):
        tmp = open(path_file_data, 'w').close()
        tmp = open(path_norm_doc, 'w').close()
        local_map = {}
        size_of_local_map = 0
        id_file_aux = 1
        size = 0
        self.N = 0
        print("Generando archivos auxiliares")
        for f in listdir(path_data_in):
            file_in = join(path_data_in, f)
            if isfile(file_in):
                with open(file_in, 'r', encoding="utf-8") as file_to_load:
                    for tweet in file_to_load:
                        tweet = tweet.rstrip()
                        json_tweet = json.load(io.StringIO(tweet))
                        tweet_id = json_tweet.get("id")
                        tweet_text = json_tweet.get("text").lower() if json_tweet.get(
                            "RT_text") == None else json_tweet.get("RT_text").lower()
                        tweet_words = self.tokenizer.tokenize(tweet_text)
                        frecuency_map = {}
                        for tweet_word in tweet_words:
                            if tweet_word in self.stopList:
                                continue
                            tweet_word = process_word(tweet_word)
                            if tweet_word == "":
                                continue
                            if '.' in tweet_word:
                                pos = tweet_word.find('.')
                                rest_word = tweet_word[pos+1:]
                                if rest_word != "":
                                    tweet_words.append(rest_word)
                                tweet_word = tweet_word[:pos]
                            if tweet_word == "":
                                continue
                            if tweet_word in self.stopList:
                                continue
                            tweet_word_root = self.__getStem(tweet_word)
                            if tweet_word_root in local_map:
                                if tweet_id in local_map[tweet_word_root]:
                                    local_map[tweet_word_root][tweet_id] = local_map[tweet_word_root][tweet_id] + 1
                                else:
                                    size = size + 1
                                    local_map[tweet_word_root][tweet_id] = 1
                                    size_of_local_map = size_of_local_map + \
                                        len(str(tweet_id)) + 6
                            else:
                                size = size + 1
                                local_map[tweet_word_root] = {tweet_id: 1}
                                size_of_local_map = size_of_local_map + \
                                    len(str(tweet_id)) + 1 + \
                                    len(tweet_word_root) + 8
                            if size_of_local_map > MAX_TERMS_IN_MAP:
                                self.__save_in_file_aux(local_map, path_file_aux + str(id_file_aux) + path_file_aux_end)
                                local_map.clear()
                                size_of_local_map = 0
                                id_file_aux += 1
                            if tweet_word_root in frecuency_map:
                                frecuency_map[tweet_word_root] += 1
                            else:
                                frecuency_map[tweet_word_root] = 1
                        self.__save_in_file_norm(frecuency_map, tweet_id)
                        self.N += 1
        if len(local_map) > 0:
            self.__save_in_file_aux(local_map, path_file_aux + str(id_file_aux) + path_file_aux_end)
        print(str(id_file_aux) + " archivos auxiliares generados. Generando archivo único")
        # Una vez generado los archivos auxiliares, unificarlos. Hay id_file_aux
        # Por cada id_file_aux, generar un buffer de lectura
        read_buffer = []
        number_of_line_buffer = []
        pq = PriorityQueue()
        buffer_remaining = []
        for i in range(id_file_aux):
            line = linecache.getline(path_file_aux + str(i+1) + path_file_aux_end, 1).rstrip()
            if line == "":
                continue
            read_buffer.append(self.__get_item_from_json_line(line))
            number_of_line_buffer.append(2)
            pq.put((read_buffer[i][0], i))
            buffer_remaining.append(i)
        size2 = 0
        self.Nterms = 0
        with open(path_file_data, 'a', encoding="utf-8") as file:
            while not pq.empty():
                term_dic = {}
                cur_term, cur_ind = pq.get()
                term_dic["term"] = cur_term
                term_dic["idf"] = 0
                term_dic["docs"] = []
                for pair in read_buffer[cur_ind][1]:
                    term_dic["docs"].append(pair)
                if cur_ind in buffer_remaining:
                    line = linecache.getline(path_file_aux + str(cur_ind+1) + path_file_aux_end,
                                              number_of_line_buffer[cur_ind]).rstrip()
                    number_of_line_buffer[cur_ind] = number_of_line_buffer[cur_ind] + 1
                    if line == "":
                        buffer_remaining.remove(cur_ind)
                        # Borrar el archivo auxiliar
                        remove(path_file_aux + str(cur_ind + 1) + path_file_aux_end)
                    else:
                        read_buffer[cur_ind] = self.__get_item_from_json_line(
                            line)
                        pq.put((read_buffer[cur_ind][0], cur_ind))
                # Mientras salga el mismo cur_term en pq.get, se agrega a local_map
                while not pq.empty():
                    cur_term_2, cur_ind_2 = pq.get()
                    if cur_term_2 != cur_term:
                        pq.put((cur_term_2, cur_ind_2))
                        break
                    for pair in read_buffer[cur_ind_2][1]:
                        term_dic["docs"].append(pair)
                    if cur_ind_2 in buffer_remaining:
                        line = linecache.getline(path_file_aux + str(cur_ind_2+1) + path_file_aux_end,
                                                  number_of_line_buffer[cur_ind_2]).rstrip()
                        number_of_line_buffer[cur_ind_2] = number_of_line_buffer[cur_ind_2] + 1
                        if line == "":
                            buffer_remaining.remove(cur_ind_2)
                            # Borrar el archivo auxiliar
                            remove(path_file_aux + str(cur_ind_2 + 1) + path_file_aux_end)
                        else:
                            read_buffer[cur_ind_2] = self.__get_item_from_json_line(line)
                            pq.put((read_buffer[cur_ind_2][0], cur_ind_2))
                term_dic["idf"] = np.log10(self.N/len(term_dic["docs"]))
                size2 += len(term_dic["docs"])
                file.write(json.dumps(term_dic, ensure_ascii=False))
                file.write("\n")
                self.Nterms += 1
        print(str(self.Nterms) + " términos encontrados")
        print(str(self.N) + " tweets procesados")
        return "Invert index created. " + str(self.Nterms) + " términos encontrados. " + str(self.N) + " tweets procesados"

    def __search_term_in_data(self, query_map):
        # query map es un mapa de semanticas con frecuencias
        # esta es una implementacion con busqueda binaria
        map_to_return = {}
        for word in query_map:
            lo = 1
            hi = self.Nterms
            while lo <= hi:
                mi = (hi + lo) // 2
                line = linecache.getline(path_file_data, mi).rstrip()
                term_json = json.load(io.StringIO(line))
                term_ = term_json.get("term")
                if term_ < word:
                    lo = mi + 1
                elif term_ > word:
                    hi = mi - 1
                else:
                    map_to_return[word] = dict(term_json)
                    break
        return map_to_return

    def __search_tweet_norm(self, set_tweet_id):
        map_to_return = {}
        with open(path_norm_doc, 'r', encoding="utf-8") as file:
            for line in file:
                line = line.rstrip()
                json_term = json.load(io.StringIO(line))
                keys = list(json_term.keys())
                if keys[0] in set_tweet_id:
                    map_to_return[keys[0]] = json_term.get(keys[0])
        return map_to_return

    def __recover_tweets(self, score):
        map_to_return = {}
        for f in listdir(path_data_in):
            file_in = join(path_data_in, f)
            if isfile(file_in):
                with open(file_in, 'r', encoding="utf-8") as file_to_load:
                    for tweet in file_to_load:
                        tweet = tweet.rstrip()
                        json_tweet = json.load(io.StringIO(tweet))
                        if str(json_tweet.get("id")) in score:
                            map_to_return[str(json_tweet.get("id"))] = json_tweet
        return map_to_return

    def score(self, query):
        if self.N == 0:
            print("No hay tweets procesados")
            return "No hay tweets procesados"
        query = query.lower()
        query_words = self.tokenizer.tokenize(query)
        query_map = {}
        for word in query_words:
            if word in self.stopList:
                continue
            word = process_word(word)
            if word == "":
                continue
            if '.' in word:
                pos = word.find('.')
                rest_word = word[pos+1:]
                if rest_word != "":
                    query_words.append(rest_word)
                word = word[:pos]
            if word == "":
                continue
            if word in self.stopList:
                continue
            query_root_word = self.__getStem(word)
            if query_root_word in query_map:
                query_map[query_root_word] += 1
            else:
                query_map[query_root_word] = 1

        self.map_score.clear()
        self.map_tweets.clear()
        self.list_keys.clear()

        map_terms = self.__search_term_in_data(query_map)

        query_vec = []
        for term in query_map.keys():
            term_inv_idx = map_terms[term]
            if not term_inv_idx:
                query_vec.append(0)
                continue
            tf = query_map[term]
            idf = term_inv_idx["idf"]
            query_vec.append(np.log10(tf+1) * idf)
        
        query_vec = np.array(query_vec)
        query_vec = query_vec/np.linalg.norm(query_vec, 2)
        
        map_term_tweet_tf = {}
        for term in query_map.keys():
            map_tweet_tf = {}
            term_inv_idx = map_terms[term]
            if not term_inv_idx:
                continue
            term_tweet_tf = term_inv_idx["docs"]
            map_tweet_tf = {x[0]:x[1] for x in term_tweet_tf}
            map_term_tweet_tf[term] = map_tweet_tf

        #filtrar tweet ids repetidos
        query_set_tweet_ids = set()
        for term in query_map.keys():
            term_inv_idx = map_terms[term]
            if term_inv_idx:
                ids = map_term_tweet_tf[term]
                query_set_tweet_ids.update(ids.keys())

        map_tweet_norm = self.__search_tweet_norm(query_set_tweet_ids)
        map_tweets_vecs = {}
        for tweet in query_set_tweet_ids:
            tweet_vec = []
            for term in query_map.keys():
                term_inv_idx = map_terms[term]
                if not term_inv_idx:
                    tweet_vec.append(0)
                    continue
                tweet_tf = map_term_tweet_tf[term]
                if tweet_tf:
                    tf = tweet_tf.get(tweet, 0)
                    idf = term_inv_idx["idf"]
                    tweet_vec.append(np.log10(tf+1) * idf)
                else:
                    tweet_vec.append(0)
            tweet_vec = np.array(tweet_vec)
            tweet_vec /= map_tweet_norm[tweet]
            map_tweets_vecs[tweet] = tweet_vec

        for document, vector in map_tweets_vecs.items():
            self.map_score[document] = np.dot(query_vec, vector)

        self.map_score = dict(sorted(self.map_score.items(), key=lambda item: item[1], reverse=True))
        self.map_tweets = self.__recover_tweets(self.map_score)
        print(len(self.map_tweets), " tweets recuperados")
        self.list_keys = list(self.map_score.keys())
        return len(self.map_tweets)

    def retrieve_k_tweets(self, k):
        result = {}
        for i in range(k):
            if i >= len(self.list_keys):
                break
            result_tweet = {}
            result_tweet['tweet_id'] = self.list_keys[i]
            result_tweet['position'] = i
            result_tweet['score'] = self.map_score[self.list_keys[i]]
            result_tweet['date'] = self.map_tweets[self.list_keys[i]].get('date')
            result_tweet['user_id'] = self.map_tweets[self.list_keys[i]].get('user_id')
            result_tweet['user_name'] = self.map_tweets[self.list_keys[i]].get('user_name')
            result_tweet['text'] = self.map_tweets[self.list_keys[i]].get('text')
            result[self.list_keys[i]] = result_tweet
            if(len(result.keys()) <= 0):
                return None
        return result.values()
