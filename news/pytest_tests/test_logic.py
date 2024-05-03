from http import HTTPStatus

from django.urls import reverse

import pytest

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


def test_user_can_create_comment(
    author_client, author, news, comment_form_data
):
    """Авторизованный пользователь может создать комментарии."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == comment_form_data['text']


def test_user_cant_use_bad_words_in_comment(author_client, news):
    """Нельзя использовать запрещенные слова в комментарии."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    comment_form_data = {'text': BAD_WORDS[0]}
    response = author_client.post(url, data=comment_form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    """Анонимный пользователь не может создавать комментарии."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=comment_form_data)
    login_url = reverse('users:login')
    excepted_url = f'{login_url}?next={url}'
    assertRedirects(response, excepted_url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
        'comment_url, edit_text',
        (
            ('news:edit', pytest.lazy_fixture('comment_form_data')),
            ('news:delete', None)
        )
)
def test_author_can_edit_or_delete_own_comment(
    author_client, author, news, comment_form_data, comment_url, edit_text
):
    """Автор может редактировать или удалить свой комментарий."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Старый текст'
    )
    url = reverse(comment_url, kwargs={'pk': comment.pk})
    redirect_url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, edit_text)
    assertRedirects(response, f'{redirect_url}#comments')
    if edit_text is not None:
        comment.refresh_from_db()
        assert comment.text == comment_form_data['text']
    else:
        assert Comment.objects.count() == 0


@pytest.mark.parametrize(
        'comment_url, edit_text',
        (
            ('news:edit', pytest.lazy_fixture('comment_form_data')),
            ('news:delete', None)
        )
)
def test_other_user_cant_edit_or_delete_comment(
    reader_client, pk_for_comment, comment_url, edit_text
):
    """Пользователь не может редактировать или удалять чужие комментарии."""
    url = reverse(comment_url, kwargs=pk_for_comment)
    response = reader_client.post(url, edit_text)
    assert response.status_code == HTTPStatus.NOT_FOUND
