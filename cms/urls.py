from django.urls import path
from .views import post_grid_view, post_detail_view

app_name = 'cms'

urlpatterns = [
    path('posts/', post_grid_view, name='post_grid'),
    path('posts/<slug:slug>/', post_detail_view, name='post_detail'),
]