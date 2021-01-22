from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок'
    )
    slug = models.SlugField(
        max_length=75,
        unique=True,
        verbose_name='Группа',
        help_text='Название группы'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текст',
        help_text='Введите текст вашего поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберете группу'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Загрузите изображение'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        # str_return = (
        #    str(self.author) + ' / ' +
        #    str(self.pub_date.strftime('%d.%m.%Y')) + ' / ' +
        #    str(self.group) + ' / ' +
        #    str(self.text)[0:50] + '...'
        # )
        # Для тестов возврат 15ти символов текста
        str_return = str(self.text)[:15]
        return str_return


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Запись',
        help_text='Запись'
    )

    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий',
        help_text='Введите текст вашего комментария'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации комментария'
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.text)[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор'
    )
