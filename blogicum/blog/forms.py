from django import forms

# Импортируем класс модели Birthday.
from .models import Post, Comment

from django.contrib.auth import get_user_model
from django.utils import timezone  # Для работы с часовыми поясами
import datetime

User = get_user_model()


# Для использования формы с моделями меняем класс на forms.ModelForm.
class PostForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        # Указываем, что надо отобразить все поля.
        exclude = ['author',]
        



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)