import os
import requests
import json
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, redirect, url_for, request
from flask_dance.contrib.slack import make_slack_blueprint, slack
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
from gpucelery import ToGPU_paint
from gpucelery import ToGPU_guesspicture
from gpucelery import ToGPU_daydream

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
sentry = Sentry(app)
#sslify = SSLify(app) # SSL portion is busted, oh well, the CIA can get at everything anyways
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["SLACK_OAUTH_CLIENT_ID"] = os.environ.get("SLACK_OAUTH_CLIENT_ID")
app.config["SLACK_OAUTH_CLIENT_SECRET"] = os.environ.get("SLACK_OAUTH_CLIENT_SECRET")
slack_bp = make_slack_blueprint(scope=["identify", "chat:write:bot"])
app.register_blueprint(slack_bp, url_prefix="/login")
mysecrettoken = os.environ.get ("SLACK_SECRETTOKEN");

# this is for the OAUTH security token stuff
@app.route("/")
def index():
    if not slack.authorized:
        return redirect(url_for("slack.login"))

    resp = slack.post("chat.postMessage", data={
        "channel": "#dml_chatbot",
        "text": "ping",
        "icon_emoji": ":robot_face:",
    })
    assert resp.ok, resp.text
    return resp.text

helptext = "My in-silico neurons and I are image fanatics.  Feel free to attach an image with comments.\n" \
           "  Comment: 'paint monet'    - will paint using my Claude Monet impersonation\n" \
           "  Comment: 'paint picasso'  - will paint using my Pablo Picasso impersonation\n" \
           "  Comment: 'paint afremov'  - will paint using my Leonid Afremov impersonation\n" \
           "  Comment: 'paint van gogh' - will paint using my Vincent van Gogh impersonation\n" \
           "  Comment: 'guess me'       - will guess what your image is\n" \
           "  Comment: 'daydream'       - will use your image in a dream\n" \
           "Note 1: i only support painting jpg and png files\n" \
           "Note 2: type the comments precisely as above since I'm not using Word2Vec yet\n" \
           "Note 3: the comments must be added as part of the image upload\n" \
           "Note 4: it's ok if you don't like my art, i will keep practicing!";

optionslist = ['daydream', 'guess me', 'paint monet', 'paint picasso', 'paint afremov', 'paint van gogh'];


def deep_search(needles, haystack):
    found = {}
    if type(needles) != type([]):
        needles = [needles]

    if type(haystack) == type(dict()):
        for needle in needles:
            if needle in haystack.keys():
                found[needle] = haystack[needle]
            elif len(haystack.keys()) > 0:
                for key in haystack.keys():
                    result = deep_search(needle, haystack[key])
                    if result:
                        for k, v in result.items():
                            found[k] = v
    elif type(haystack) == type([]):
        for node in haystack:
            result = deep_search(needles, node)
            if result:
                for k, v in result.items():
                    found[k] = v
    return found

# only support for jpg and png for now
def validPictureFormat (filename):
    filename = filename.lower ()
    if filename[-4:] == ".jpg" or filename[-5:] == ".jpeg" or filename[-4:] == ".png":
        return True
    return False

def getFileType (filename):
    filename = filename.lower ()
    if filename[-4:] == ".jpg" or filename[-5:] == ".jpeg":
        return 'jpg'
    elif filename[-4:] == ".png":
        return 'png'
    else:
        return 'invalidformat'
    

imagecache = {}; # empty dictionary
def cacheimages (eventjson):
   print ('entering cacheimages')
   if 'channel' in eventjson:
      findme = deep_search(["image_url"], eventjson)
      if 'image_url' in findme:
        imagecache[eventjson['channel']] = { 'imageurl': findme['image_url'], 'imagetype': 'readheader' }
        print (imagecache[eventjson['channel']])
      else:
         findme = deep_search(["thumb_url"], eventjson)
         if 'thumb_url' in findme:
            imagecache[eventjson['channel']] = { 'imageurl': findme['thumb_url'], 'imagetype': 'readheader' }
            print (imagecache[eventjson['channel']])
         else:
            findme = deep_search(["url_private", "filetype"], eventjson)
            if 'url_private' in findme and 'filetype' in findme:
               if findme['filetype'].lower () == 'png' or findme['filetype'].lower () == 'jpg':
                  imagecache[eventjson['channel']] = { 'imageurl': findme['url_private'], 'imagetype': findme['filetype'].lower () }
                  print (imagecache[eventjson['channel']])
      print (findme)
      print ('exiting cacheimages')


