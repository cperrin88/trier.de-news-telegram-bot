"""Simple telegram bot for trier.de news"""
import configparser

import click
from telegram import ParseMode
from telegram.ext import Updater, PicklePersistence
from telegram.ext.callbackcontext import CallbackContext

from .news import News


@click.command()
@click.option(
    "-f",
    "--file",
    help="Configuration file",
    type=click.Path(exists=True),
    default="./trier-bot.ini",
)
def main(file):
    """Entrypoint"""
    config = configparser.ConfigParser()
    config.read(file)

    news = News(config["rss"]["feed_url"], config["rss"]["state_file"])

    def refresh_feed(context: CallbackContext):
        """Callback to refresh the newsfeed"""
        messages = news.fetch_latest_news_md()
        if not messages:
            return

        for msg in messages:
            context.bot.send_message(
                chat_id=context.bot_data["chat_id"],
                text=msg,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                disable_notification=True,
            )

    my_persistence = PicklePersistence(filename=config["telegram"]["state_file"])

    updater = Updater(
        token=config["telegram"]["api_key"],
        use_context=True,
        persistence=my_persistence,
    )
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher.bot_data["chat_id"] = config["telegram"]["chat_id"]

    job_queue.run_repeating(
        refresh_feed, interval=int(config["rss"]["refresh_interval"]), first=0
    )

    updater.start_polling()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
