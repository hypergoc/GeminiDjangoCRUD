from django.shortcuts import render, get_object_or_404
from .models import Post

def post_grid_view(request):
    posts = Post.objects.filter(published=True).order_by('-date_of_publishing').prefetch_related('images')
    context = {
        'posts': posts
    }
    return render(request, 'cms/post_grid.html', context)

def post_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    context = {
        'post': post
    }
    return render(request, 'cms/post_detail.html', context)