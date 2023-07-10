import pandas as pd
import pickle
import numpy as np
import re
from gensim.models import KeyedVectors
import pymorphy2
from nltk.corpus import stopwords

stopwords = stopwords.words("russian")
pymorph = pymorphy2.MorphAnalyzer()

# Загрузка BOW модели, СЛоваря слов, модели RandomForest, векторов слов 
filename = r"ml_data/BOW.pkl"
with open(filename, 'rb') as file:
    bow_model = pickle.load(file)

filename = r"ml_data/WordsVocab.pkl"
with open(filename, 'rb') as file:
    WordsVocab = pickle.load(file)

filename = r"ml_data/Random_Forest_Model.pkl"
with open(filename, 'rb') as file:
    RandForest = pickle.load(file)

filename = ""
wv = KeyedVectors.load(r"ml_data/word2vec.wordvectors", mmap='r')

# Функция преобразования текста в вектор
def Text2Vec(text_data):
    x = bow_model.transform(text_data)
    CountVecData=pd.DataFrame(x.toarray(), columns=bow_model.get_feature_names_out())

    W2Vec_Data=pd.DataFrame()
    
    for i in range(CountVecData.shape[0]):      
        Sentence = np.zeros(300)

        for word in WordsVocab[CountVecData.iloc[i,:] >= 1]:
            if word in wv.key_to_index.keys():    
                Sentence=Sentence+wv[word]

        W2Vec_Data = pd.concat([W2Vec_Data, pd.DataFrame([Sentence])])
    return(W2Vec_Data)

# Приведение комментария к нормальной форме 
def to_normal_form(comment):
    comment = comment.split() # Разделяем комментарий на слова
    tokens = []
    for token in comment:
        if token and token not in stopwords:
            token = token.strip() # удаляем лишние пробелы в токене
            token = pymorph.normal_forms(token)[0]
            tokens.append(token)
    return tokens

# Функция очистки
def clean_comment(comment):
    clean_pattern = "[A-Za-z0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-\n\“\”]+" # очистка от ненужного
    comment = re.sub(clean_pattern, ' ', comment)
    clean_pattern = "[^А-Яа-я\sA-Za-z]" # для удаления emoji
    comment = re.sub(clean_pattern, ' ', comment)
    return comment

# Функция подготовки комментария для предикта ml моделью
def to_pred_func(comment):  
    comment = clean_comment(comment)
    comment = to_normal_form(comment)
    comment = ' '.join(map(str, comment))
    x = [comment]   
    ml_comment = Text2Vec(x)
    return ml_comment

# Анализ одиночного комментария
def single_comment(comment):
    pred_comm = to_pred_func(comment)
    predict = RandForest.predict(pred_comm)
    return predict[0]

# Анализ множества комментариев
def more_comments(domain):
    comments = pd.read_csv(r'pars_comments/' + domain + '.csv')
    pos_arr = []
    neg_arr = []
    pos_count = 0
    neg_count = 0

    for com in comments['comment']:
        pred_com = to_pred_func(com)
        predict = RandForest.predict(pred_com)
        if predict == 1:
            pos_arr.append(com)
            pos_count += 1
        elif predict == -1:
            neg_arr.append(com)
            neg_count += 1
    
    return pos_arr, neg_arr, pos_count, neg_count