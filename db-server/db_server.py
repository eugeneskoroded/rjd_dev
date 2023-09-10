import os
os.environ['TRANSFORMERS_CACHE'] = 'volume/cache'
MODEL_NAME = os.environ['MODEL_NAME'] #'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'


import json
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from db_functions import find_top_indexes, distance_compare, get_vectors_and_text

from flask import Flask, request, jsonify

app = Flask(__name__)

gpt_url = 'http://gpt_server:8082/ai_answer' 

model = SentenceTransformer(MODEL_NAME)

error_message = "К сожалению ИИ помощник сейчас недоступен. "
ai_message = "Ответ ИИ. "
search_message = "Выдержка из документации. "

with open("volume/data/database.json", 'r') as json_file:
    database = json.load(json_file)

def start_message(doc_id, ai=False):
    if not ai:
        message = f"Исходя из положения №{doc_id} вам предоставлены наиболее вероятные причины неисправностей и их решения:"
        return search_message + message
    return f"Ответ ассистента был сформулирован исходя данных положения №{doc_id} и наиболее вероятных причин неисправностей содержащихся в нем:"

def prompt_message(response_list, user_problem):
    data = "\n".join(response_list)
    return f"Данные: '''{data}'''. Исходя из данных выбери необходимое решение неисправности опираясь на проблему пользователя: '''{user_problem}''' " 

@app.route('/get_simmilar', methods=['GET'])
def receive_message():
    try:
        data = request.get_json()
        
        message = data['message']
        doc_id = data['document_id']
        ai = data["ai"]

        db = database[str(doc_id)]
        tables, vectors = get_vectors_and_text(db)
        
        embedding = model.encode([message])[0]
        similarities = distance_compare(embedding, vectors)

        if max(similarities) < 0.55:
            return jsonify({'text': "Не получилось найти информацию, попробуйте переформулировать запрос"})
        
        indexes = find_top_indexes(similarities, n=3)
    
        final_tables = [tables[index] for index in indexes]
        
        response_list = []
        for tables in final_tables:
            n, neispravnost, prichina, metod_ust = tables
            table_text = f"Пункт {n}: Неисправность: {neispravnost} -> Причина: {prichina} -> Решение: {metod_ust};"
            response_list.append(table_text)

        if ai:
            prompt = prompt_message(response_list, message)
            data = {'prompt': prompt}
            
            try:
                response = requests.get(gpt_url, json=data).json()["answer"]
                if response:
                    response_text = "\n".join([ai_message, response, search_message, start_message(doc_id, ai=True)] + response_list)
                else:
                    response_text = "\n".join([error_message, start_message(doc_id)] + response_list)
            except:
                response_text = "\n".join([error_message, start_message(doc_id)] + response_list)
                
        else:
            response_text = "\n".join([start_message(doc_id)] + response_list)
        
        return jsonify({'text': response_text})
        
    except Exception as e:
        return jsonify({'text': "Ошибка, пожалуйста, попробуйте другой набор данных", "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8083')