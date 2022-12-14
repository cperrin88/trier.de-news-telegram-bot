"""Fetches news from the feed"""
import datetime
import os.path
import re
from dataclasses import dataclass
from io import StringIO
from typing import List

import feedparser
import pytz


@dataclass
class NewsItem:
    """News item dataclass"""

    date: datetime.datetime
    title: str
    url: str


class News:
    """Manages the fetching of news from RSS"""

    escape_chars = f'([{re.escape(r"_*~`>#+-=|{}.!")}])'

    def __init__(self, feed_url: str, state_file: str):
        self.feed_url = feed_url
        self.state_file = state_file
        self._last_update =  datetime.datetime.fromtimestamp(0, tz=pytz.utc)

    @property
    def last_update(self) -> datetime.datetime:
        """getter for last_update"""
        if not self._last_update:
            self.restore_state()
        return self._last_update

    @last_update.setter
    def last_update(self, value: datetime.datetime):
        """setter for last_update"""
        self._last_update = value
        self._save_state()

    def restore_state(self):
        """Restore the last_update from file"""
        if not os.path.isfile(self.state_file):
            self._save_state()
        else:
            with open(self.state_file, "r", encoding="utf-8") as file:
                last_update = file.readline()
                self._last_update = datetime.datetime.fromisoformat(last_update)

    def _save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as file:
            file.write(str(self._last_update.isoformat()))
            file.flush()

    def fetch_latest_news(self) -> List[NewsItem]:
        """Fetch the news RSS and parse the entries"""
        upd = self.last_update
        feed = feedparser.parse(self.feed_url)
        news_items = []
        for entry in feed.entries:
            date = datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            if date > upd:
                news_items.append(NewsItem(date, entry.title, entry.link))

        if feed.entries:
            self.last_update = datetime.datetime.strptime(
                feed.entries[0].published, "%a, %d %b %Y %H:%M:%S %z"
            )
        return news_items

    def fetch_latest_news_md(self) -> list[str] | None:
        """Get the latest new from the Server as Markdown"""
        news_items = self.fetch_latest_news()
        if not news_items:
            return None
        messages = []
        buffer = StringIO()
        for item in news_items:
            date = item.date.strftime("%d.%m.%y %H:%M")

            msg = f"[{item.title}]({item.url}) \\({date}\\)\n"

            msg = re.sub(self.escape_chars, r"\\\1", msg)

            if buffer.tell() + len(msg) >= 4096:
                messages.append(buffer.getvalue())
                buffer.truncate()

            buffer.write(msg)
        messages.append(buffer.getvalue())
        return messages
