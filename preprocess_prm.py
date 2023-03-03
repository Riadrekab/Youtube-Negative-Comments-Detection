# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 00:06:55 2023

@author: Y K
"""

import preprocess_prm
import nltk
nltk.download('omw-1.4',quiet=True)
import preprocessor as p
import re
nltk.download('wordnet',quiet=True)
nltk.download('stopwords',quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from wordsegment import load, segment


#sources : https://towardsdatascience.com/basic-tweet-preprocessing-in-python-efd8360d529e
#          https://www3.tuhh.de/sts/hoou/data-quality-explored/3-2-simple-transf.html

#retirer ponctuation et nombres, décomposer les hashtag et les garder en tant que mots normaux
def remove_punctuation_numbers_keep_hashtag(words):
 new_words = []
 hashtags = []
 for word in words:
    new_word = re.sub(r'\d','',(word))
    if(new_word.startswith('#')):
        new_word = re.sub(r'[^\w\s]', '', (new_word))
        hashtags = segment(new_word)
        for element in hashtags:
            if(element != ''):
                new_words.append(element)
    else:
        new_word = re.sub(r'[^\w\s]', '', (new_word))
        if new_word != '':
           new_words.append(new_word)
 return new_words

#transformer le mot en sa forme canonique la plus commune
def lemmatize_text(text,words_tokenizer,lemmatizer):
  return [(lemmatizer.lemmatize(w)) for w \
                       in words_tokenizer.tokenize((text))]

#main
def main(sample):
        text = sample
        result=[]
        p.set_options(p.OPT.URL,p.OPT.MENTION,p.OPT.RESERVED,p.OPT.EMOJI,p.OPT.SMILEY,p.OPT.NUMBER)   
        text = p.clean(text)
        text = text.replace('\d+', '')
        text = text.lower()
        lemmatizer = WordNetLemmatizer()
        words_tokenizer =  TweetTokenizer()
        text=lemmatize_text(text,words_tokenizer,lemmatizer)
        text=remove_punctuation_numbers_keep_hashtag(text)
        stop_words = set(stopwords.words("english"))
        for element in text:
            element = re.sub(r'([A-Za-z])\1{2,}', r'\1', element)
            if(element not in stop_words):
                result.append(element)
        return result
    

