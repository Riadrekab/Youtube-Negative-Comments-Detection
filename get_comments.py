#import de scrapping des commentaires
import os
import googleapiclient.discovery
import time
from googleapiclient import errors
#import de preprocessing
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
#import de langage
from lingua import Language, LanguageDetectorBuilder
#import de bdd
import pymongo
 
def main():
    #récuperation de la database
    db = get_database()
    col = db["comments"]
    #preprocessing et detection de langage
    load()
    languages = [Language.ENGLISH,Language.FRENCH]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyCmu47FHSHKHr2c8Ljy9Sp_HRugFqj-SG4"
    comments = []
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)


    query_videos = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        maxResults=100,
        regionCode="GB"
    )
    
    response_videos = query_videos.execute()

    for video in response_videos["items"]:
        id = video["id"]
        
        if "commentCount" in video["statistics"]:
            
            query = youtube.commentThreads().list(
                part="snippet, replies",
                maxResults=100,
                videoId=id
            )
                
            response = query.execute()
            while "nextPageToken" in response:
                for item in response["items"]:
                    if "textDisplay" in item["snippet"]["topLevelComment"]["snippet"]:
                        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                        confidence_value = detector.compute_language_confidence(comment, Language.ENGLISH)
                        if(confidence_value>=0.8):
                            comment = preprocess(comment)
                            x = col.insert_one(list_to_dic(comment))
                            if "replies" in item:
                                for reply in item["replies"]["comments"]:
                                    comment2 = reply["snippet"]["textDisplay"]
                                    confidence_value = detector.compute_language_confidence(comment2, Language.ENGLISH)
                                    if(confidence_value>=0.8):
                                        comment2 = preprocess(comment2)
                                        x = col.insert_one(list_to_dic(comment2))
                                        
                query = youtube.commentThreads().list(
                    part="snippet, replies",
                    maxResults=100,
                    videoId=id,
                    pageToken=response["nextPageToken"]
                )
                response = query.execute()
                print("Number of comments : \n",len(comments)," \n")
                time.sleep(9)
            
        else:
            pass

        
    print(len(comments))
    
def list_to_dic(list):
       return {"words" : list}

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

def lemmatize_text(text,words_tokenizer,lemmatizer):
  return [(lemmatizer.lemmatize(w)) for w \
                       in words_tokenizer.tokenize((text))]
      
def preprocess(sample):
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
    
def get_database():

    CONNECTION_STRING = "mongodb+srv://comments:SSxO2BV1HfOJXxs9@cluster0.nbxckzp.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)
    
    return client['comments_db']
  

if __name__ == "__main__":
    main()