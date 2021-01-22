import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


USERNAME_1 = 'Kostya'
USERNAME_2 = 'Vika'
GROUP_TITLE_1 = 'Крысы'
GROUP_TITLE_2 = 'Кошки'
GROUP_DESCRIPTION_1 = 'Про крыс'
GROUP_DESCRIPTION_2 = 'Про кошек'
SLUG_GROUP_1 = 'rets'
SLUG_GROUP_2 = 'cats'
ABOUT_AUTHOR_URL = reverse('about:author')
ABOUT_TECH_URL = reverse('about:tech')
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
FOLLOW_INDEX_URL = reverse('follow_index')
GROUP_1_URL = reverse('group',
                      kwargs={'slug': SLUG_GROUP_1})
PROFILE_1_URL = reverse('profile',
                        kwargs={'username': USERNAME_1})
GROUP_2_URL = reverse('group',
                      kwargs={'slug': SLUG_GROUP_2})
PROFILE_2_URL = reverse('profile',
                        kwargs={'username': USERNAME_2})
POST_VIEW_URL = reverse('post', kwargs={
                'username': 'Kostya',
                'post_id': 1}
                )
POST_EDIT_URL = reverse('post_edit', kwargs={
                'username': 'Kostya',
                'post_id': 1}
                )   
TEST_TEXT_1 = 'Тестовый текст про крыс'
TEST_TEXT_2 = 'Тестовый текст про кошек'
TEST_TEXT_STR = 'Тестовый текст '

class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        
        super().setUpClass()
        
        
        group_rets = Group.objects.create(
            title=GROUP_TITLE_1,
            description=GROUP_DESCRIPTION_1,
            slug=SLUG_GROUP_1
        )

        group_cats = Group.objects.create(
            title=GROUP_TITLE_2,
            description=GROUP_DESCRIPTION_2,
            slug=SLUG_GROUP_2
        )
        
        author_kostya = User.objects.create_user(username=USERNAME_1, id=1)
        author_vika = User.objects.create_user(username=USERNAME_2, id=2)
        Follow.objects.get_or_create(user=author_kostya, author=author_vika)
        posts = []

        for i in range(15):
            posts.append(Post(
                id=i,
                text=TEST_TEXT_1,
                author=author_kostya,
                group=group_rets
            ))

        for i in range(15, 30):
            posts.append(Post(
                id=i,
                text=TEST_TEXT_2,
                author=author_vika,
                group=group_cats
            ))            

        Post.objects.bulk_create(posts)

        cls.post = Post.objects.get(id=1)

    def setUp(self):

        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username=USERNAME_1, id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_view_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'index.html': INDEX_URL,            
            'new.html': NEW_POST_URL,
            'about/author.html': ABOUT_AUTHOR_URL,
            'about/tech.html': ABOUT_TECH_URL,
            'group.html': GROUP_1_URL,
            'profile.html': PROFILE_1_URL,

        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template) 


    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)

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
        response = self.authorized_client.get(GROUP_1_URL)
        self.assertEqual(response.context.get('group').title, GROUP_TITLE_1)
        self.assertEqual(response.context.get('group').description, GROUP_DESCRIPTION_1)
        self.assertEqual(response.context.get('group').slug, SLUG_GROUP_1)
        self.assertEqual(len(response.context['page']), 10)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, TEST_TEXT_2)
        self.assertEqual(str(post_author), USERNAME_2)
        self.assertEqual(str(post_group), GROUP_TITLE_2)
        self.assertEqual(post_paginator_count, 10)


    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_1_URL)
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, TEST_TEXT_1)
        self.assertEqual(str(post_author), USERNAME_1)
        self.assertEqual(str(post_group), GROUP_TITLE_1)
        self.assertEqual(response.context.get('count'), 15)
        self.assertEqual(str(response.context.get('author')), USERNAME_1)
        self.assertEqual(post_paginator_count, 10)

    def test_post_view_page_show_correct_context(self):
        """Шаблон post_view сформирован с правильным контекстом.""" 
        response = self.authorized_client.get(POST_VIEW_URL)
        self.assertEqual(str(response.context.get('post')), TEST_TEXT_STR)
        self.assertEqual(response.context.get('count'), 15)
        self.assertEqual(str(response.context.get('author')), USERNAME_1) 
        self.assertEqual(response.context.get('post_id'), 1)

    def test_edit_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""

        response = self.authorized_client.get(POST_EDIT_URL)

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
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()
        self.assertEqual(post_text, TEST_TEXT_2)
        self.assertEqual(str(post_author), USERNAME_2)
        self.assertEqual(str(post_group), GROUP_TITLE_2)
        self.assertEqual(post_paginator_count, 10)

    def test_follow_index_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом не подписанного на автора."""
        self.user = get_user_model().objects.create_user(username=USERNAME_2, id=2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        post_paginator_count = response.context.get('paginator').get_page(1).object_list.count()        
        self.assertEqual(post_paginator_count, 0)
