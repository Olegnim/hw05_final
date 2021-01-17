from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_homepage(self):
        """ Проверка доступности главной страницы """
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        """ Проверка доступности страницы about"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        """ Проверка доступности страницы tech """
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_wrong_url(self):
        """ Проверка возврата ошибки 404"""
        response = self.guest_client.get('/wrong/url/')
        self.assertEqual(response.status_code, 404)

class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        
        super().setUpClass()
        
        Post.objects.create(
            id=1,
            text='Тестовый текст',
            author=User.objects.create_user(username='Kostya', id=1),
            group=Group.objects.create(
                title='Крысы',
                description='Про крыс',
                slug='rets'
            )

        )

    def setUp(self):

        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Kostya', id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_urls_auth_users_uses_correct_template(self):
        """URL-адрес для авторизованного пользователя использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'new.html': '/new',
            'group.html': '/group/rets/',
            'profile.html': '/Kostya/',
            'post.html': '/Kostya/1/',
            'post_new.html': '/Kostya/1/edit/',
            'comments.html': '/Kostya/1/comment',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)


    def test_urls_guest_uses_correct_template(self):
        """URL-адрес для гостя использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/rets/',
            'profile.html': '/Kostya/',
            'post.html': '/Kostya/1/',
            'registration/login.html': '/Kostya/1/edit/',
            'registration/login.html': '/Kostya/1/comment',
        }
        for template, reverse_name in templates_url_names.items():            
            with self.subTest():
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)


    def test_urls_edit_post_uses_correct_template(self):
        """ URL-адрес при редактировании поста другим пользователем использует соответствующий шаблон. """
        self.userx = get_user_model().objects.create_user(username='Yulya', id=2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.userx)        
        response = self.authorized_client.get('/Kostya/1/edit/', follow=True)
        self.assertTemplateUsed(response, 'post.html')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/Kostya/1/edit/')
        self.assertEqual(response.status_code, 302)
        
    def test_new_guest_redirect(self):
        """ Перенаправления гостя при попытке создать запись """
        response = self.guest_client.get('/new')
        self.assertEqual(response.status_code, 302)
