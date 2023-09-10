import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def find_top_indexes(lst, n=3):
    # Create a list of tuples containing (value, index)
    indexed_values = [(value, index) for index, value in enumerate(lst)]
    
    # Sort the list of tuples in descending order based on the values
    sorted_values = sorted(indexed_values, key=lambda x: x[0], reverse=True)

    # Extract the indexes of the top 'n' values
    top_indexes = [index for value, index in sorted_values[:n]]
    
    return top_indexes


def distance_compare(user_vector, case_table_vectors):
    user_vector = np.array(user_vector)

    similarities = []
    for vectors in case_table_vectors:
        vectors = np.array(vectors)

        similarity_matrix = cosine_similarity(user_vector.reshape(1, -1), vectors)
        similarities.append(similarity_matrix.mean())

    return similarities


def get_vectors_and_text(db):
    table, vectors = [], []
    for neispravnost in db.keys():
        neispravnost_embed = db[neispravnost]['vector']
        for prichina in db[neispravnost]['cases'].keys():
            prichina_data = db[neispravnost]['cases'][prichina]

            n = prichina_data['n']
            prichina_embed = prichina_data['vector']
            all_text_embed = prichina_data['common_vector']
            
            metod_ust = prichina_data["Метод устранения"]['text']
            
            table.append([n, neispravnost, prichina, metod_ust])
            vectors.append([neispravnost_embed, prichina_embed, all_text_embed])
    return table, vectors