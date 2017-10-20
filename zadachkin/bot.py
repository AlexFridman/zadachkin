#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging
import sys
from configparser import ConfigParser

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, ConversationHandler, RegexHandler)
from telegram.replykeyboardremove import ReplyKeyboardRemove

from zadachkin.db import Mongo, init_mongodb
from zadachkin.db.entities import Source, TaskList
from zadachkin.task_list_generator import TaskListGenerator

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

reply_keyboard = [['Получить задачки'], ['Показать историю']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
task_list_generator = TaskListGenerator()


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
    logger.info('User {} requested task list'.format(update.message.from_user.name))
    task_list = task_list_generator.generate_task_list()

    tasks_str = []
    task_template = '{}. {}, {} (стр. {} - {})'

    simple_task_list = []

    for i, (source, task_i, (start_page, end_page)) in enumerate(task_list):
        tasks_str.append(task_template.format(i + 1, source.author, task_i, start_page, end_page))
        simple_task_list.append((source.str_id, task_i))

    formatted_task_list = '\n'.join(tasks_str)

    try:
        TaskList(user_id=update.message.from_user.name,
                 timestamp=datetime.datetime.utcnow(),
                 tasks=simple_task_list).save()
    except Exception as e:
        logger.error('Failed to save task list')

    update.message.reply_text('Твое задание на сегодня:\n' + formatted_task_list + '\n\nВремя пошло!')


def get_history(bot, update):
    logger.info('User {} requested history'.format(update.message.from_user.name))
    # TODO: implement
    update.message.reply_text(
        'Твоя история:\n'
        '(пока не работает :( )\n'
        'Прокрути чат выше!\n'
    )


def update_sources(bot, update):
    logger.info('Updating sources')
    task_list_generator.replace_sources(list(Source.objects))


def setup_bot(updater):
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('cancel', cancel))

    dp.add_handler(CommandHandler('tasks', get_tasks))
    dp.add_handler(CommandHandler('history', get_history))

    # TODO: make available only for admins
    dp.add_handler(CommandHandler('update_sources', update_sources))

    dp.add_handler(RegexHandler('Получить задачки', get_tasks))
    dp.add_handler(RegexHandler('Показать историю', get_history))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()


def main():
    try:
        config_path = sys.argv[1]
    except IndexError:
        config_path = 'config.ini'

    # parse config
    config = ConfigParser()
    config.read(config_path)

    # init db connection
    host_port = ':'.join((config.get('mongodb', 'host'), config.get('mongodb', 'port')))
    username = config.get('mongodb', 'username')
    password = config.get('mongodb', 'password')
    db_name = config.get('mongodb', 'db_name')

    conf = Mongo(db_name, [host_port], username, password)
    init_mongodb(conf.connection)

    # load sources from db
    update_sources(None, None)

    # setup tg bot
    updater = Updater(config.get('telegram', 'access_token'))
    setup_bot(updater)
    updater.idle()


if __name__ == '__main__':
    main()
