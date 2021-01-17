import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User, Follow


class CheckPostForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        Post.objects.create(
            id=1,
            text='Кролики - это не только ценный мех',
            author=User.objects.create_user(username='Inga', id=1),
            group=Group.objects.create(
                title='Кролики',
                description='Про кроликов',
                slug='rabbits'
            )
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


    def setUp(self):       
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Inga', id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_create_post_with_pic(self):
        """Валидная форма создает запись Post с картинкой."""

        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Кролики - это не только ценный мех 2',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(Post.objects.filter(
            text='Кролики - это не только ценный мех 2'
        ).exists())


    def test_text_label(self):
        """ Проверка label для формы PostForm """
        text_label = CheckPostForm.form.fields['text'].label 
        self.assertEqual(text_label, 'Текст')

    def test_text_help_text(self):
        """ Проверка help_text для формы PostForm """
        text_help_text = CheckPostForm.form.fields['text'].help_text 
        self.assertEqual(text_help_text, 'Введите текст вашего поста')

    def test_creat_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Кролики - это не только ценный мех 2',
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), post_count+1)
        self.assertTrue(Post.objects.filter(
            text='Кролики - это не только ценный мех 2'
        ).exists())
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Кролики - это мясо',
        }

        response = self.authorized_client.post(
            reverse('post_edit',
                kwargs={
                    'username': 'Inga',
                    'post_id': 1,
                    }
            ),
            data=form_data,
            follow=True
        )
        post_text = response.context.get('post').text
        self.assertRedirects(response, '/Inga/1/')        
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_text, 'Кролики - это мясо')
        self.assertEqual(response.status_code, 200)

    def test_cache_index_page(self):
        """ Проеврка кэширования главной страницы """
        html_index_0 = self.guest_client.get('/')

        form_data = {
            'text': 'Кролики - это не только ценный мех 2',
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        html_index_1 = self.guest_client.get('/')
        self.assertHTMLEqual(
            str(html_index_0.content), 
            str(html_index_1.content),
            'Что-то пошло не так'
            )


    def test_unfollowing(self):
        """ Авторизованный пользователь может подписаться и отписаться на автора """
        self.user = get_user_model().objects.create_user(username='Vasya', id=2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.post(
            reverse('profile_follow',
                kwargs={
                    'username': 'Inga',
                    }
            )     
        )
        follow_list = Follow.objects.filter(user=self.user)
        follow_list_count = Follow.objects.filter(user=self.user).count()
        print(str(follow_list_count))
        self.assertEqual(follow_list_count, 1)
        self.assertEqual(str(follow_list[0].author), 'Inga')
        self.assertEqual(response.status_code, 200)        
        response = self.authorized_client.post(
            reverse('profile_unfollow',
                kwargs={
                    'username': 'Inga',
                    }
            )     
        )
        follow_list_count = Follow.objects.filter(user=self.user).count()
        self.assertEqual(follow_list_count, 0)
        self.assertEqual(response.status_code, 200)
