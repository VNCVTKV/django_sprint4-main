from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserProfileForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator


def get_posts(category=None, username=None):
    current_time = timezone.now()
    queryset = Post.objects.select_related(
        'category',
        'location',
        'author',
    ).filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True
    )

    if category:
        queryset = queryset.filter(category__slug=category)
    
    return queryset


def index(request):
    paginator = Paginator(get_posts(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    paginator = Paginator(get_posts(category=category_slug), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}

    return render(request, 'blog/category.html', context)


def post_detail(request, id):
    post = get_object_or_404(get_posts(), id=id)
    form = CommentForm(request.POST or None)
    queryset = Comment.objects.filter(post=id)
    context = {'post': post, 'form': form, 'comments': queryset}
    # Форму с переданным в неё объектом request.GET 
    # записываем в словарь контекста...
    if form.is_valid():
        form.save()
    # ...и отправляем в шаблон.

    return render(request,
                  'blog/detail.html', context)


def create_post(request, pk=None):
    if pk is not None:
        instance = get_object_or_404(Post, id=pk)
    else:
        # Связывать форму с объектом не нужно, установим значение None.
        instance = None    
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}
    # Форму с переданным в неё объектом request.GET 
    # записываем в словарь контекста...
    if form.is_valid():
        form.save()
    # ...и отправляем в шаблон.
    return render(request, 'blog/create.html', context)


def delete_post(request, pk=None):
    instance = get_object_or_404(Post, id=pk)  
    form = PostForm(instance=instance)
    context = {'form': form}
    # Форму с переданным в неё объектом request.GET 
    # записываем в словарь контекста...
    if request.method == 'POST':
        # ...удаляем объект:
        instance.delete()
    # ...и отправляем в шаблон.
    return render(request, 'blog/create.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    paginator = Paginator(get_posts().filter(author__username=username), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def edit_profile(request):
    user = get_object_or_404(User, pk=request.user.id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user) # Передаем POST-данные, файлы и текущий объект
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            return redirect('blog:profile', username=username)  #  Указываем URL-маршрут куда нужно перенаправить после успешного сохранения
    else:
        form = UserProfileForm(instance=user)  

    return render(request, 'blog/user.html', {'form': form})


def add_comment(request, id, pk=None):
    post = get_object_or_404(Post, id=id)
    if pk is not None:
        comment = get_object_or_404(Comment, id=pk)
    else:
        comment = None
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'post': post, 'comment': comment}
    if form.is_valid():
        comment = form.save(commit=False) #создаем или изменяем комент
        comment.author = request.user # устанавливаем автора
        comment.post = post # устанавливаем связь с постом.
        comment.save() # сохраняем в базу.
        return redirect('blog:post_detail', id=id) 

    return render(request, 'blog/comment.html', context)


def delete_comment(request, id, pk):
    post = get_object_or_404(Post, id=id)
    comment = get_object_or_404(Comment, id=pk)
    form = CommentForm(instance=comment)
    context = {'post': post, 'form': form, 'comment': comment}
    # Форму с переданным в неё объектом request.GET 
    # записываем в словарь контекста...
    if request.method == 'POST':
        # ...удаляем объект:
        comment.delete()
    # ...и отправляем в шаблон.
    return render(request, 'blog/comment.html', context)