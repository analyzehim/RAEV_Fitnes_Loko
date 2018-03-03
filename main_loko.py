# -*- coding: utf-8 -*-
from bot_proto import *
from db_proto import DB


def schedule_handler(update, schedule_state):

    if 'message_unicode' in update:
        message_unicode = update['message_unicode']
    if 'from_id' in update:
        from_id = update['from_id']

    if schedule_state == 1:
        if 'callback_data' in update:
            data = update['callback_data']
            telebot.send_schedule(from_id, data)
            db.set_schedule_state(from_id, 2)
            #telebot.send_menu(from_id)

    if schedule_state == 2:
        if 'callback_data' in update:

            data = update['callback_data']
            if data.encode('utf-8') == telebot.schedule_req:
                db.set_schedule_state(from_id, 1)
                telebot.send_schedule_request(from_id, telebot.programs)
            else:
                db.set_schedule_state(from_id, 0)
                telebot.send_menu(from_id)



def notif_handler(update, notif_state):
    if 'message_unicode' in update:
        message_unicode = update['message_unicode']
    if 'from_id' in update:
        from_id = update['from_id']

    if notif_state == 1:
        if message_unicode == telebot.notif_able:
            db.set_notification_state(from_id, 2)
            telebot.send_notif_able_request(from_id, telebot.programs)

        elif message_unicode == telebot.notif_disable:
            db.set_notification_state(from_id, 3)
            telebot.send_notif_disable_request(from_id, db.get_programs(from_id))

        else:
            db.set_notification_state(from_id, 0)
            telebot.send_menu(from_id)

    elif notif_state == 2:
        if 'callback_data' in update:
            data = update['callback_data']
            db.add_programs(from_id, data)
            db.set_notification_state(from_id, 0)
            telebot.add_program(from_id, data)
            telebot.send_menu(from_id)

    elif notif_state == 3:
        if 'callback_data' in update:
            data = update['callback_data']
            db.delete_programs(from_id, data)
            db.set_notification_state(from_id, 0)
            telebot.delete_program(from_id, data)
            telebot.send_menu(from_id)
    else:
        db.set_notification_state(from_id, 0)
        telebot.send_menu(from_id)




def check_updates():
    parameters_list = telebot.get_updates()
    if not parameters_list:
        return 0
    for parameters in parameters_list:
        run_command(parameters)


def run_command(update):
    #print update
    message =''
    message_unicode =u''
    from_id = 0

    if 'message' in update:
        message = update['message']
    if 'message_unicode' in update:
        message_unicode = update['message_unicode']
    if 'from_id' in update:
        from_id = update['from_id']
        try:
            log_event("{0} send message '{1}'".format(from_id, message))
        except:
            pass
    notif_state = db.get_notification_state(from_id)
    schedule_state = db.get_schedule_state(from_id)
    #print from_id, message, notif_state

    if message == '/start':
        telebot.send_menu(from_id)
        db.add_default_id(from_id)

    elif message_unicode == telebot.menu_str:
        db.add_default_id(from_id)
        telebot.send_menu(from_id)

    elif notif_state != 0:
        notif_handler(update, notif_state)

    elif schedule_state != 0:
        schedule_handler(update, schedule_state)

    #print message_unicode.encode('raw_unicode_escape')
    elif message_unicode == telebot.cards_str:
        telebot.send_cards(from_id)
        db.add_default_id(from_id)

    elif message_unicode == telebot.contacts_str:
        telebot.send_contacts(from_id)
        db.add_default_id(from_id)

    elif message_unicode == telebot.notification_str:
        telebot.send_notification_request(from_id)
        db.set_notification_state(from_id, 1)

    elif message_unicode == telebot.schedule_str:
        telebot.send_schedule_request(from_id, telebot.programs)
        db.set_schedule_state(from_id, 1)

    else:
        log_event('No action')
        db.add_default_id(from_id)
        telebot.send_menu(from_id)
    notif_state = db.get_notification_state(from_id)
    schedule_state = db.get_schedule_state(from_id)
    #print from_id, message, notif_state


if __name__ == "__main__":

    telebot = Telegram()
    db = DB()
    telebot.send_text(telebot.admin_id, "START")
    while True:
        try:
            check_updates()
            time.sleep(telebot.Interval)
        except KeyboardInterrupt:
            print 'Interrupt by user..'
            break
        except Exception, e:
            log_event(get_exception())