import datetime

from trier_de_news_telegram_bot.news import News


def test_fetch_latest_news(tmp_path):
    """Test fetching news"""
    feed_file = "tests/testdata/feed.xml"
    state_file = tmp_path / "state.data"
    news = News(feed_url=feed_file, state_file=state_file)

    news_items = news.fetch_latest_news()

    assert len(news_items) == 10
    assert news_items[0].title == "Bücherbasar am ersten Samstag im Monat"
    assert news.last_update ==  datetime.datetime.strptime("Wed, 14 Dec 2022 10:51:06 +0100", "%a, %d %b %Y %H:%M:%S %z")

def test_fetch_latest_news_md(tmp_path):
    """Test fetching news"""
    feed_file = "tests/testdata/feed.xml"
    state_file = tmp_path / "state.data"
    news = News(feed_url=feed_file, state_file=state_file)

    news_items = news.fetch_latest_news_md()

    assert len(news_items) == 1
    assert len(news_items[0]) < 4096
    assert '[Bücherbasar am ersten Samstag im Monat](http://www\\.trier\\.de/icc/internet\\_de/nav/4cc/broker\\.jsp?uMen\\=4cc4fbd0\\-1d9c\\-d311\\-c258\\-732ead2aaa78&uCon\\=1ef6073b\\-1a00\\-1581\\-257a\\-45c751d91e56&uTem\\=0b93090b\\-49e4\\-7271\\-94e8\\-c0f4087257ba) \\(14\\.12\\.22 10:51\\)' in news_items[0]
