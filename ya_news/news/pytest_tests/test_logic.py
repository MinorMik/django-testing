from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .urls import LOGIN_URL

pytestmark = pytest.mark.django_db

COMMENT_FORM_DATA = {"text": "Новый текст комментария"}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Аноним не может создать комментарий."""
    comments_count_before = Comment.objects.count()
    response = client.post(detail_url, data=COMMENT_FORM_DATA)

    expected_url = f"{LOGIN_URL}?next={detail_url}"

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count_before


def test_user_can_create_comment(author_client, author, news, detail_url):
    """Авторизованный пользователь успешно создает комментарий."""
    Comment.objects.all().delete()

    response = author_client.post(detail_url, data=COMMENT_FORM_DATA)

    expected_url = f"{detail_url}#comments"

    comment = Comment.objects.get()

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    assert comment.text == COMMENT_FORM_DATA["text"]
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    """Сначала проверяем количество записей в БД, затем — ошибку формы."""
    comments_count_before = Comment.objects.count()
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS}, еще текст"}

    response = author_client.post(detail_url, data=bad_words_data)

    form = response.context['form']

    assert Comment.objects.count() == comments_count_before
    assertFormError(form, "text", WARNING)


def test_author_can_delete_comment(
    author_client, comment, detail_url, delete_url
):
    """Автор может успешно удалить свой собственный комментарий."""
    comments_count_before = Comment.objects.count()
    expected_url = f'{detail_url}#comments'

    response = author_client.delete(delete_url)

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(
    reader_client, comment, delete_url
):
    """Обычный пользователь НЕ может удалить чужой комментарий."""
    comments_count_before = Comment.objects.count()

    response = reader_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before


def test_author_can_edit_comment(
    author_client, comment, news, detail_url, edit_url
):
    """Извлекаем объект через get(), сверяем неизменность автора и новости."""
    expected_url = f'{detail_url}#comments'

    response = author_client.post(edit_url, data=COMMENT_FORM_DATA)

    updated_comment = Comment.objects.get(id=comment.id)

    assertRedirects(response, expected_url)
    assert updated_comment.text == COMMENT_FORM_DATA["text"]
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, edit_url
):
    """Другой пользователь получает 404, поля сущности остаются прежними."""
    response = reader_client.post(edit_url, data=COMMENT_FORM_DATA)

    updated_comment = Comment.objects.get(id=comment.id)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert updated_comment.text == comment.text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
