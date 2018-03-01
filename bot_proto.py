# -*- coding: utf-8 -*-
import requests
import time
import socket
import sys
import traceback
import xml.etree.ElementTree as ET
import os
import shutil
import codecs

INTERVAL = 0.5

def get_menu_str():
    f = codecs.open('data/menu_str.txt', 'r', encoding='utf-8')
    menu_str = f.read()
    return menu_str[1:]

def get_contacts_text():
    f = codecs.open('data/contacts_text.txt', 'r', encoding='utf-8')
    contacts_text = f.read()
    return contacts_text


def get_menu_text():
    #f = open("data/menu.txt","r")
    f = codecs.open('data/menu.txt', 'r', encoding='cp1251')
    menu = f.read()
    return menu


def get_schedule_str():
    f = codecs.open('data/schedule.txt', 'r', encoding='utf-8')
    schedule_str = f.read()
    return schedule_str[1:]

def get_cards_str():
    f = codecs.open('data/cards.txt', 'r', encoding='utf-8')
    cards_str = f.read()
    return cards_str[1:]


def get_notification_str():
    f = codecs.open('data/notification.txt', 'r', encoding='utf-8')
    notification_str = f.read()
    return notification_str[1:]


def get_feedback_str():
    f = codecs.open('data/feedback.txt', 'r', encoding='utf-8')
    feedback_str = f.read()
    return feedback_str[1:]


def get_contacts_str():
    f = codecs.open('data/contacts.txt', 'r', encoding='utf-8')
    contacts_str = f.read()
    return contacts_str[1:]


def get_token(tree):
    root = tree.getroot()
    token = root.findall('token')[0].text
    return token


def get_admin(tree):
    root = tree.getroot()
    admin_id = root.findall('admin_id')[0].text
    return int(admin_id)


def get_proxies(tree):
    root = tree.getroot()
    proxy_url = root.findall('proxy')[0].text
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    return proxies


def check_mode(tree):
    import requests

    try:
        requests.get('https://www.google.com')
        return False
    except:
        proxies = get_proxies(tree)
        requests.get('https://www.google.com', proxies=proxies)
        return True


class Telegram:
    def __init__(self):
        if not os.path.exists("documents"):
            os.makedirs("documents")
        self.cfgtree = ET.parse('private_config.xml')
        self.proxy = check_mode(self.cfgtree)
        self.TOKEN = get_token(self.cfgtree)
        self.URL = 'https://api.telegram.org/bot'
        self.admin_id = get_admin(self.cfgtree)
        self.offset = 0
        self.host = socket.getfqdn()
        self.Interval = INTERVAL
        self.menu_text = get_menu_text()
        self.schedule_str = get_schedule_str()
        self.cards_str = get_cards_str()
        self.notification_str = get_notification_str()
        self.feedback_str = get_feedback_str()
        self.contacts_str = get_contacts_str()
        self.menu_str = get_menu_str()
        self.contacts_text  = get_contacts_text()

        if self.proxy:
            self.proxies = get_proxies(self.cfgtree)
            log_event("Init completed with proxy, host: " + str(self.host))
        else:
            log_event("Init completed, host: " + str(self.host))


    def edit_keyboard(self, chat_id, message_id, keyboard):

        json_data = {"chat_id": chat_id, "message_id": message_id,
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/editMessageReplyMarkup', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/editMessageReplyMarkup', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API

    def send_text_with_keyboard(self, chat_id, text, keyboard):
        try:
            log_event('Sending to %s: %s; keyboard: %s' % (chat_id, text, keyboard))  # Logging
        except:
            log_event('Error with LOGGING')
        json_data = {"chat_id": chat_id, "text": text,
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API

    def get_updates(self):
        data = {'offset': self.offset + 1, 'limit': 5, 'timeout': 0}
        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/getUpdates', data=data, proxies=self.proxies)
        else:
            request = requests.post(self.URL + self.TOKEN + '/getUpdates', data=data)
        if (not request.status_code == 200) or (not request.json()['ok']):
            return False

        if not request.json()['result']:
            return
        updates_list = []
        for update in request.json()['result']:
            #return update['callback_query']['message']['message_id']

            self.offset = update['update_id']

            if 'message' not in update or 'text' not in update['message']:
                continue
            if 'callback_query' in update:
                callback_mes_id = update['callback_query']['message']['message_id']
            from_id = update['message']['chat']['id']  # Chat ID
            #author_id = update['message']['from']['id']  # Creator ID
            message = update['message']['text'].encode("utf-8")
            message_unicode = update['message']['text']
            date = update['message']['date']
            try:
                name = update['message']['chat']['first_name'].encode("utf-8")
            except:
                name = update['message']['from']['first_name'].encode("utf-8")
            parameters = ({'name':name, 'message_unicode':message_unicode, 'from_id':from_id, 'message': message, 'date': date})
            updates_list.append(parameters)
            #log_event('from %s (id%s): "%s" with author: %s; time:%s' % parameters)
        return updates_list

    def send_text(self, chat_id, text):
        #log_event('Sending to %s: %s' % (chat_id, text))  # Logging
        data = {'chat_id': chat_id, 'text': text}  # Request create
        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data,
                                    proxies=self.proxies)  # HTTP request with proxy
        else:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data)  # HTTP request
        #print request.json()
        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API


    def send_menu(self, chat_id):
        '''
        Send logo at first
        '''
        image_path = "data/menu_img.jpg"
        data = {'chat_id': chat_id}
        files = {'photo': (image_path, open(image_path, "rb"))}
        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendPhoto', data=data, files=files,
                                    proxies=self.proxies)  # HTTP request with proxy)
        else:
            request = requests.post(self.URL + self.TOKEN + '/sendPhoto', data=data, files=files)

        if not request.status_code == 200:  # Check server status
            return False
        '''
        Send text at second
        '''
        data = {'chat_id': chat_id, 'text': self.menu_text,'parse_mode':'HTML'}  # Request create
        # if self.proxy:
        #     request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data,
        #                             proxies=self.proxies)  # HTTP request with proxy
        # else:
        #     request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=data)  # HTTP request
        #
        # if not request.status_code == 200:  # Check server status
        #     return False
        # return request.json()['ok']  # Check API
        '''
        Send keyboard at third
        '''
        keyboard = [[self.schedule_str], [self.cards_str], [self.notification_str], [self.feedback_str, self.contacts_str]]

        json_data = {'chat_id': chat_id, 'text': self.menu_text,'parse_mode':'HTML',
                     "reply_markup": {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        #print request.json()
        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API

    def send_contacts(self, chat_id):
        keyboard = [[self.menu_str]]
        json_data = {'chat_id': chat_id, 'text': self.contacts_text, 'parse_mode': 'HTML',
                     "reply_markup": {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        # print request.json()
        if not request.status_code == 200:  # Check server status
            return False
        return request.json()['ok']  # Check API


def log_event(text):
    f = open('log.txt', 'a')
    event = '%s >> %s' % (time.ctime(), text)
    print event + '\n'
    f.write(event + '\n')
    f.close()
    return


def get_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    return ''.join('!! ' + line for line in lines)
