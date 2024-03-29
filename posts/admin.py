from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):

    list_display = ("pk", "group", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):

    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):

    list_display = ("pk", "post", "text", "created", "author")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):

    list_display = ("pk", "user", "author")
    search_fields = ("user",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
