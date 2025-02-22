"""
views for the tutun_app application
"""

import calendar
import datetime
import json

import requests
import jwt

from taggit.models import Tag

from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from django.contrib.auth import logout, views
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

from django.urls import reverse
from django.urls import reverse_lazy

from django.views import generic
from django.views.generic import CreateView

from tutun.settings import API_YANDEX_MAPS_KEY, SECRET_JWT_KEY
from .forms import UserRegisterForm, PrivateRouteForm, PrivateDotForm, ProfileForm, \
    NoteForm, ComplaintForm, AnswerComplaintForm, AuthTokenBotForm
from .models import User, PrivateRoute, PublicRoute, PrivateDot, Note, Complaint, PublicDot


def get_bar_context(request):
    """
    Инициализация bar(навбар)

    Генерирует нужный навбар в зависимости
    от статуса пользователя авторизован или нет

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`
    """

    if request.user.is_authenticated:
        menu = [
            {'title': str(request.user), 'url': reverse('profile', kwargs={'stat': 'reading'})},
            {'title': 'Все маршруты', 'url': reverse('public_routes')},
            {'title': 'Новый маршрут', 'url': reverse('new_route')},
            {'title': 'Получить токен для тг авторизации', 'url': reverse('tg_token')},
            {'title': 'Обратная связь', 'url': reverse('complaints')},
            {'title': 'Выйти', 'url': reverse('logout')}
        ]

    else:
        menu = [{'title': 'Приветсвенная страница', 'url': reverse('public_routes')}]

    return menu


class MyLoginView(views.LoginView):
    """
    Переопределенние view авторизации
    """

    template_name = 'registration/login.html'
    success_message = 'Вы успешно вошли на сайт!'

    def form_valid(self, form):
        """
        @return: form_valid - если форма коректна, то пользователь авторизируется на сайт
        @rtype: :class:`django.http.HttpResponseRedirect`
        """

        user = form.get_user()

        messages.success(self.request, f'Вы успешно вошли на сайт, {user}!')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        @return: get_context_data - словарь, представляющий контекст шаблона,
        предоставленные аргументы ключевого
        слова будут составлять возвращаемый контекст @rtype: dict
        """

        context = super().get_context_data(**kwargs)

        context.update({
            'bar': get_bar_context(self.request),
            'title': 'Авторизация на сайте'
        })

        return context


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Переопределенние view регистрации

    @param form_class: форма регистрации
    @type form_class: :class:`django.contrib.auth.forms.BaseUserCreationForm`

    @param success_url: url логина
    @type success_url: object

    @param template_name: путь до шаблона логина
    @type template_name: basestring

    @param success_message: текст сообщения, в случаи успешной авторизации
    @type success_message: basestring
    """

    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'

    def get_context_data(self, **kwargs):
        """
        @return Возвращает контекст для генерации страницы регистрации
        @rtype : dict
        """

        context = super().get_context_data(**kwargs)

        context.update({
            'bar': get_bar_context(self.request),
            'title': 'Регистрация на сайте'
        })

        return context

    def get_success_message(self, cleaned_data):
        """
        @return: get_success_message - в случае успешной регистарции выводит сообщение
        @rtype: basestring
        """
        return self.success_message


def logout_view(request):
    """
    "Разлогинивание"

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с url, на который перенаправить пользователя
    @rtype: object
    """

    logout(request)

    messages.success(request, "Вы успешно вышли из учётной записи")

    return redirect('index')


def index_page(request):
    """
    Отображение приветственной страницы

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: возвращает массив с контекстом для приветсвенной страницы
    @rtype: list
    """

    context = {
        'bar': get_bar_context(request),
    }

    return render(request, 'index.html', context)


class PublicRoutesPage(generic.ListView):
    template_name = 'public_routes.html'
    context_object_name = 'routes_list'

    def get_queryset(self):
        """
        Получение списка публичных маршрутов

        @return: список всех маршрутов из базы данных
        """
        return PublicRoute.objects.all()

    def get_context_data(self, **kwargs):
        """

        @param kwargs:
        @return: Возвращает контекст для генерации страниы публичных маршрутов
        """

        context = super().get_context_data(**kwargs)
        routes = self.get_queryset()
        tags = Tag.objects.all()

        context.update({
            'bar': get_bar_context(self.request),
            'routes_list': routes,
            'tags': tags,
        })

        return context


