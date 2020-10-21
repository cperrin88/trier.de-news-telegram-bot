import configparser

import click as click
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, PicklePersistence

from news import News

news = News()


def start_handler(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             text=r"""
\# Title1
[URL](https://google\.com)
                             """)
    bd = context.bot_data
    if "chats" not in bd:
        context.bot_data["chats"] = set()

    context.bot_data["chats"].add(update.effective_chat.id)


def stop_handler(update, context):
    bd = context.bot_data
    if "chats" in bd:
        context.bot_data["chats"].remove(update.effective_chat.id)


def refresh_feed(context):
    messages = news.get_latest_news_md()
    if not messages:
        return

    for msg in messages:
        context.bot.send_message(chat_id=context.bot_data['chat_id'],
                                 text=msg,
                                 parse_mode=ParseMode.MARKDOWN_V2,
                                 disable_web_page_preview=True,
                                 disable_notification=True)


@click.command()
@click.option("-f", "--file", help="Configuration file",
              type=click.Path(exists=True), default="./trier-bot.ini")
def main(file):
    config = configparser.ConfigParser()
    config.read(file)

    news.feed_url = config['rss']['feed_url']
    news.state_file = config['rss']['state_file']
    news.restore_state()

    my_persistence = PicklePersistence(
        filename=config['telegram']['state_file'])

    updater = Updater(token=config['telegram']['api_key'], use_context=True,
                      persistence=my_persistence)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher.bot_data["chat_id"] = config['telegram']['chat_id']

    job_queue.run_repeating(refresh_feed,
                            interval=int(config['rss']['refresh_interval']),
                            first=0)

    updater.start_polling()


if __name__ == "__main__":
    main()
