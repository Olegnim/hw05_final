import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User, Follow


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        
        super().setUpClass()
        
        
        group_rets = Group.objects.create(
            title='Крысы',
            description='Про крыс',
            slug='rets'
        )

        group_cats = Group.objects.create(
            title='Кошки',
            description='Про кошек',
            slug='cats'
        )
        
        author_kostya = User.objects.create_user(username='Kostya', id=1)
        author_vika = User.objects.create_user(username='Vika', id=2)
        Follow.objects.get_or_create(user=author_kostya, author=author_vika)
        posts = []

        for i in range(15):
            posts.append(Post(
                id=i,
                text='Тестовый текст про крыс',
                author=author_kostya,
                group=group_rets
            ))

        for i in range(15, 30):
            posts.append(Post(
                id=i,
                text='Тестовый текст про кошек',
                author=author_vika,
                group=group_cats
            ))            

        Post.objects.bulk_create(posts)

        cls.post = Post.objects.get(id=1)

    def setUp(self):

        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Kostya', id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_view_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'index.html': reverse('index'),            
            'new.html': reverse('new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            'group.html': 
                reverse('group', kwargs={'slug': 'rets'}),
            'profile.html': 
                reverse('profile', kwargs={'username': 'Kostya'}),

        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template) 


    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {       
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.fields.ImageField,
        }        

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'rets'})
        )
        self.assertEqual(response.context.get('group').title, 'Крысы')
        self.assertEqual(response.context.get('group').description, 'Про крыс')
        self.assertEqual(response.context.get('group').slug, 'rets')
        self.assertEqual(len(response.context['page']), 10)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, 'Тестовый текст про кошек')
        self.assertEqual(str(post_author), 'Vika')
        self.assertEqual(str(post_group), 'Кошки')
        self.assertEqual(post_paginator_count, 10)


    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'Kostya'})
        )
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, 'Тестовый текст про крыс')
        self.assertEqual(str(post_author), 'Kostya')
        self.assertEqual(str(post_group), 'Крысы')
        self.assertEqual(response.context.get('count'), 15)
        self.assertEqual(str(response.context.get('author')), 'Kostya')
        self.assertEqual(post_paginator_count, 10)

    def test_post_view_page_show_correct_context(self):
        """Шаблон post_view сформирован с правильным контекстом.""" 
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': 'Kostya',
                'post_id': 1}
            )
        )
        self.assertEqual(str(response.context.get('post')), 'Тестовый текст ')
        self.assertEqual(response.context.get('count'), 15)
        self.assertEqual(str(response.context.get('author')), 'Kostya') 
        self.assertEqual(response.context.get('post_id'), 1)

    def test_edit_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""

        response = self.authorized_client.get(            
            reverse('post_edit', kwargs={
                'username': 'Kostya',
                'post_id': 1,
                }
            )
        )

        form_fields = {       
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }        

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


    def test_follow_index_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом для пользователя подписанного на автора."""
        response = self.authorized_client.get(reverse('follow_index'))
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, 'Тестовый текст про кошек')
        self.assertEqual(str(post_author), 'Vika')
        self.assertEqual(str(post_group), 'Кошки')
        self.assertEqual(post_paginator_count, 10)

    def test_follow_index_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом не подписанного на автора."""
        self.user = get_user_model().objects.create_user(username='Vika', id=2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse('follow_index'))
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()        
        self.assertEqual(post_paginator_count, 0)
