# -*- coding: utf-8 -*-
from bot_proto import *
from db_proto import DB


def check_updates():
    parameters_list = telebot.get_updates()
    if not parameters_list:
        return 0
    for parameters in parameters_list:
        run_command(parameters)


def run_command(update):

    if 'message' in update:
        cmd = update['message']
    if 'message_unicode' in update:
        message_unicode = update['message_unicode']
    if 'from_id' in update:
        from_id = update['from_id']

    notif_state = db.get_notification_state(from_id)
    schedule_state = db.get_schedule_state(from_id)

    if notif_state == 1:

        if message_unicode == telebot.notif_able:
            db.set_notification_state(from_id, 2)
            telebot.send_notif_able_request(from_id, telebot.subscribes)

        elif message_unicode == telebot.notif_disable:
            db.set_notification_state(from_id, 3)
            telebot.send_notif_disable_request(from_id, db.get_subscribe(from_id))

        else:
            db.set_notification_state(from_id, 0)
            telebot.send_menu(from_id)



    #print message_unicode.encode('raw_unicode_escape')

    if cmd == '/start':
        telebot.send_menu(from_id)
        db.add_new_id(from_id)

    elif message_unicode == telebot.menu_str:
        db.set_default_state()
        telebot.send_menu(from_id)

    elif message_unicode == telebot.cards_str:
        telebot.send_cards(from_id)

    elif message_unicode == telebot.contacts_str:
        telebot.send_contacts(from_id)

    elif message_unicode == telebot.notification_str:
        telebot.send_notification_request(from_id)
        db.set_notification_state(from_id, 1)

    else:
        log_event('No action')


if __name__ == "__main__":

    telebot = Telegram()
    db = DB()
    while True:
        try:
            check_updates()
            time.sleep(telebot.Interval)
        except KeyboardInterrupt:
            print 'Interrupt by user..'
            break
        except Exception, e:
            log_event(get_exception())