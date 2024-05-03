from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
        'name, kwargs',
        (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('pk_for_news')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, kwargs):
    """Доступность страниц для аннонимного пользователя."""
    url = reverse(name, kwargs=kwargs)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        )
)
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_comment')),
        ('news:delete', pytest.lazy_fixture('pk_for_comment')),
    )
)
def test_pages_availability_for_comment_edit_and_delete(
    parametrized_client, name, kwargs, expected_status
):
    """Доступность страниц редактирование и удаление своих комментариев."""
    url = reverse(name, kwargs=kwargs)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
        'name, kwargs',
        (
            ('news:edit', pytest.lazy_fixture('pk_for_comment')),
            ('news:delete', pytest.lazy_fixture('pk_for_comment')),
        )
)
def test_redirects(client, name, kwargs):
    """Тестирование редиректа для аннонимных пользователей."""
    login_url = reverse('users:login')
    url = reverse(name, kwargs=kwargs)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
