import requests
import telebot
import vk_api
import pyrebase
import json
import threading
import os
from dotenv import load_dotenv

load_dotenv()

apiKey = os.getenv("API_KEY")
authDomain = os.getenv("AUTH_DOMAIN")
databaseURL = os.getenv("DATABASE_URL")
projectId = os.getenv("PROJECT_ID")
serviceAccountId = os.getenv("SERVICE_ACCOUNT_ID")
serviceAccount = os.getenv("SERVICE_ACCOUNT")
storageBucket = os.getenv("STORAGE_BUCKET")
vkLogin = os.getenv("VK_LOGIN")
vkPassword = os.getenv("VK_PASSWORD")
token = os.getenv("TOKEN")

config = {
    "apiKey": apiKey,
    "authDomain": authDomain,
    "databaseURL": databaseURL,
    "projectId": projectId,
    "serviceAccountId": serviceAccountId,
    "serviceAccount": serviceAccount,
    "storageBucket": storageBucket
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

bot = telebot.TeleBot(token)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def updateVKPosts():
    try:
        vk_session = vk_api.VkApi(vkLogin, vkPassword)
        vk_session.auth(token_only=True)
        tools = vk_api.VkTools(vk_session)

        wall = tools.get_all_slow('wall.get', 25, {'owner_id': 161916309}, 'items', 25)['items']
        posts = db.child("posts").get().val()
        lastPost = posts[len(posts) - 1]
        new = []

        for post in wall:
            if 'is_pinned' in post and post['is_pinned'] == 1:
                continue
            if post['text'] == lastPost['text']:
                break
            else:
                new.insert(0, {"date": post['date'], "text": post['text']})
        db.child('/posts').set(posts + new)
    except:
        print('error')
        return


def sendPost():
    try:
        channelId = -1001453337141
        currentPost = db.child("currentPost").get().val()
        posts = db.child("posts").get().val()
        post = 'Привет, я дед!'

        if len(posts) <= currentPost + 1:
            post = json.loads(requests.get('http://fucking-great-advice.ru/api/random').text)['text']
        else:
            currentPost = currentPost + 1
            post = posts[currentPost]['text']
        bot.send_message(channelId, post)
        print(post)
        db.child("currentPost").set(currentPost)
    except:
        print('error')


cycle = os.getenv("CYCLE")
if cycle is None:
    cycle = 4 * 60 * 60 * 60
else:
    cycle = int(cycle)

set_interval(sendPost, cycle / 4)
set_interval(updateVKPosts, cycle)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


print('bot has been started')

bot.polling()
