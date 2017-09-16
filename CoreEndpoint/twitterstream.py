from gpucelery import Twitter_ToGPU_paint
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
import json
import random
import os

consumer_key = os.environ.get        ("TWITTER_consumer_key")
consumer_secret = os.environ.get     ("TWITTER_consumer_secret")
access_token_key = os.environ.get    ("TWITTER_access_token_key")
access_token_secret = os.environ.get ("TWITTER_access_token_secret")


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):	
        Twitter_ToGPU_paint (api, data)
#        json_data= json.loads(data)
#        print(json_data)
#        tweeter_name = json_data['user']['screen_name']
#        status = "(@%s thanks for the mention and random number %f" % (tweeter_name, random.random())
#        api.update_status(status)
        return True

    def on_error (self, status):
        print (status)


stream_listener = StdOutListener()


stream = Stream(auth, stream_listener)
stream.filter(track=['#SmartBotNC'])