class PublicRoutesTagsPage(generic.ListView):
    """
    Отображение страницы маршрутов по тегу

    @type template_name: str
    @param template_name: Имя шаблона для рендеринга страницы

    @type context_object_name: str
    @param context_object_name: Имя контекстного объекта

    @type model: :class:`django.db.models.Model`
    @param model: Модель данных для маршрутов

    @type paginate_by: int
    @param paginate_by: Количество элементов на страницу

    @type tag: :class:`Tag`
    @param tag: Текущий тег для фильтрации маршрутов

    @return: Возвращает объект  ответа сервера с html-кодом внутри
    @rtype: object
    """
    template_name = 'public_routes.html'
    context_object_name = 'routes_list'
    model = PublicRoute
    paginate_by = 10
    tag = None

    def get_queryset(self):
        """
        Получение списка маршрутов по тегу

        @return: QuerySet с отфильтрованными маршрутами
        @rtype: :class:`django.db.models.QuerySet`
        """
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = PublicRoute.objects.all().filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Обновление контекста для шаблона

        @param kwargs: Дополнительные аргументы контекста
        @return: Обновленный контекст
        @rtype: dict
        """
        context = super().get_context_data(**kwargs)
        tags = Tag.objects.all()
        context.update({
            'bar': get_bar_context(self.request),
            'title': f'Маршруты по тегу: {self.tag.name}',
            'tags': tags,
        })
        return context


class PublicRoutesSearchResults(generic.ListView):
    """
    Отображение страницы результатов поиска маршрутов

    @type template_name: str
    @param template_name: Имя шаблона для рендеринга страницы

    @type context_object_name: str
    @param context_object_name: Имя контекстного объекта

    @return: Возвращает объект  ответа сервера с html-кодом внутри
    @rtype: object
    """
    template_name = 'search_results_public.html'
    context_object_name = 'routes_list'

    def get_queryset(self):
        """
        Получение списка маршрутов по запросу поиска

        @return: QuerySet с найденными маршрутами
        @rtype: :class:`django.db.models.QuerySet`
        """
        query = self.request.GET.get('q')
        object_list = PublicRoute.objects.filter(
            Q(Name__icontains=query)
        )
        return object_list

    def get_context_data(self, **kwargs):
        """
        Обновление контекста для шаблона

        @param kwargs: Дополнительные аргументы контекста
        @return: Возвращает Обновленный контекст
        @rtype: dict
        """
        context = super().get_context_data(**kwargs)
        tags = Tag.objects.all()
        context.update({
            'bar': get_bar_context(self.request),
            'tags': tags,
        })
        return context


@login_required
def profile(request, stat):
    """
    Отображенеие профиля.
    Отображает профиль, также позволяет редактировать,
    обрабатывая формы и сохраняя данные в базу данных.
    @param: request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param: stat: Человек просматривает профиль или редактирует
    @return: str

    @return: Возвращает объект ответа сервера с html-кодом внутри, либо HTTP ответ,
     который перенаправляет клиента на указанный URL
    @rtype: :class:`django.http.HttpResponse` / `HttpResponseRedirect`
    """

    user = request.user

    if user.is_anonymous:
        return redirect('login')

    routes = PrivateRoute.objects.filter(author=user)

    profile_info = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tg_username': user.tg_username
    }

    if request.method == 'POST':
        form = ProfileForm(request.POST)

        if form.is_valid():
            User.objects.filter(id=user.id).update(
                username=form.data["username"],
                email=form.data["email"],
                first_name=form.data["first_name"],
                last_name=form.data["last_name"],
            )

            messages.success(request, "Вы успешно изменили профиль!")

            return redirect(reverse('profile', kwargs={'stat': 'reading'}))

        messages.error(request, "Во время изменения профиля, произошла ошибка")
    else:
        form = ProfileForm(initial={
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tg_username': user.tg_username
        })

    context = {
        'bar': get_bar_context(request),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tg_username': user.tg_username,
        'routes': routes,
        'stat': stat,
        'form': form,
        'profile_info': profile_info,
        'url': reverse('profile', kwargs={'stat': 'editing'}),
        'url_back': reverse('profile', kwargs={'stat': 'reading'})
    }

    return render(request, 'profile.html', context)


@login_required
def create_route(request):
    """
    Создание нового маршрута.
    Обрабатывает формы проверяет данные на валидность и сохраняет их в базу данных.
    Тагже генерирует формы для их последующего заполнения пользователем.

    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с html-кодом внутри, либо HTTP ответ,
     который перенаправляет клиента на указанный URL
    @rtype: :class:`django.http.HttpResponse` / `HttpResponseRedirect`
    """
    error_text = ''

    if request.method == 'POST':
        route_form = PrivateRouteForm(request.POST)

        dot_forms = [PrivateDotForm(request.POST,
                                    prefix=str(x)) for x in range(len(request.POST)) if
                     f'dots-{x}-name' in request.POST]
        note_forms = [NoteForm(request.POST, prefix=str(x)) for x in range(len(request.POST)) if
                      f'notes-{x}-text' in request.POST]

        if route_form.is_valid() and len(dot_forms) != 0:
            route = route_form.save(commit=False)

            route.author = request.user
            route.length = (route.date_out - route.date_in).days
            route.month = calendar.month_name[route.date_in.month]
            route.year = route.date_in.year

            route.save()

            for dot_form in dot_forms:
                dot_data = dot_form.data
                if dot_data[f'dots-{dot_form.prefix}-date']:
                    dot_date = datetime.datetime.strptime(
                        dot_data[f'dots-{dot_form.prefix}-date'],
                        '%Y-%m-%d').date()

                    if dot_date > route.date_out or dot_date < route.date_in:
                        messages.error(request, 'Даты точек должны находиться в пределах путешествия.')

                        context = {
                            'bar': get_bar_context(request),
                            'route_form': route_form,
                            'dot_forms': dot_forms,
                            'note_forms': note_forms,
                        }

                        route.delete()

                        return render(request, 'new_route.html', context)

                dot = PrivateDot(
                    name=dot_data[f'dots-{dot_form.prefix}-name'],
                    date=None,
                    note=dot_data.get(f'dots-{dot_form.prefix}-note'),
                    information=dot_data.get(f'dots-{dot_form.prefix}-information'),
                )

                if (f'dots-{dot_form.prefix}-date' in dot_data and
                        dot_data[f'dots-{dot_form.prefix}-date']):
                    dot.date = dot_data[f'dots-{dot_form.prefix}-date']

                dot.save()
                route.dots.add(dot)

            for note_form in note_forms:
                note_data = note_form.data

                note = Note(
                    text=note_data[f'notes-{note_form.prefix}-text']
                )

                note.save()
                route.note.add(note)

            messages.success(request, 'Маршрут успешно создан.')
            route.tags.set(route_form.cleaned_data.get('tags', []))

            return redirect(reverse('profile', kwargs={'stat': 'reading'}))

        messages.error(request, 'Необходимо добавить хотя бы одну точку.')

    else:
        route_form = PrivateRouteForm()
        dot_forms = []
        note_forms = []

    context = {
        'bar': get_bar_context(request),
        'route_form': route_form,
        'dot_forms': dot_forms,
        'note_forms': note_forms,
        'error_text': error_text,
    }

    return render(request, 'new_route.html', context)


@login_required
def save_route(request, pk=None):
    """
    Копирование публичного маршрута в приватный
    """
    if request.method == 'POST':
        public_route = get_object_or_404(PublicRoute, pk=pk)

        private_route = PrivateRoute.objects.create(
            Name=public_route.Name,
            author=request.user,
            comment=public_route.comment,
            rate=public_route.rate if public_route.rate is not None else 0,
            length=public_route.length,
            month=public_route.month,
            year=public_route.year
        )

        # Копирование точек маршрута
        for public_dot in public_route.dots.all():
            private_dot = PrivateDot.objects.create(
                name=public_dot.name,
                information=public_dot.information
            )
            private_route.dots.add(private_dot)

        # Копирование тегов
        private_route.tags.set(public_route.tags.all())

        messages.success(request, "Маршрут успешно скопирован в приватные!")
        return redirect(reverse('route_detail', kwargs={'route_id': private_route.pk}))

    return HttpResponseNotAllowed(['POST'])  # Укажите страницу ошибки или верните HTTP 405



@login_required()
def route_detail(request, route_id):
    """
    Демонстрация конкретного приватного маршрута.
    Функция получате из базы данных данные, а также
    получает от yandex api geocoder координаты точек по их адресу илил названию.
    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param route_id: id маршрута, который должен отобразиться
    @type route_id: int

    @return: Возвращает объект ответа сервера с html-кодом внутри
    @rtype: :class:`django.http.HttpResponse`
    """
    route = PrivateRoute.objects.get(id=route_id)
    dots = sorted(route.dots.all(), key=lambda dot: dot.date if dot.date else datetime.date.min)
    notes = route.note.all().order_by("id")

    url = 'https://geocode-maps.yandex.ru/1.x/'
    apikey = API_YANDEX_MAPS_KEY

    getparams = {
        'lang': 'ru_RU',
        'apikey': apikey,
        'format': 'json'
    }

    dots_vis = []

    for dot in dots:
        getparams['geocode'] = dot.information

        try:
            response = requests.get(url=url, params=getparams)
            data = response.json()
            try:
                geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                coords = geo_object['Point']['pos'].split()
                inf = geo_object['name']

                dots_vis.append({
                    'name': dot.name,
                    'coords': coords,
                    'inf': inf,
                    'date': str(dot.date)
                })
            except KeyError:
                messages.error(request, 'Произошла непредведенная ошибка.')
        except ConnectionError:
            messages.error(request, 'Эта страница в данный момент не доступна, попробуйте позже.')

    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
        'notes': notes,
        'dots_vis': dots_vis,
        'API_YANDEX_MAPS_KEY': f"https://api-maps.yandex.ru/v3/?apikey={API_YANDEX_MAPS_KEY}&lang=ru_RU"
    }

    return render(request, 'route_detail.html', context)


@login_required()
def public_route_detail(request, route_id):
    """
    Демонстрация конкретного публичного маршрута.
    Функция получате из базы данных данные, а также
    получает от yandex api geocoder координаты точек по их адресу илил названию.
    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param route_id: id маршрута, который должен отобразиться
    @type route_id: int

    @return: Возвращает объект ответа сервера с html-кодом внутри
    @rtype: :class:`django.http.HttpResponse`
    """
    route = get_object_or_404(PublicRoute, id=route_id)
    dots = route.dots.all()

    url = 'https://geocode-maps.yandex.ru/1.x/'
    apikey = API_YANDEX_MAPS_KEY
    getparams = {
        'lang': 'ru_RU',
        'apikey': apikey,
        'format': 'json'
    }

    dots_vis = []

    for dot in dots:
        getparams['geocode'] = dot.information

        try:
            response = requests.get(url=url, params=getparams)
            data = response.json()
            try:
                geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                coords = geo_object['Point']['pos'].split()
                inf = geo_object['name']
                dots_vis.append({
                    'name': dot.name,
                    'coords': coords,
                    'inf': inf,
                })
            except KeyError:
                messages.error(request, 'Произошла непредведенная ошибка.')
        except ConnectionError:
            messages.error(request, 'Эта страница в данный момент не доступна, попробуйте позже.')

    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
        'dots_vis': dots_vis,
        'API_YANDEX_MAPS_KEY': API_YANDEX_MAPS_KEY
    }

    return render(request, 'public_route_detail.html', context)


@login_required
def editing_route(request, route_id):
    """
    Редактирование маршрута
    Функция, сохраняющая изменения в параметрах уже существующих точек, заметок и самого маршурта,
     а также обрабатывает добавление новых точек и заметок.
    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param route_id: id маршрута, к которому нужно применить изменения
    @type route_id: int

    @return: Возвращает объект ответа сервера с html-кодом внутри, либо HTTP ответ,
    который перенаправляет клиента на указанный URL
    @rtype: :class:`django.http.HttpResponse` / `HttpResponseRedirect`
    """
    if request.user != PrivateRoute.objects.get(id=route_id).author:
        return redirect(reverse('main_menu'))

    if request.method == 'POST':
        route = PrivateRoute.objects.get(id=route_id)
        route_form = PrivateRouteForm(request.POST)

        if route_form.is_valid():
            PrivateRoute.objects.filter(id=route_id).update(
                Name=route_form.data['Name'],
                date_in=route_form.data['date_in'],
                date_out=route_form.data['date_out'],
                comment=route_form.data['comment'],
                baggage=route_form.data['baggage'],
                rate=route_form.data['rate'],
                length=(route.date_out - route.date_in).days,
                month=calendar.month_name[route.date_in.month],
                year=route.date_in.year
            )
            route.tags.set(route_form.cleaned_data.get('tags', []))
            new_notes = {"new_text": request.POST.getlist('text')}
            notes = route.note.all()

            for index_note in range(len(notes)):
                Note.objects.filter(id=notes[index_note].id).update(
                    text=new_notes["new_text"][index_note])

            for index_note in range(len(notes), len(new_notes["new_text"])):
                note = Note(text=new_notes["new_text"][index_note])

                note.save()
                route.note.add(note)

            new_dots = {"new_name": request.POST.getlist('name'),
                        "new_note": request.POST.getlist('note'),
                        "new_information": request.POST.getlist('information'),
                        "new_date": request.POST.getlist('date'),
                        }

            dots = route.dots.all()

            for index_dot in range(len(dots)):
                if new_dots['new_date'][index_dot]:
                    dot_date = datetime.datetime.strptime(
                        new_dots['new_date'][index_dot],
                        '%Y-%m-%d').date()

                    if dot_date > route.date_out or dot_date < route.date_in:
                        messages.error(request, 'Даты точек должны находиться в пределах путешествия.')

                        notes = route.note.all().order_by("id")
                        notes_form = []

                        for note in notes:
                            notes_form.append(NoteForm(initial={'text': note.text, }))

                        dots = sorted(route.dots.all(), key=lambda dot: dot.date if dot.date else datetime.date.min)
                        dots_form = []

                        for dot in dots:
                            dots_form.append(PrivateDotForm(initial={
                                'name': dot.name,
                                'note': dot.note,
                                'date': dot.date,
                                'information': dot.information,
                            }))

                        context = {
                            'bar': get_bar_context(request),
                            'route_form': route_form,
                            'dots_form': dots_form,
                            'notes_form': notes_form,
                            'url_back': reverse('route_detail', kwargs={'route_id': route_id})
                        }

                        return render(request, 'editing_route.html', context)

                PrivateDot.objects.filter(id=dots[index_dot].id).update(
                    name=new_dots['new_name'][index_dot],
                    note=new_dots['new_note'][index_dot] if new_dots['new_note'][index_dot] else None,
                    information=new_dots['new_information'][index_dot],
                    date=new_dots['new_date'][index_dot] if new_dots['new_date'][index_dot] else None,
                )

            for index_dot in range(len(dots), len(new_dots["new_name"])):
                dot = PrivateDot(
                    name=new_dots['new_name'][index_dot],
                    note=new_dots['new_note'][index_dot] if new_dots['new_note'][index_dot] else None,
                    information=new_dots['new_information'][index_dot],
                    date=new_dots['new_date'][index_dot] if new_dots['new_date'][index_dot] else None,
                )

                if new_dots['new_date'][index_dot]:
                    dot_date = datetime.datetime.strptime(
                        new_dots['new_date'][index_dot],
                        '%Y-%m-%d').date()

                    if dot_date > route.date_out or dot_date < route.date_in:
                        messages.error(request, 'Даты точек должны находиться в пределах путешествия.')

                        notes = route.note.all().order_by("id")
                        notes_form = []

                        for note in notes:
                            notes_form.append(NoteForm(initial={'text': note.text, }))

                        dots = sorted(route.dots.all(), key=lambda dot: dot.date if dot.date else datetime.date.min)
                        dots_form = []

                        for dot in dots:
                            dots_form.append(PrivateDotForm(initial={
                                'name': dot.name,
                                'note': dot.note,
                                'date': dot.date,
                                'information': dot.information,
                            }))

                        context = {
                            'bar': get_bar_context(request),
                            'route_form': route_form,
                            'dots_form': dots_form,
                            'notes_form': notes_form,
                            'url_back': reverse('route_detail', kwargs={'route_id': route_id})
                        }

                        return render(request, 'editing_route.html', context)

                dot.save()
                route.dots.add(dot)

            messages.success(request, "Вы успешно изменили маршрут!")

            return redirect(reverse('route_detail', kwargs={'route_id': route_id}))

        messages.error(request, "Во время изменения маршрута, произошла ошибка")
    else:
        route = PrivateRoute.objects.get(id=route_id)

        route_form = PrivateRouteForm(initial={
            'Name': route.Name,
            'date_in': route.date_in,
            'date_out': route.date_out,
            'baggage': route.baggage,
            'comment': route.comment,
            'rate': route.rate,
            'tags': route.tags.values_list('id', flat=True)
        })

        notes = route.note.all().order_by("id")
        notes_form = []

        for note in notes:
            notes_form.append(NoteForm(initial={'text': note.text, }))

        dots = sorted(route.dots.all(), key=lambda dot: dot.date if dot.date else datetime.date.min)
        dots_form = []

        for dot in dots:
            dots_form.append(PrivateDotForm(initial={
                'name': dot.name,
                'note': dot.note,
                'date': dot.date,
                'information': dot.information,
            }))

        context = {
            'bar': get_bar_context(request),
            'route_form': route_form,
            'dots_form': dots_form,
            'notes_form': notes_form,
            'url_back': reverse('route_detail', kwargs={'route_id': route_id})
        }

        return render(request, 'editing_route.html', context)


@login_required
def update_note(request, note_id):
    """
    Обновление состояния заметки.
    Функция изменяет состояние заметки (выполненная/невыполненная)

    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param note_id: id заметки, статус которой необходимо изменить
    @type note_id: int

    @return: Возвращает объект JSON ответа сервера
    @rtype: :class:`django.http.JsonResponse`
    """
    if request.method == 'PATCH':
        try:
            note = Note.objects.get(id=note_id)
            done = json.loads(request.body.decode('utf-8')).get('done')
            note.done = done

            note.save()

            return JsonResponse({'status': 'success',
                                 'message': 'Состояние задачи успешно обновлено'})
        except Note.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Задача не найдена'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


@login_required()
def complaints(request):
    """
    Отображение жалоб.
    @param request: Запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с html-кодом внутри
    @rtype: :class:`django.http.HttpResponse`
    """
    if request.user.is_superuser:
        status = 1
        data = Complaint.objects.filter().order_by('data')
    else:
        status = 0
        data = Complaint.objects.filter(author=request.user)

    data = list(reversed(data))

    context = {
        'bar': get_bar_context(request),
        'data': data,
        'status': status
    }

    return render(request, 'complaints.html', context)


@login_required()
def create_complaint(request):
    """
    Создание Жалоб.
    Функция создаёт формы для их заполнения,
    а также обрабатывает заполненные и сохраняет данные в базу данных.

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с html-кодом внутри, либо HTTP ответ,
    который перенаправляет клиента на указанный URL
    @rtype: :class:`django.http.HttpResponse` / `HttpResponseRedirect`
    """

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            saver_form = Complaint(
                text=form.data['text'],
                author=request.user,
                data=datetime.datetime.now())
            saver_form.save()

            messages.success(request, "Вы успешно отправили жалобу!")

            return redirect(reverse('complaints'))

        messages.error(request, "Во время отправки жалобы, произошла ошибка")
    else:
        form = ComplaintForm

        context = {
            'bar': get_bar_context(request),
            'form': form
        }

    return render(request, 'create_complaint.html', context)


@login_required()
def complaint_answer(request, complaint_id):
    """
    Ответ на жалобу.
    Функция создаёт формы для их заполнения,
    а также обрабатывает заполненные и сохраняет данные в базу данных.
    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @param complaint_id: id жалобы
    @type complaint_id: int

    @return: Возвращает объект ответа сервера с html-кодом внутри, либо HTTP ответ,
    который перенаправляет клиента на указанный URL
    @rtype: :class:`django.http.HttpResponse` / `HttpResponseRedirect`
    """

    complaint = Complaint.objects.filter(id=complaint_id)

    if request.method == 'POST':
        answer_form = AnswerComplaintForm(request.POST)

        if answer_form.is_valid():
            complaint.update(answer=answer_form.data["answer"])

            messages.success(request, "Вы успешно отправили ответ на жалобу!")

            return redirect(reverse('complaints'))

        messages.error(request, "Во время отправки ответа на жалобу, произошла ошибка")
    else:
        answer_form = AnswerComplaintForm(initial={
            'answer': complaint[0].answer,
        })

    context = {
        'bar': get_bar_context(request),
        'form': answer_form,
        'complaint': Complaint.objects.get(id=complaint_id),
        'url': reverse('complaint_answer', args=(complaint_id,))
    }

    return render(request, 'complaint_answer.html', context)


@login_required()
def post_route(request, id):
    """
    Публикайия маршрута.
    Копирует маршрут без приватных данных в публичные маршруты.

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: HTTP ответ, который перенаправляет клиента на указанный URL
    @rtype: :class:`HttpResponseRedirect`
    """
    private_route = get_object_or_404(PrivateRoute, id=id)
    public_dots = []

    public_route = PublicRoute.objects.create(
        Name=private_route.Name,
        author=request.user,
        comment=private_route.comment,
        rate=private_route.rate,
        length=private_route.length,
        month=private_route.month,
        year=private_route.year,
    )

    public_route.save()

    for dot in private_route.dots.all():
        public_dot, created = PublicDot.objects.get_or_create(
            name=dot.name,
            information=dot.information
        )

        public_dots.append(public_dot)

    public_route.dots.set(public_dots)
    public_route.tags.add(*private_route.tags.names())

    messages.success(request, "Вы успешно опубликоватли маршрут!")

    return redirect(reverse('public_route_detail', kwargs={'route_id': public_route.id}))


@login_required()
def get_tg_token(request):
    """
    Страница с токеном для авторизации в телеграмм боте.
    Генерирует форму с JWT-токеном, который отправляется боту для авторизации.

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с html-кодом внутри
    @rtype: :class:`django.http.HttpResponse`
    """
    user = User.objects.get(username=request.user)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    payload = {'username': user.username, 'exp': expiration_time}

    secret_key = SECRET_JWT_KEY
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')

    token_form = AuthTokenBotForm(initial={'token': jwt_token})

    messages.success(request, 'Токен успешно сгенерирован')

    context = {
        'bar': get_bar_context(request),
        'token_form': token_form
    }

    return render(request, 'get_token_bot.html', context)


def yandex_maps(request):
    """
    Функция подключения к яндекс карте.
    Отправляет запрос к API и передаёт ответ.

    @param request: запрос на страницу
    @type request: :class:`django.http.HttpRequest`

    @return: Возвращает объект ответа сервера с html-кодом внутри,
    либо json в котом указывается какая ошибка именно ошибка произошла
    @rtype: :class:`django.http.HttpResponse` / `django.http.JsonResponse`
    """
    url = "https://api-maps.yandex.ru/v3/"
    params = {
        "apikey": API_YANDEX_MAPS_KEY,
        "lang": "ru_RU"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        safe_response = response.text.replace(API_YANDEX_MAPS_KEY, "api_key_hidden")
        return HttpResponse(safe_response, content_type="application/x-javascript")
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=400)