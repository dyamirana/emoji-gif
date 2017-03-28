#!/usr/bin/env python
# -*- coding: utf-8 -*-
import vk
import requests
import os
import json
import threading
import logging
import sqlite3
import giphypop
import random
import settings
from Queue import Queue
from time import sleep
from emojis import emojidict
from flask import Flask, request


conveyor = Queue()

gif = giphypop.Giphy()

confirmation_code = settings.confirmcode
api = vk.API(vk.Session(access_token=settings.token), v='5.63', timeout=30)
apiuser = vk.API(vk.Session(access_token=settings.usertoken), v='5.63', timeout=30)

# db
con = sqlite3.connect('data.db',check_same_thread=False)
cur = con.cursor()

cur.execute(
    'CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY ,vkid INTEGER ,firstName VARCHAR(100), secondName VARCHAR(30))')
cur.execute('CREATE TABLE IF NOT EXISTS emojitogif (id INTEGER PRIMARY KEY, emoji VARCHAR, gipfs VARCHAR)')
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, vkid INTEGER, ingroup BOOLEAN)')
cur.execute('CREATE TABLE IF NOT EXISTS giphy (id INTEGER PRIMARY KEY, gifvkid TEXT, giphyname TEXT)')
con.commit()

admins = api.groups.getMembers(group_id=settings.groupid,filter='managers')["items"]
print admins

def upload(url,name):
    # try:
        gif = requests.get(url, stream=True)

        if gif.status_code == 200:
            uploadurl = apiuser.docs.getWallUploadServer()['upload_url']
            responsefileuploaded = requests.post(uploadurl, files={'file': ('file.gif', gif.raw)})
            responsefileuploadeds = json.loads(responsefileuploaded.text)
            file = '%s' % responsefileuploadeds['file']
            if 'file' in responsefileuploaded.text:
                saved = apiuser.docs.save(file=file, title=name)
                cur.execute('INSERT INTO giphy (gifvkid ,giphyname) VALUES (?,?);', ('doc%d_%d'%(saved[0]['owner_id'],saved[0]['id']), url.split('/')[4]))
                con.commit()

                return saved
    # except:
    #     return None


def check_users():
#     try:
    users = api.groups.getMembers(group_id=settings.groupid)['count']
    cur.execute('SELECT COUNT(vkid) FROM users')

    if cur.fetchall()[0][0] < users:
        ofset = users//1000
        if ofset ==0:
            for i in api.groups.getMembers(group_id=settings.groupid)["items"]:
                cur.execute('SELECT t.* FROM users t WHERE vkid =%d'%(i))

                if len(cur.fetchall()) ==0:
                    cur.execute('INSERT INTO users (vkid ,ingroup) VALUES (?,?);', (i, True))
                    con.commit()
        else:
            for c in range(0,ofset):
                for i in api.groups.getMembers(group_id=settings.groupid,offset=ofset*1000  )["items"]:
                    cur.execute('SELECT t.* FROM users t WHERE vkid =%d' % (i))
                    if len(cur.fetchall()) == 0:
                        cur.execute('INSERT INTO users (vkid ,ingroup) VALUES (?,?);', (i, True))
                        con.commit()
    # except:
    #     pr
    #     sleep(0.2)
    #     check_users()


# for i in api.groups.getMembers(group_id=settings.groupid)["items"]:
#     cur.execute('INSERT INTO users (vkid ,ingroup) VALUES (?,?);',(i,'default'))
# con.commit()
# cur.execute('SELECT t.* FROM users t WHERE vkid = %d' % 183156792)
# print cur.fetchall()


# service
service_commands = ['settings', 'admins']


