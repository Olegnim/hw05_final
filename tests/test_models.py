import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        
        super().setUpClass()
        
        Post.objects.create(
            id=1,
            text='Тестовый текст',
            author=User.objects.create_user(username='vasya', id=1),
            group=Group.objects.create(
                title='Крысы',
                description='Про крыс',
                slug='rets'
            )

        )

        cls.post = Post.objects.get(id=1)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'author': 'Автор',
            'pub_date': 'Дата публикации'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст вашего поста',
            'group': 'Выберете группу',
            'author': 'Автор',
            'pub_date': 'Дата публикации'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
    
    def test_object_name_is_group(self):
        """__str__  post - это строчка с содержимым post.group."""
        post = PostModelTest.post
        expected_object_name = 'Крысы'
        actual_object_name = str(post.group)
        self.assertEqual(expected_object_name, actual_object_name)

    def test_object_name_is_post(self):
        """__str__  post - это строчка с содержимым post."""
        post = PostModelTest.post
        #expected_object_name = f'vasya / {datetime.datetime.now():%d.%m.%Y} / Крысы / Тестовый текст...'
        expected_object_name = 'Тестовый текст'
        actual_object_name = str(post)
        self.assertEqual(expected_object_name, actual_object_name)
