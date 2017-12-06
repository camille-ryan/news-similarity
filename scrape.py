import requests
import json
import itertools
from bs4 import BeautifulSoup, UnicodeDammit
from datetime import datetime, timedelta
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API

# Load keys and news sources
with open("keys") as f:
    keys = f.readlines()

with open("sources") as f:
    pubs = f.readlines()
    
embed_rocks_key = keys[0]
#twitter
consumer_key = keys[1]
consumer_secret = keys[2]
access_token = keys[3]
access_token_secret = keys[4]

# Auth to Twitter
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Use embed.rocks API to process raw html
def getBody(url):
    url = ('https://api.embed.rocks/api/?'
           'url={}'
           '&key={}'.format(url, embed_rocks_key))
    r = requests.get(url)
    if r.ok:
        article = json.loads(r.content)
        if 'article' in article.keys():
            article['article'] = BeautifulSoup(article['article']).text
            return article
        else:
            print datetime.now(), " failed to fetch ", url
            return None

# Listen to Twitter for new articles and save the articles to a jsonlines file.
class NewsListener(StreamListener):
    def on_status(self, status):
        try:
            for u in status.entities['urls']:
                if 'expanded_url' not in u.keys():
                    next
                url = u['expanded_url']
                r = requests.head(url, allow_redirects=True)
                url = r.url
                if ('twitter.com' in url) or ('facebook.com' in url) or ('youtube.com' in url) or (('haaretz' in url) and ('premium in url')):
                    next
                else: 
                    article = getBody(r.url)
                    with open("news.jsonl", "a") as out:
                        out.write(json.dumps(article) + "\n")
                    print datetime.now(), " fetched ", r.url
        except:
            pass


# Run the twitter streaming API
newsListener = NewsListener()
stream = Stream(auth = api.auth, listener=newsListener)
stream.userstream(pubs)
