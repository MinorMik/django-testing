from http import HTTPStatus

from notes.tests.base import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        """Доступность публичных страниц
        для анонимного пользователя.
        """
        urls = (
            ("home", self.home_url),
            ("login", self.login_url),
            ("signup", self.signup_url),
        )
        for name, url in urls:
            with self.subTest(page=name, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability_via_post(self):
        """Logout доступен по POST и возвращает OK."""
        with self.subTest(url=self.logout_url, method="POST"):
            response = self.client.post(self.logout_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Страницы, доступные авторизованному читателю."""
        urls = (
            ("list", self.list_url),
            ("add", self.add_url),
            ("success", self.success_url),
        )
        for name, url in urls:
            with self.subTest(client="reader", page=name, url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Права доступа к detail/edit/delete:
        автор — OK,
        читатель — NOT_FOUND.
        """
        users_statuses = (
            ("author", self.author_client, HTTPStatus.OK),
            ("reader", self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ("detail", self.detail_url),
            ("edit", self.edit_url),
            ("delete", self.delete_url),
        )

        for client_name, client, expected_status in users_statuses:
            for url_name, url in urls:
                with self.subTest(
                    client=client_name,
                    page=url_name,
                    url=url,
                    expected_status=expected_status.value
                ):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Анонимному пользователю на защищённые страницы — редирект."""
        urls = (
            ("list", self.list_url),
            ("add", self.add_url),
            ("success", self.success_url),
            ("detail", self.detail_url),
            ("edit", self.edit_url),
            ("delete", self.delete_url),
        )
        for page_name, url in urls:
            redirect_url = f"{self.login_url}?next={url}"
            with self.subTest(
                client="anonymous",
                page=page_name,
                url=url,
                redirect_to=redirect_url
            ):
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
