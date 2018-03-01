# -*- coding: utf-8 -*-
from bot_proto import *


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

    message_unicode.encode('raw_unicode_escape')

    if cmd == '/start':
        telebot.send_menu(from_id)

    elif message_unicode == telebot.menu_str:
        telebot.send_menu(from_id)

    elif message_unicode == telebot.cards_str:
        telebot.send_cards(from_id)

    elif message_unicode == telebot.contacts_str:
        telebot.send_contacts(from_id)

    else:
        log_event('No action')


if __name__ == "__main__":

    telebot = Telegram()
    while True:
        try:
            check_updates()
            time.sleep(telebot.Interval)
        except KeyboardInterrupt:
            print 'Interrupt by user..'
            break
        except Exception, e:
            log_event(get_exception())

    # while True:
    #     keyboard1 = [[{'text': 'Button 1', 'url': 'http://www.yandex.ru/'}, {'text': 'Button 2', 'callback_data': 'data 2'}]]
    #     keyboard2 = [
    #         [{'text': 'Button 3', 'url': 'http://www.yandex.ru/'}, {'text': 'Button 4', 'callback_data': 'data 2'}]]
    #     telebot.send_text_with_keyboard(telebot.admin_id, 'Options:', keyboard1)
    #     time.sleep(5)
    #     message_id = telebot.get_updates()
    #     telebot.edit_keyboard(74102915, message_id, keyboard2)
    #     time.sleep(10)
    #
    # # telebot.send_text_with_keyboard(telebot.admin_id, 'Options:', keyboard)
    # # telebot.send_text_with_keyboard(telebot.admin_id, 'Options:', keyboard)
    # #
    # # while True:
    #     print telebot.get_updates(editMessageReplyMarkup)
    #     print "_____"
    #     telebot.send_text(telebot.admin_id, "Run on {0}".format(telebot.host))
    #     #telebot.send_text_with_keyboard(telebot.admin_id, 'Options:', [["breakfast", "lunch", "dinner"], ["cry", "sex", "tv-series"]])
    #
    #     time.sleep(5)
    #
    # # while True:
    # #     try:
    # #         time.sleep(telebot.Interval)
    # #     except KeyboardInterrupt:
    # #         print 'Interrupt by user..'
    # #         break
    # #     except Exception, e:
    # #         log_event(get_exception())