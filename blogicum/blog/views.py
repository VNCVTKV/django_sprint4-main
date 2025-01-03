from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserProfileForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def get_posts(category=None, username=None):
    queryset = Post.with_comments_count().select_related(
        'category',
        'location',
        'author',
    ).filter(
        is_published=True,
        category__is_published=True
    )

    if category:
        queryset = queryset.filter(category__slug=category)
    
    return queryset


def index(request):
    current_time = timezone.now()
    paginator = Paginator(get_posts().filter(pub_date__lte=current_time,).order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    current_time = timezone.now()
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    paginator = Paginator(get_posts(category=category_slug).filter(pub_date__lte=current_time,).order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}

    return render(request, 'blog/category.html', context)


def post_detail(request, id):
    post = get_object_or_404(get_posts() | request.user.posts.all(), id=id)
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


# @login_required
# def create_post(request, pk=None):
#        if pk is not None:
#            instance = get_object_or_404(Post, id=pk)
#            if request.user != instance.author:
#       #         return redirect('blog:post_detail', id=pk)
#        else:
#            # Связывать форму с объектом не нужно, установим значение None.
#            instance = None
#        form = PostForm(request.POST or None, files=request.FILES or None, instance=instance)
#        context = {'form': form}
#         Форму с переданным в неё объектом request.GET 
#         записываем в словарь контекста...
#        if form.is_valid():
#            post = form.save(commit=False)
#            post.author = request.user
#            post.save()
#            return redirect('blog:post_detail', id=post.id) 
#         ...и отправляем в шаблон.
#         return render(request, 'blog/create.html', context)

@login_required
def create_post(request):
    template = 'blog/create.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, pk):
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('blog:post_detail', pk)
    context = {'form': form}
    return render(request, template, context)


# @login_required
# def delete_post(request, pk):
#     instance = get_object_or_404(Post, id=pk)  
#     form = PostForm(instance=instance)
#     if request.user != instance.author:
#         return redirect('blog:post_detail', id=pk) 
#     context = {'form': form}
#     # Форму с переданным в неё объектом request.GET 
#     # записываем в словарь контекста...
#     if request.method == 'POST':
#         # ...удаляем объект:
#         instance.delete()
#         return redirect('blog:post_detail', id=pk)
#     # ...и отправляем в шаблон.
#     return render(request, 'blog/create.html', context)
@login_required
def delete_post(request, pk):
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, template, context)


def profile(request, username):
    current_time = timezone.now()
    queryset = Post.with_comments_count().select_related(
        'category',
        'location',
        'author',
    ).filter(Q(author__username=username,) & Q(pub_date__lte=current_time,) 
             | Q(author__username=request.user.username,) & Q(pub_date__gt=current_time,))
    profile = get_object_or_404(User, username=username)
    paginator = Paginator(queryset.order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
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


@login_required
def add_comment(request, id, pk=None):
    post = get_object_or_404(Post, id=id)
    if pk is not None:
        comment = get_object_or_404(Comment, id=pk)
        if request.user != comment.author:
            return redirect('blog:post_detail', id=id) 
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


@login_required
def delete_comment(request, id, pk):
    post = get_object_or_404(Post, id=id)
    comment = get_object_or_404(Comment, id=pk)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=id) 
    context = {'post': post, 'comment': comment}
    # Форму с переданным в неё объектом request.GET 
    # записываем в словарь контекста...
    if request.method == 'POST':
        # ...удаляем объект:
        comment.delete()
        return redirect('blog:post_detail', id=id)
    # ...и отправляем в шаблон.
    return render(request, 'blog/comment.html', context)