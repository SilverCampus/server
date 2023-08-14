from django.contrib import admin

from .models import BoardPost, BoardComment, BoardPostLike

admin.site.register(BoardPost)
admin.site.register(BoardComment)
admin.site.register(BoardPostLike)