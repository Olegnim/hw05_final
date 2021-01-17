from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    text = forms.CharField(
        label='Текст',
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True,
        help_text='Введите текст вашего поста'
    )
    class Meta:

        model = Post
        fields = [
            'group',
            'text',
            'image',
        ]
        labels = {
            'group': 'Группы',
        }
        attrs = {
            'group': 'form-control',
        }


class CommentForm(forms.ModelForm):

    text = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True,
        help_text='Введите вашего комментария'        
    )
    class Meta:

        model = Comment
        fields = [
            'text',
        ]
