from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.urls import reverse

from django.contrib.auth import login as auth_login

from datetime import datetime, timedelta


# К форуму
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.views.generic import ListView
from django.utils import timezone

# Подключение моделей
from django.contrib.auth.models import User, Group

from django.db import models
from django.db.models import Q

from .models import Board, Topic, Post, Reviews, News
# Подключение форм
from .forms import BoardForm, NewTopicForm, PostForm, ReviewsForm, NewsForm, SignUpForm

from django.contrib.auth.models import AnonymousUser

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

# Стартовая страница 
def index(request):
    news1 = News.objects.all().order_by('-daten')[0:1]
    news24 = News.objects.all().order_by('-daten')[1:4]
    reviews = Reviews.objects.exclude(rating=None).order_by('?')[0:4]
    return render(request, "index.html", {"news1": news1, "news24": news24 ,"reviews": reviews, })    

# Контакты
def contact(request):
    return render(request, "contact.html")

# Общая информация о компании
def about(request):
    return render(request, "info/about.html")

# Фотогалерея
def photogallery(request):
    return render(request, "info/photogallery.html")

# Филиалы
def branch(request):
    return render(request, "info/branch.html")

def forum(request):
    boards = Board.objects.all()
    return render(request, 'forum/home.html', {'boards': boards})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'forum/topics.html', {'board': board, 'topics': topics})

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def board_index(request):
    board = Board.objects.all().order_by('name')
    return render(request, "board/index.html", {"board": board})

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def board_create(request):
    if request.method == "POST":
        board = Board()        
        board.name = request.POST.get("name")
        board.description = request.POST.get("description")
        board.save()
        return HttpResponseRedirect(reverse('board_index'))
    else:        
        boardform = BoardForm()
        return render(request, "board/create.html", {"form": boardform})

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def board_edit(request, id):
    try:
        board = Board.objects.get(id=id) 
        if request.method == "POST":
            board.name = request.POST.get("name")
            board.description = request.POST.get("description")
            board.save()
            return HttpResponseRedirect(reverse('board_index'))
        else:
            # Загрузка начальных данных
            boardform = BoardForm(initial={'name': board.name, 'description': board.description })
            return render(request, "board/edit.html", {"form": boardform})
    except Board.DoesNotExist:
        return HttpResponseNotFound("<h2>Board not found</h2>")

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def board_delete(request, id):
    try:
        board = Board.objects.get(id=id)
        board.delete()
        return HttpResponseRedirect(reverse('board_index'))
    except Board.DoesNotExist:
        return HttpResponseNotFound("<h2>Board not found</h2>")

# Просмотр страницы read.html для просмотра объекта.
@login_required
def board_read(request, id):
    try:
        board = Board.objects.get(id=id) 
        return render(request, "board/read.html", {"board": board})
    except Board.DoesNotExist:
        return HttpResponseNotFound("<h2>Board not found</h2>")

@login_required
def new_topic(request, pk):
    try:
        board = get_object_or_404(Board, pk=pk)
        if request.method == 'POST':
            form = NewTopicForm(request.POST)
            if form.is_valid():
                topic = form.save(commit=False)
                topic.board = board
                topic.starter = request.user  # <- here
                topic.save()
                Post.objects.create(
                    message=form.cleaned_data.get('message'),
                    topic=topic,
                    created_by=request.user  # <- and here
                )
                return redirect('topic_posts', pk=pk, topic_pk=topic.pk)  # <- here
                #return redirect('board_topics', pk=board.pk)  # TODO: redirect to the created topic page
        else:
            form = NewTopicForm()
        return render(request, 'forum/new_topic.html', {'board': board, 'form': form})
    except Exception as error:
        print(error)


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'forum/topic_posts.html', {'topic': topic})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()  # <- здесь
            topic.save()                         # <- здесь

            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'forum/reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'forum/edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)    

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'forum/topic_posts.html'
    paginate_by = 20
    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <- здесь
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True           # <- пока здесь

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)
    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def news_index(request):
    try:
        news = News.objects.all().order_by('-daten')
        return render(request, "news/index.html", {"news": news})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
def news_list(request):
    try:
        news = News.objects.all().order_by('-daten')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                news_search = request.POST.get("news_search")
                #print(news_search)                
                if news_search != '':
                    news = news.filter(Q(news_title__contains = news_search) | Q(details__contains = news_search)).all()                
                return render(request, "news/list.html", {"news": news, "news_search": news_search, })    
            else:          
                return render(request, "news/list.html", {"news": news})                 
        else:
            return render(request, "news/list.html", {"news": news}) 
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def news_create(request):
    try:
        if request.method == "POST":
            news = News()        
            news.daten = request.POST.get("daten")
            news.news_title = request.POST.get("news_title")
            news.details = request.POST.get("details")
            if 'photo' in request.FILES:                
                news.photo = request.FILES['photo']   
            newsform = NewsForm(request.POST)
            if newsform.is_valid():
                news.save()
                return HttpResponseRedirect(reverse('news_index'))
            else:
                return render(request, "news/create.html", {"form": newsform})
        else:        
            newsform = NewsForm(initial={'daten': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), })
            return render(request, "news/create.html", {"form": newsform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def news_edit(request, id):
    try:
        news = News.objects.get(id=id) 
        if request.method == "POST":
            news.daten = request.POST.get("daten")
            news.news_title = request.POST.get("news_title")
            news.details = request.POST.get("details")
            if "photo" in request.FILES:                
                news.photo = request.FILES["photo"]
            newsform = NewsForm(request.POST)
            if newsform.is_valid():
                news.save()
                return HttpResponseRedirect(reverse('news_index'))
            else:
                return render(request, "news/edit.html", {"form": newsform})
        else:
            # Загрузка начальных данных
            newsform = NewsForm(initial={'daten': news.daten.strftime('%Y-%m-%d %H:%M:%S'), 'news_title': news.news_title, 'details': news.details, 'photo': news.photo })
            return render(request, "news/edit.html", {"form": newsform})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def news_delete(request, id):
    try:
        news = News.objects.get(id=id)
        news.delete()
        return HttpResponseRedirect(reverse('news_index'))
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
#@login_required
def news_read(request, id):
    try:
        news = News.objects.get(id=id) 
        return render(request, "news/read.html", {"news": news})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для просмотра
def reviews_list(request):
    reviews = Reviews.objects.all().order_by('-dater')
    return render(request, "reviews/list.html", {"reviews": reviews})

# Список для просмотра с кнопкой удалить
@login_required
@group_required("Managers")
def reviews_index(request):
    reviews = Reviews.objects.all().order_by('-dater')
    return render(request, "reviews/index.html", {"reviews": reviews})

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
def reviews_create(request):
    if request.method == "POST":
        reviews = Reviews()        
        reviews.rating = request.POST.get("rating")
        reviews.details = request.POST.get("details")
        reviews.user = request.user
        reviewsform = ReviewsForm(request.POST)
        if reviewsform.is_valid():
            reviews.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "reviews/create.html", {"form": reviewsform})     
    else:        
        reviewsform = ReviewsForm(initial={'rating': 5, })
        return render(request, "reviews/create.html", {"form": reviewsform})

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def reviews_delete(request, id):
    try:
        reviews = Reviews.objects.get(id=id)
        reviews.delete()
        return HttpResponseRedirect(reverse('reviews_index'))
    except Reviews.DoesNotExist:
        return HttpResponseNotFound("<h2>Reviews not found</h2>")

###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return HttpResponseRedirect(reverse('index'))
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")



