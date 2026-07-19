from http import HTTPStatus

from notes.tests.base import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_public_pages_availability(self):
        """Проверка доступности публичных страниц
        (GET) для анонимного клиента."""
        urls = (self.home_url, self.login_url, self.signup_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_via_post(self):
        """Logout доступен по POST и возвращает OK"""
        with self.subTest(url=self.logout_url):
            response = self.client.post(self.logout_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_pages_for_reader(self):
        """Страницы, доступные авторизованному читателю
        (list, add, success)."""
        urls = (self.list_url, self.add_url, self.success_url)
        for url in urls:
            with self.subTest(url=url, client="reader"):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_access_permissions(self):
        """
        Проверка прав доступа к detail/edit/delete:
          - автор: OK
          - читатель: NOT_FOUND
        """
        test_cases = [
            # (client, expected_status)
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        ]
        urls = (self.detail_url, self.edit_url, self.delete_url)

        for client, expected_status in test_cases:
            for url in urls:
                with self.subTest(client="author" if client is
                                  self.author_client else "reader",
                                  url=url,
                                  expected_status=expected_status.value):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous(self):
        """Анонимному пользователю на защищённые страницы
        — редирект на login?next=..."""
        protected_urls = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in protected_urls:
            redirect_url = f"{self.login_url}?next={url}"
            with self.subTest(url=url, redirect_to=redirect_url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
