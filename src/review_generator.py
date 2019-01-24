from hiking_data_v1 import my_tokenizer
import tensorflow as tf
import pandas as pd
import nltk
import gensim
from gensim import corpora, models, similarities
from gensim.models import phrases

def word2vecmodel_gensim(text):
    corpus = text.values.tolist()
    bigrams = phrases.Phrases(corpus)
    model = gensim.models.Word2Vec(bigrams, min_count=10, size = 100)
    return model
        
    

