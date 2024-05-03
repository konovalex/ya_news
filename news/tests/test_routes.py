from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Comment, News


User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование работы маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Создаем новость, автора, читателя, и комментарий от автора ."""
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    def test_pages_availability(self):
        """Проверка доступности страниц."""
        pages = (
            ('news:home', None),
            ('news:detail', {'pk': self.news.pk}),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in pages:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """Проверка доступности комментариев."""
        pages = ['news:edit', 'news:delete']
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in pages:
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'pk': self.comment.id})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка переадресации неавторизованного пользователя."""
        login_url = reverse('users:login')
        pages = ['news:edit', 'news:delete']
        for name in pages:
            with self.subTest(name=name):
                url = reverse(name, kwargs={'pk': self.comment.id})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
