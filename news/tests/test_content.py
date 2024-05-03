from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News


User = get_user_model()


class TestHomePage(TestCase):
    """Тестирование главной страницы."""

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        """Список новостей, чтобы получилось минимум 2 страницы."""
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)

    def test_context_dict(self):
        """Проверка отображения количество новостей, согласно пагинатору."""
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = object_list.count()
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        """Проверка сортировки списка новостей."""
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):
    """Тестирование страницы с отдельной новостью."""

    @classmethod
    def setUpTestData(cls):
        """Новость, автор комментариев и несколько комментариев к новости."""
        cls.news = News.objects.create(
            title='Тестовая новость',
            text='Просто текст'
        )
        cls.detail_url = reverse('news:detail', kwargs={'pk': cls.news.id})
        cls.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        cls.comments_count = 10
        for index in range(cls.comments_count):
            comment = Comment.objects.create(
                news=cls.news, author=cls.author, text=f'Текст {index}'
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self):
        """Проверка сортировки комментариев к новости."""
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_client_has_no_form(self):
        """У анонимного участника нет формы создания комментария."""
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """У авторизованного участника есть форма создания комментария."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)
