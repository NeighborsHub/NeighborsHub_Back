from django.contrib import admin

from post.models import Post, Category, Comment, LikePost

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(LikePost)
class LikePostAdmin(admin.ModelAdmin):
    pass