def message(body, u_id,in_atch=[]):

    cur.execute('SELECT t.* FROM users t WHERE vkid = %d' % u_id)

    if len(cur.fetchall()) != 0:
        body = body.lower()
        args = []
        command = ''
        if body != '':
            splitted = body.split(' ')
            command = splitted[0]

            if len(splitted) > 1:
                args = splitted[1::]
        cur.execute("SELECT t.* FROM emojitogif t WHERE emoji= (?)", (command,))
        check = cur.fetchall()

        if any(command in i[1] for i in check):
            dbresult = check
            print check[0][2]
            if len(dbresult) != 0:
                api.messages.send(user_id=u_id,
                                  message=" ", attachment=random.choice(dbresult)[2])
                return

        if u'добавь' in body and str(u_id) in str(admins) :
            if len(args) >0 and len(in_atch)>0:
                for at in in_atch:
                    if at['type'] == 'doc':
                        if 'access_key' in at['doc']:attext ='doc%d_%d_%s' % (at['doc']['owner_id'], at['doc']['id'],at['doc']['access_key'])
                        else: attext ='doc%d_%d' % (at['doc']['owner_id'], at['doc']['id'])
                        cur.execute("SELECT t.* FROM emojitogif t WHERE gipfs = (?)", (attext,))
                        dbresult = cur.fetchall()
                        if len(dbresult) == 0:
                            cur.execute('INSERT INTO emojitogif (emoji ,gipfs) VALUES (?,?);',
                                        (args[0],attext))
                            con.commit()
                        api.messages.send(user_id=u_id,
                                          message=u"Успешно!")
            else:
                api.messages.send(user_id=u_id,
                                  message=u"Ошибка!")
            return 'ok'
        if any(e in command for e in emojidict.keys()):
            try:
                result =gif.search(phrase=str(emojidict[command]))
            except:
                url = gif.screensaver(tag='fun').media_url

                doc = upload(url,'random')
                attch = 'doc%d_%d'%(doc[0]['owner_id'],doc[0]['id'])
                api.messages.send(user_id=u_id,message="В моей базе нет этого символа🤔\nВзамен держи рандомную гифку!",attachment=attch)
                return 'ok'
            url = random.choice([x for x in result])

            cur.execute("SELECT t.* FROM giphy t WHERE giphyname = (?)",(url.media_url.split('/')[4],))
            dbresult = cur.fetchall()
            if len(dbresult) != 0:

                attch = dbresult[0][1]
            else:
                doc = upload(url.media_url,body)

                attch = 'doc%d_%d'%(doc[0]['owner_id'],doc[0]['id'])
            api.messages.send(user_id=u_id,
                              message=" ",attachment=attch)
            return 'ok'
        else:
                url = gif.screensaver(tag='fun').media_url

                doc = upload(url,'random')
                attch = 'doc%d_%d'%(doc[0]['owner_id'],doc[0]['id'])
                api.messages.send(user_id=u_id,message="В моей базе нет этого символа🤔\nВзамен держи рандомную гифку!",attachment=attch)
    else:
        api.messages.send(user_id=u_id,
                          message=u'Вы не подписаны на сообщество! Сделайте это прямо сейчас!');

app = Flask(__name__)


@app.route('/callback.html', methods=['POST'])
def callback():
    data = request.get_json()
    if data['type'] == "confirmation":
        return confirmation_code
    if data['type'] == 'message_new':
        if u'Привет' in data['object']['body']: return 'ok'
        dsaa = conveyor.put(data)
        return 'ok'
        # if message(data['object']['body'],data['object']['user_id']):
        #     print data['object']['body']
        #
    if data['type'] == 'group_join':
        cur.execute('SELECT t.* FROM users t WHERE vkid =%d' % (data['object']['user_id']))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO users (vkid ,ingroup) VALUES (?,?);', (data['object']['user_id'], True))
            con.commit()
        return 'ok'
    if data['type'] == 'group_leave':
        cur.execute('SELECT t.* FROM users t WHERE vkid =%d' % (data['object']['user_id']))
        if len(cur.fetchall()) != 0:
            cur.execute('DELETE FROM  users WHERE vkid=%d;'%(data['object']['user_id']))
            con.commit()
        try:
            api.messages.send(user_id=data['object']['user_id'], message=u"Очень жаль, что ты вышел:с Было же так весело!")
        except:
            pass
        return 'ok'
    return 'ok'


def worker():
    # event.wait()
    # try:
    while True:
        if not conveyor.empty():
            item = conveyor.get()
            if item['object']['body'] != '':
                if 'attachments' in item['object']:
                    hmm = message(item['object']['body'], item['object']['user_id'],item['object']['attachments'])
                else:
                    hmm =message(item['object']['body'], item['object']['user_id'])
            conveyor.task_done()
        sleep(0.1)
    # except Exception as exp:
    #     print 'Exception in Worker %s' % (exp)
    #     worker()


def web_process():
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 80))
        app.run(host='0.0.0.0', port=port)
        app.logger.setLevel(logging.ERROR)


# THREAD SECTION
check_users()
flask_thread = threading.Thread(target=web_process)
flask_thread.start()
workerthread = threading.Thread(target=worker)
workerthread.start()