# this captures the main event hook
@app.route('/eventhook', methods=['POST'])
def result():
        jsoncontent = request.get_json ();
        print (jsoncontent);

        if 'challenge' in jsoncontent:
            return (jsoncontent['challenge'])

        if 'event' in jsoncontent and 'type' in jsoncontent['event']: 
            event = jsoncontent['event']
            cacheimages (event);

            if 'user' in event and 'channel' in event and 'message' == event['type']: # if there's a type in the event, message, and it's a user (could be a bot)
                payload = {'token': mysecrettoken, 'user': event['user']} # get username
                r = requests.post(url='https://slack.com/api/users.info', data=payload)
                username = r.json ()['user']['name']

                if 'upload' in event and event['upload'] == True and 'file' in event: # if attachment
                    file = event['file']
                    if 'is_external' in file and file['is_external'] == False and 'url_private' in file  and 'initial_comment' in file and 'filetype' in file and (file['filetype'].lower() == 'jpg' or file['filetype'].lower() == 'png'):
                        initial_comment = file['initial_comment'];
                        if 'comment' in initial_comment:
                            optionpicked = initial_comment['comment'].lower();
                            if optionpicked in optionslist:
#                                if (username == 'kbhit'): # only mirror kbhit, just for testing lol
                                    if (optionpicked == "guess me"):
                                        message = "Okie dokie I will give my best effort to guess the picture <@%s|cal>, firing up my retinal neurons - hold tight." % (event['user']);
                                        payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                                        response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                                        if (not 'error' in response.json()):
                                            print ("Lets add this bad boy to the queue\n");
                                            ToGPU_guesspicture.delay (mysecrettoken, event['channel'], event['user'], file['url_private'], file['filetype'].lower());
                                    elif (optionpicked == "daydream"):
                                        message = "I'm going to sleep and daydream about your picture <@%s|cal>, firing up my subconscious neurons - Zzzzzzz." % (event['user']);
                                        payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                                        response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                                        if (not 'error' in response.json()):
                                            print ("Lets add this bad boy to the queue\n");
                                            ToGPU_daydream.delay (mysecrettoken, event['channel'], event['user'], 'notusedyet', file['url_private'], file['filetype'].lower());
                                    else:
                                        message = "Will do captain <@%s|cal>, firing up my painting neurons - stay tuned." % (event['user']);
                                        payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                                        response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                                        if (not 'error' in response.json()):
                                            print ("Lets add this bad boy to the queue\n");
                                            ToGPU_paint.delay (mysecrettoken, event['channel'], event['user'], optionpicked, file['url_private'], file['filetype'].lower());

                elif 'text' in event: # if it's a regular message
                    textmessage = event['text'].lower ()
#                    if (username == 'kbhit' and textmessage == 'help'): # only mirror kbhit, just for testing lol
                    if (textmessage == 'help'): # only mirror kbhit, just for testing lol
                        payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': helptext };
                        response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                    elif (textmessage == 'guess last'):
                       if not (event['channel'] in imagecache):
                          message = "Sorry <@%s|cal>, I don't remember the last image on this channel (I may have been restarted)." % (event['user']);
                          payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                          response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                       else: 
                          lastcache = imagecache[event['channel']];
                          message = "Attempting to guess the last picture or thumbnail in this channel <@%s|cal>, concentrating... one minute please." % (event['user']);
                          payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                          response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                          if (not 'error' in response.json()):
                             print ("Lets add this bad boy to the queue\n");
                             print (lastcache);
                             ToGPU_guesspicture.delay (mysecrettoken, event['channel'], event['user'], lastcache['imageurl'], lastcache['imagetype']);
                    elif (textmessage == 'daydream last'):
                       if not (event['channel'] in imagecache):
                          message = "Sorry <@%s|cal>, I don't remember the last image on this channel (I may have been restarted)." % (event['user']);
                          payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                          response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                       else: 
                          lastcache = imagecache[event['channel']];
                          message = "Going to daydream about the last picture or thumbnail in this channel <@%s|cal>, Zzzzzzz... sleeping for a few" % (event['user']);
                          payload = {'token': mysecrettoken, 'channel': event['channel'], 'text': message};
                          response = requests.post(url='https://slack.com/api/chat.postMessage', data=payload);
                          if (not 'error' in response.json()):
                             print ("Lets add this bad boy to the queue\n");
                             print (lastcache);
                             ToGPU_daydream.delay (mysecrettoken, event['channel'], event['user'], 'notusedyet', lastcache['imageurl'], lastcache['imagetype']);

        return "I'm a good painter I think";

@app.route('/messagebutton', methods=['POST'])
def result2():
        print (request);
        jsoncontent = request.get_json ();
        print (jsoncontent);
        return ("if you ever want to support message buttons, then you might consider putting it in this code block mr. coder")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
