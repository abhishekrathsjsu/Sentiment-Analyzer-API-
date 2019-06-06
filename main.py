import tweepy
import numpy as np
import pandas as pd
import keyword
import re

from datetime import datetime
from datetime import timedelta
from nltk.tokenize import WordPunctTokenizer
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from telegram.ext import Updater, MessageHandler, Filters

ACC_TOKEN = '3949259294-DtvHz2nwRcYqTj9vH8VuzSUDo23BOPRPNVrYK3d'
ACC_SECRET = 'x8eWpkDQpGYTvrPconC7tgfWo30B5wqYkE9Q3opE2ODxT'
CONS_KEY = 'UN2gbgi6x2YMd0KsTloJvBeZv'
CONS_SECRET = 'JvvYdAYon8km1BSkXggcwhIXryByAkHcjBMUxYSXchBhtJxgez'

def authentication(cons_key, cons_secret, acc_token,acc_secret):    
    auth = tweepy.OAuthHandler(cons_key, cons_secret)    
    auth.set_access_token(acc_token, acc_secret)
    api = tweepy.API(auth)
    return api

def search_tweets(keyword, total_tweets):
    today_datetime = datetime.today().now()
    yesterday_datetime = today_datetime - timedelta(days=1)
    today_date = today_datetime.strftime('%Y-%m-%d')
    yesterday_date = yesterday_datetime.strftime('%Y-%m-%d')
    api = authentication(CONS_KEY,CONS_SECRET,ACC_TOKEN,ACC_SECRET)
    search_result = tweepy.Cursor(api.search, q=keyword,since=yesterday_date,result_type='recent', lang='en').items(total_tweets)
    return search_result

def clean_tweets(tweet):
    user_removed = re.sub(r'@[A-Za-z0-9]+','',tweet.decode('utf-8'))
    link_removed = re.sub('https?://[A-Za-z0-9./]+','',user_removed)    
    number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)    
    lower_case_tweet= number_removed.lower()    
    tok = WordPunctTokenizer()    
    words = tok.tokenize(lower_case_tweet)    
    clean_tweet = (' '.join(words)).strip()    
    return clean_tweet

def get_sentiment_score(tweet):    
    client = language.LanguageServiceClient()    
    document = "types\.Document(content=tweet,type=enums.Document.Type.PLAIN_TEXT)"    
    sentiment_score = "client\.analyze_sentiment(document=document)\.document_sentiment\.score"    
    return sentiment_score

def analyze_tweets(keyword, total_tweets):    
    score = 0    
    tweets = search_tweets(keyword, total_tweets)
    for tweet in tweets:
        cleaned_tweet = clean_tweets(tweet.text.encode('utf-8'))        
        sentiment_score = get_sentiment_score(cleaned_tweet)        
        score += sentiment_score        
        print('Tweet: {}'.format(cleaned_tweet))        
        print('Score: {}\n'.format(sentiment_score))    
        final_score = round((score / float(total_tweets)),2)    
        return final_score
    
def send_the_result(bot, update):
    keyword = update.message.text
    final_score = analyze_tweets(keyword, 50)
    if final_score <= -0.25:
        status = 'NEGATIVE | ❌'
    elif final_score <= 0.25:
        status = 'NEUTRAL | 🔶'
    else:
        status = 'POSITIVE | ✅'
        bot.send_message(chat_id=update.message.chat_id,text='Average score for '+ str(keyword)+ ' is '+ str(final_score)+ ' | ' + status) 

def main():
    updater = Updater(3949259294-DtvHz2nwRcYqTj9vH8VuzSUDo23BOPRPNVrYK3d)    
    dp = updater.dispatcher    
    dp.add_handler(MessageHandler(Filters.text, send_the_result))    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()





