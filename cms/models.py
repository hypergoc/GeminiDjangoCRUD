from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

class PostCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = "Post Category"
        verbose_name_plural = "Post Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ManyToManyField(PostCategory, related_name='posts', blank=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    published = models.BooleanField(default=False)
    date_of_publishing = models.DateTimeField(blank=True, null=True)
    share_on_instagram = models.BooleanField(default=False)
    share_on_facebook = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_of_publishing']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.published and self.date_of_publishing is None:
            self.date_of_publishing = timezone.now()
        
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        super().save(*args, **kwargs)

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_path = models.ImageField(upload_to='post_images/')
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.post.title} (Order: {self.order})"