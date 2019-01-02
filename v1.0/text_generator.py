from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
import keras.utils as ku 
import numpy as np
from nltk.tokenize import RegexpTokenizer

def my_tokenizer(doc):
    tokenizer = RegexpTokenizer(r'\w+')
    article_tokens = tokenizer.tokenize(doc.lower())
    return article_tokens

