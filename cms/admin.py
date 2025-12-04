from django.contrib import admin
from .models import Post, PostCategory, PostImage

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image_path', 'order')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'published', 'date_of_publishing', 'created_at')
    list_filter = ('published', 'category')
    search_fields = ('title', 'subtitle', 'content')
    filter_horizontal = ('category',)
    inlines = [PostImageInline]
    date_hierarchy = 'date_of_publishing'
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'subtitle', 'content', 'category')
        }),
        ('Publishing', {
            'fields': ('published', 'date_of_publishing')
        }),
        ('Social Media', {
            'fields': ('share_on_instagram', 'share_on_facebook'),
            'classes': ('collapse',)
        }),
    )