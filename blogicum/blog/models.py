from django.db import models

from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Count


User = get_user_model()

# Create your models here.


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории' 

    def __str__(self):
        return self.title 
    

class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения' 

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать отложенные публикации.',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'

    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    
    image = models.ImageField(blank=True,
                              upload_to='post_image',
                              verbose_name='Изображение')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации' 

    def __str__(self):
        return self.title 
    
    @classmethod
    def with_comments_count(cls, queryset=None):
       """Вычисляет количество комментов для каждого поста и добавляет это как поле `comments_count`."""
       if queryset is None:
          queryset = cls.objects.all()
       return queryset.annotate(comment_count = Count('comments'))


class Comment(BaseModel):
    text = models.TextField('Текст комментария')

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',) 

