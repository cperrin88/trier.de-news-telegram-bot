import datetime
import os.path
import re
import time

import feedparser
from io import StringIO
from typing import List

import telegram.utils.helpers


class NewsItem:
    def __init__(self, date: datetime.datetime, title: str, url: str):
        self.date = date
        self.title = title
        self.url = url


class News:
    def __init__(self, state_file=None, feed_url=None):
        self.feed_url = feed_url
        self.state_file = state_file
        self.last_update = datetime.datetime.now()
        if self.state_file:
            self.restore_state()

    def restore_state(self):
        if not os.path.isfile(self.state_file):
            self.last_update = datetime.datetime.now()
            self._save_state()
            return

        with open(self.state_file, "r") as f:
            last_update = f.readline()
            self.last_update = datetime.datetime.fromtimestamp(float(last_update))
            pass

    def _save_state(self):
        with open(self.state_file, "w") as f:
            f.write(str(self.last_update.timestamp()))
            f.flush()

    def get_latest_news(self) -> List[NewsItem]:
        upd = self.last_update
        self.last_update = datetime.datetime.now()
        f = feedparser.parse(self.feed_url)
        out = list()
        for e in f.entries:
            date = datetime.datetime.fromtimestamp(
                time.mktime(e.published_parsed))
            if date > upd:
                ni = NewsItem(date , e.title, e.link)
                out.append(ni)
        self._save_state()
        return out

    def get_latest_news_md(self) -> List[str]:
        news = self.get_latest_news()
        if not news:
            return
        out = list()
        sb = StringIO()
        for n in news:
            date = n.date.strftime("%d.%m.%y %H:%M")
            msg = "[{title}]({url}) \({date}\)\n" \
                .format(date=date,
                        title=n.title,
                        url=n.url)
            escape_chars = r'_*~`>#+-=|{}.!'
            msg = re.sub('([{}])'.format(re.escape(escape_chars)), r'\\\1',
                          msg)
            if sb.tell() + len(msg) >= 4096:
                out.append(sb.getvalue())
                sb.clear()
            sb.write(msg)
        out.append(sb.getvalue())
        return out
