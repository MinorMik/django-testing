from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf
from .urls import HOME_URL, LOGIN_URL, SIGNUP_URL, LOGOUT_URL

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND


@pytest.mark.parametrize(
    "url, expected_status",
    [
        (HOME_URL, OK),
        (LOGIN_URL, OK),
        (SIGNUP_URL, OK),
    ],
)
def test_public_pages_availability(client, url, expected_status):
    """Проверка доступности публичных страниц (GET)."""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url, client_fixture, expected_status",
    [
        ("edit_url", "author_client", OK),
        ("edit_url", "reader_client", NOT_FOUND),
        ("delete_url", "author_client", OK),
        ("delete_url", "reader_client", NOT_FOUND),
    ],
)
def test_protected_pages_by_client_type(request, url, client_fixture,
                                        expected_status, news):
    """
    Проверка страниц, требующих авторизации и прав.
    Здесь url — это имя фикстуры (edit_url/delete_url), потому что они зависят
    от новости.
    """
    client = request.getfixturevalue(client_fixture)

    url_value = request.getfixturevalue(url)

    response = client.get(url_value)
    assert response.status_code == expected_status


def test_logout_via_post(client):
    """Отдельный тест на logout: он должен делать редирект (302)."""
    response = client.post(LOGOUT_URL)
    assert response.status_code == FOUND


def test_author_can_edit_news(author_client, edit_url):
    response = author_client.get(edit_url)
    assert response.status_code == OK


def test_reader_cannot_edit_news(reader_client, edit_url):
    response = reader_client.get(edit_url)
    assert response.status_code == NOT_FOUND


def test_author_can_delete_news(author_client, delete_url):
    response = author_client.get(delete_url)
    assert response.status_code == OK


def test_reader_cannot_delete_news(reader_client, delete_url):
    response = reader_client.get(delete_url)
    assert response.status_code == NOT_FOUND


@pytest.mark.parametrize(
    "url_fixture_name",
    ["edit_url", "delete_url"],
)
def test_redirect_for_anonymous_client(client, request, url_fixture_name,
                                       news):
    """Проверка перенаправления анонимных пользователей на login."""
    url = request.getfixturevalue(url_fixture_name)
    expected_redirect = f"{LOGIN_URL}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_redirect)
