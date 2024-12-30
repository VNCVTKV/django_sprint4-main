from django import forms

# Импортируем класс модели Birthday.
from .models import Post, Comment


# Для использования формы с моделями меняем класс на forms.ModelForm.
class PostForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        # Указываем, что надо отобразить все поля.
        fields = '__all__' 


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)