from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Автор комментария."""
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model):
    """Читатель комментария."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Новость."""
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )
    return news


@pytest.fixture
def many_news():
    """Создание нескольких новостей."""
    today = datetime.today()
    news_list = [News(
        title=f'Новость {idx}',
        text='Текст',
        date=today - timedelta(days=idx)
    ) for idx in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    News.objects.bulk_create(news_list)


@pytest.fixture
def many_comments(author, news):
    """Несколько комментариев к новосте."""
    comments_count = 5
    today = timezone.now()
    for idx in range(comments_count):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {idx}'
        )
        comment.created = today + timedelta(days=idx)
        comment.save()


@pytest.fixture
def comment(author, news):
    """Создание комментария к новости."""
    comment = Comment.objects.create(
            news=news,
            author=author,
            text='Комментарий'
        )
    return comment


@pytest.fixture
def pk_for_news(news):
    """Возвращает PK новости."""
    return {'pk': news.pk}


@pytest.fixture
def pk_for_comment(comment):
    """Возвращает PK для комментария."""
    return {'pk': comment.pk}


@pytest.fixture
def comment_form_data():
    """Данные для формы комментария."""
    return {
        'text': 'Текст комментария'
    }
