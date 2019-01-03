from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
import keras.utils as ku 
import numpy as np
import re

tokenizer = Tokenizer()

def data_prep(dataframe, trail_id):
    text = '. '.join(dataframe[dataframe['trail_id'] == trail_id]['body'])
    corpus = re.split('(?<=[.!?]) +', text.lower())
    tokenizer.fit_on_text(corpus)
    total_words = len(tokenizer.word_index)+1
    input_sequences = []
    for sent in corpus:
        token_list = tokenizer.texts_to_sequences([sent])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[:i+1]
            input_sequences.append(n_gram_sequence)
    return input_sequences
    
