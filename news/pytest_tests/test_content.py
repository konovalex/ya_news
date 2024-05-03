import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_homepage_contains_news_by_pages(client, many_news):
    """Новости разбиты постранично и отсортированы от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE
    news_list = [news.date for news in object_list]
    sorted_news_list = sorted(news_list, reverse=True)
    assert news_list == sorted_news_list


@pytest.mark.django_db
def test_detail_news_sorted_comments(client, many_comments, pk_for_news):
    """Комментарии в новости отсортированы от старых к новым."""
    url = reverse('news:detail', kwargs=pk_for_news)
    response = client.get(url)
    assert 'news' in response.context
    news_list = response.context['news']
    all_comments = news_list.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
        'parametrize_client, form_is_contains',
        (
            (pytest.lazy_fixture('author_client'), True),
            (pytest.lazy_fixture('client'), False)
        )
)
@pytest.mark.django_db
def test_detail_page_contains_form(
    pk_for_news, parametrize_client, form_is_contains
):
    """Авторизованному пользователю отображается форма комментария."""
    url = reverse('news:detail', kwargs=pk_for_news)
    response = parametrize_client.get(url)
    is_form_exists = ('form' in response.context)
    assert is_form_exists is form_is_contains
    if is_form_exists:
        assert isinstance(response.context['form'], CommentForm)
