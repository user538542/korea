from django.contrib import admin

from .models import Board, Topic, Post, Reviews, News

# Добавление модели на главную страницу интерфейса администратора
admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Reviews)
admin.site.register(News)
