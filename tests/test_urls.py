from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post, User


INDEX_URL = '/'
ABOUT_AUTHOR_URL = '/about/author/'
ABOUT_TECH_URL = '/about/tech/'
NEW_POST_URL = '/new'
GROUP_URL = '/group/rets/'
PROFILE_URL = '/Kostya/'
POST_URL = '/Kostya/1/'
POST_EDIT_URL = '/Kostya/1/edit/'
COMMENT_URL = '/Kostya/1/comment'
WRONG_URL = '/wrong/url/'
GROUP_TITLE = 'Крысы'
GROUP_DESCRIPTION = 'Про крыс'
GROUP_SLUG = 'rets'
USERNAME = 'Kostya'
USERNAME2 = 'Yulya'


class StaticURLTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_homepage(self):
        """ Проверка доступности главной страницы """
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        """ Проверка доступности страницы about"""
        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        """ Проверка доступности страницы tech """
        response = self.guest_client.get(ABOUT_TECH_URL)
        self.assertEqual(response.status_code, 200)

    def test_wrong_url(self):
        """ Проверка возврата ошибки 404"""
        response = self.guest_client.get(WRONG_URL)
        self.assertEqual(response.status_code, 404)

class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        
        super().setUpClass()
        
        Post.objects.create(
            id=1,
            text='Тестовый текст',
            author=User.objects.create_user(username=USERNAME, id=1),
            group=Group.objects.create(
                title=GROUP_TITLE,
                description=GROUP_DESCRIPTION,
                slug=GROUP_SLUG
            )

        )

    def setUp(self):

        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username=USERNAME, id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_urls_auth_users_uses_correct_template(self):
        """URL-адрес для авторизованного пользователя использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': INDEX_URL,
            'new.html': NEW_POST_URL,
            'group.html': GROUP_URL,
            'profile.html': PROFILE_URL,
            'post.html': POST_URL,
            'post_new.html': POST_EDIT_URL,
            'comments.html': COMMENT_URL,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)


    def test_urls_guest_uses_correct_template(self):
        """URL-адрес для гостя использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': INDEX_URL,
            'group.html': GROUP_URL,
            'profile.html': PROFILE_URL,
            'post.html': POST_URL,
            'registration/login.html': POST_EDIT_URL,
            'registration/login.html': COMMENT_URL,
        }
        for template, reverse_name in templates_url_names.items():            
            with self.subTest():
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)


    def test_urls_edit_post_uses_correct_template(self):
        """ URL-адрес при редактировании поста другим пользователем использует соответствующий шаблон. """
        self.userx = get_user_model().objects.create_user(username=USERNAME2, id=2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.userx)        
        response = self.authorized_client.get(POST_EDIT_URL, follow=True)
        self.assertTemplateUsed(response, 'post.html')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get(POST_EDIT_URL)
        self.assertEqual(response.status_code, 302)
        
    def test_new_guest_redirect(self):
        """ Перенаправления гостя при попытке создать запись """
        response = self.guest_client.get(NEW_POST_URL)
        self.assertEqual(response.status_code, 302)
