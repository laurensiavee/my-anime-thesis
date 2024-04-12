import numpy as np 
import pandas as pd 
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel

def get_rec_content_based(id, anime_subset, indices_id, cosine_sim_soup):
    idx = indices_id[int(id)]
    
    sim = list(enumerate(cosine_sim_soup[idx]))
    sim = sorted(sim, key=lambda x: x[1], reverse=True)
    sim = sim[1:11]

    anime_indices = [i[0] for i in sim]
    list_id = []

    for a in anime_indices:
        list_id.append(str(anime_subset['anime_id'].iloc[a]))

    return list_id