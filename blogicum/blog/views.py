from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.utils import timezone


def get_posts(category=None):
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
    post_list = get_posts().order_by('-pub_date')[:5]
    return render(request, 'blog/index.html', {'post_list': post_list})


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)

    post_list = get_posts(category_slug)

    return render(request, 'blog/category.html',
                  {'category': category, 'post_list': post_list})


def post_detail(request, id):
    post = get_object_or_404(get_posts(), id=id)

    return render(request,
                  'blog/detail.html', {'post': post})