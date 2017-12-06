import requests
import json
import itertools
from bs4 import BeautifulSoup, UnicodeDammit
from datetime import datetime, timedelta
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import sys

args = sys.argv
# Load keys and news sources
with open('secrets.json', 'r') as f:
    keys = json.loads(f.read())

with open("sources") as f:
    pubs = f.readlines()


# Use embed.rocks API to process raw html
def getBody(url):
    url = ('https://api.embed.rocks/api/?'
           'url={}'
           '&key={}'.format(url, keys['embed_rocks']))
    r = requests.get(url)
    if r.ok:
        article = json.loads(r.content)
        if 'article' in article.keys():
            article['article'] = BeautifulSoup(article['article']).text
            return article
        else:
            if "verbose" in args:
                print datetime.now(), " failed to fetch ", url
            return None

# Listen to Twitter for new articles and save the articles to a jsonlines file.
class NewsListener(StreamListener):
    def set_auth(self, auth):
        self.api = API(auth)

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
                    if "verbose" in args:
                        print datetime.now(), " fetched ", r.url
        except:
            pass




if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    # Auth to Twitter
    auth = OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
    auth.set_access_token(keys["access_token"], keys["access_token_secret"])
    
    # Run the twitter streaming API
    newsListener = NewsListener()
    newsListener.set_auth(auth)
    stream = Stream(auth, listener=newsListener)
    stream.userstream(pubs)


