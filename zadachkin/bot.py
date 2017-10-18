#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, ConversationHandler, RegexHandler)
# Enable logging
from telegram.replykeyboardremove import ReplyKeyboardRemove

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

reply_keyboard = [['Получить задачки'], ['Показать историю']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        'Привет! Меня зовут Задачкин!\n'
        'Готов порешать?!\n\n'
        '/tasks - команда выдачи задачек\n'
        '/history - команда просмотра истории',
        reply_markup=markup
    )


def cancel(bot, update):
    user = update.message.from_user
    logger.info('User %s canceled the conversation.' % user.first_name)
    update.message.reply_text('Из этой игры нельзя выйти!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update {} caused error {}'.format(update, error))


def get_tasks(bot, update):
    update.message.reply_text(
        'Твое задание на сегодня:\n'
        'решать задачки'
    )


def get_history(bot, update):
    update.message.reply_text(
        'Твоя история:\n'
        'дата: задачки\n'
        'дата: задачки\n'
    )


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ.get('TOKEN'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('tasks', get_tasks))
    dp.add_handler(CommandHandler('history', get_history))
    dp.add_handler(RegexHandler('Получить задачки', get_tasks))
    dp.add_handler(RegexHandler('Показать историю', get_history))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
