from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone
from notes.models import Note

User = get_user_model()


class NotesTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='Автор', password='testpass'
        )
        self.reader = User.objects.create_user(
            username='Читатель', password='testpass'
        )

        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметок',
            slug='note-slug',
            author=self.author,
            pub_date=timezone.now(),
        )

        self.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }

    def test_something_with_note(self):
        response = self.author_client.get(f'/notes/{self.note.slug}/')
        self.assertEqual(response.status_code, 200)
