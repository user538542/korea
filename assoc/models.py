from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from django.core.files.storage import default_storage as storage  

from django.contrib.auth.models import User

import math

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# choices (список выбора). Итератор (например, список или кортеж) 2-х элементных кортежей,
# определяющих варианты значений для поля.
# При определении, виджет формы использует select вместо стандартного текстового поля
# и ограничит значение поля указанными значениями.

# Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необязательное читабельное название.
# Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
# null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
# blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
# Это не то же что и null. null относится к базе данных, blank - к проверке данных.
# Если поле содержит blank=True, форма позволит передать пустое значение.
# При blank=False - поле обязательно.

# Раздел форума
class Board(models.Model):
    name = models.CharField(_('board_name'), max_length=128, unique=True)
    description = models.TextField(_('board_description'))
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'board'
    def __str__(self):
        return self.name

# Тема форума   
class Topic(models.Model):
    subject = models.CharField(_('topic_subject'), max_length=255)
    last_updated = models.DateTimeField(_('last_updated'), auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(_('views'), default=0)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'topic'
    def __str__(self):
        return self.subject
    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)
    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6
    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

# Сообщение (POST) для форума
class Post(models.Model):
    message = models.TextField(_('message'),max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created_at'),auto_now_add=True)
    updated_at = models.DateTimeField(_('updated_at'),null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'post'
    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

# Новости 
class News(models.Model):
    daten = models.DateTimeField(_('daten'))
    news_title = models.CharField(_('news_title'), max_length=256)
    details = models.TextField(_('news_details'))
    photo = models.ImageField(_('news_photo'), upload_to='images/', blank=True, null=True)    
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'news'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['daten']),
        ]
        # Сортировка по умолчанию
        ordering = ['daten']
    #def save(self):
    #    super().save()
    #    img = Image.open(self.photo.path) # Open image
    #    # resize image
    #    if img.width > 512 or img.height > 700:
    #        proportion_w_h = img.width/img.height  # Отношение ширины к высоте 
    #        output_size = (512, int(512/proportion_w_h))
    #        img.thumbnail(output_size) # Изменение размера
    #        img.save(self.photo.path) # Сохранение

# Отзывы 
class Reviews(models.Model):
    dater = models.DateTimeField(_('dater_reviews'), auto_now_add=True)
    rating = models.IntegerField(_('rating'), blank=True, null=True)
    details = models.TextField(_('details_reviews'))
    user = models.ForeignKey(User, related_name='reviews_user', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'reviews'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['dater']),
        ]
        # Сортировка по умолчанию
        ordering = ['dater']
