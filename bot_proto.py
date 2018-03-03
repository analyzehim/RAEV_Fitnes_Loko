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


def parse_program(programs):
    mas = sorted(list(programs))
    LINE_SIZE = 3
    keyboard = []
    keyboard.append( [{'text': mas[0], 'callback_data': mas[0]}] )
    for elem in mas[1:]:
        if len(keyboard[-1])!= LINE_SIZE:
            keyboard[-1].append({'text': elem, 'callback_data': elem})
        else:
            keyboard.append([{'text': elem, 'callback_data': elem}])
    return keyboard



def get_schedule_dict():
    f = codecs.open('data/programs.txt', 'r', encoding='utf-8')
    schedule = f.read().split('!')
    programs = schedule[1::2]
    programs_time = schedule[2::2]
    schedule_dict={}
    for i in range(len(programs_time)):
        schedule_dict[programs[i]] = programs_time[i]
    return set(schedule_dict.keys()), schedule_dict

def get_notif_able():
    f = codecs.open('data/notif_able.txt', 'r', encoding='utf-8')
    notif_able = f.read()
    return notif_able[1:]

def get_notif_disable():
    f = codecs.open('data/notif_disable.txt', 'r', encoding='utf-8')
    notif_disable = f.read()
    return notif_disable[1:]


def get_menu_str():
    f = codecs.open('data/menu_str.txt', 'r', encoding='utf-8')
    menu_str = f.read()
    return menu_str[1:]

def get_contacts_text():
    f = codecs.open('data/contacts_text.txt', 'r', encoding='utf-8')
    contacts_text = f.read()
    return contacts_text

def get_cards_text():
    f = codecs.open('data/cards_text.txt', 'r', encoding='utf-8')
    cards_text = f.read()
    return cards_text

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
        self.programs, self.schedule_dict = get_schedule_dict()

        self.schedule_str = get_schedule_str()
        self.cards_str = get_cards_str()
        self.notification_str = get_notification_str()
        self.feedback_str = get_feedback_str()
        self.contacts_str = get_contacts_str()
        self.menu_str = get_menu_str()
        self.notification_req_str = "В этом разделе Вы можете настроить уведомления."
        self.notification_able_str = "Выберите групповую программу на уведомления о которой Вы хотите подписаться:"
        self.notification_disable_str = "Выберите групповую программу от уведомлений которой Вы хотите отписаться:"
        self.schedule_request_str = "Выберите групповую программу, расписание которой вы хотите посмотреть:"
        self.schedule_req = "Посмотреть другие расписания"
        self.contacts_text = get_contacts_text()
        self.cards_text = get_cards_text()
        self.menu_text = get_menu_text()

        self.notif_able = get_notif_able()
        self.notif_disable = get_notif_disable()

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
            print update
            #return update['callback_query']['message']['message_id']

            self.offset = update['update_id']
            ans = {}

            if 'message' in update:
                ans['message'] = update['message']['text'].encode("utf-8")
                ans['message_unicode'] = update['message']['text']
                ans['date'] = update['message']['date']
                ans['from_id'] = update['message']['chat']['id']  # Chat ID
                try:
                    ans['name'] = update['message']['chat']['first_name'].encode("utf-8")
                except:
                    ans['name'] = update['message']['from']['first_name'].encode("utf-8")

            if 'callback_query' in update:
                ans['callback_mes_id'] = update['callback_query']['message']['message_id']
                ans['from_id'] = update['callback_query']['message']['chat']['id']
                ans['callback_data'] = update['callback_query']['data']

            #author_id = update['message']['from']['id']  # Creator ID


            updates_list.append(ans)
            #log_event('from %s (id%s): "%s" with author: %s; time:%s' % parameters)
        return updates_list

    def send_text(self, chat_id, text):
        log_event('Sending to %s: %s' % (chat_id, text))  # Logging
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
        Send text and keyboard at second
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

    def send_cards(self, chat_id):
        keyboard = [[self.menu_str]]
        json_data = {'chat_id': chat_id, 'text': self.cards_text, 'parse_mode': 'HTML',
                     "reply_markup": {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        # print request.json()
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
            return False
        return request.json()['ok']  # Check API

    def send_notification_request(self, chat_id):

        keyboard = [[self.notif_able], [self.notif_disable], [self.menu_str]]
        json_data = {'chat_id': chat_id, 'text': self.notification_req_str, 'parse_mode': 'HTML',
                     "reply_markup": {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        # print request.json()
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
            return False
        return request.json()['ok']  # Check API


    def send_notif_able_request(self, chat_id, programs):
        keyboard = parse_program(programs)

        json_data = {"chat_id": chat_id, 'text': self.notification_able_str,
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
            return False
        return request.json()['ok']  # Check API

    def send_notif_disable_request(self, chat_id, programs):
        keyboard = parse_program(programs)

        #keyboard = [[{'text': '1', 'callback_data': 'data 1'}, {'text': '2', 'callback_data': 'data 2'}]]
        json_data = {"chat_id": chat_id, 'text': self.notification_disable_str,
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
            return False
        return request.json()['ok']  # Check API

    def add_program(self, from_id, data):
        self.send_text(from_id, " Вы подписаны на {0}".format(data))

    def delete_program(self, from_id, data):
        self.send_text(from_id, " Вы отписались от {0}".format(data))

    def send_schedule_request(self, chat_id, programs):
        keyboard = parse_program(programs)
        #keyboard = [[{'text': '1', 'callback_data': 'data 1'}, {'text': '2', 'callback_data': 'data 2'}]]
        json_data = {"chat_id": chat_id, 'text': self.schedule_request_str,
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
            return False
        return request.json()['ok']  # Check API

    def send_schedule(self, chat_id, data):
        schedule = self.schedule_dict[data]
        keyboard = [
                    [{'text': self.schedule_req, 'callback_data': self.schedule_req}],
                    [{'text': self.menu_str, 'callback_data': self.menu_str}]
                    ]
        json_data = {'chat_id': chat_id, 'text': schedule, 'parse_mode': 'HTML',
                     "reply_markup": {"inline_keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}}
        if not self.proxy:  # no proxy
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data)  # HTTP request

        if self.proxy:
            request = requests.post(self.URL + self.TOKEN + '/sendMessage', json=json_data,
                                    proxies=self.proxies)  # HTTP request with proxy

        # print request.json()
        if not request.status_code == 200:  # Check server status
            log_event("ERROR: " + request.text)
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
