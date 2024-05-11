import json
import datetime
from datetime import datetime
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.messages.views import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from taggit.models import Tag
import calendar
from .models import User, PrivateRoute, PublicRoute, PrivateDot, Note, Complaint, PublicDot
from .forms import UserRegisterForm, PrivateRouteForm, PrivateDotForm, ProfileForm, NoteForm, ComplaintForm, \
    AnswerComplaintForm


def get_bar_context(request):
    menu = []
    if request.user.is_authenticated:
        menu.append(dict(title=str(request.user), url=reverse('profile', kwargs={'stat': 'reading'})))
        menu.append(dict(title='все маршруты', url=reverse('public_routes')))
        menu.append(dict(title='новый маршрут', url=reverse('new_route')))
        menu.append(dict(title='Обратная связь', url=reverse('complaints')))
        menu.append(dict(title='Выйти', url=reverse('logout')))
    else:
        menu.append(dict(title=str(request.user), url='#'))

    return menu


class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'

        return context


def logout_view(request):
    logout(request)
    return redirect('index')


def index_page(request):
    context = {
        'bar': get_bar_context(request),
        'author': 'mother...', 'creation_date': '15.03.2024',
        'user': request.user}
    return render(request, 'index.html', context)


class PublicRoutesPage(generic.ListView):
    template_name = 'public_routes.html'
    context_object_name = 'routes_list'

    def get_queryset(self):
        return PublicRoute.objects.all()


class PublicRoutesTagsPage(generic.ListView):
    template_name = 'public_routes.html'
    context_object_name = 'routes_list'
    model = PublicRoute
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = PublicRoute.objects.all().filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Маршруты по тегу: {self.tag.name}'
        return context


class PublicRoutesSearchResults(generic.ListView):
    template_name = 'search_results_public.html'
    context_object_name = 'routes_list'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = PublicRoute.objects.filter(
            Q(Name__icontains=query)
        )
        return object_list


@login_required()
def profile(request, stat):
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
            User.objects.filter(id=user.id).update(username=form.data["username"], email=form.data["email"],
                                                   first_name=form.data["first_name"], last_name=form.data["last_name"],
                                                   tg_username=form.data["tg_username"])

            return redirect(reverse('profile', kwargs={'stat': 'reading'}))
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
    error_text = ''
    if request.method == 'POST':
        route_form = PrivateRouteForm(request.POST)
        dot_forms = [PrivateDotForm(request.POST, prefix=str(x)) for x in range(len(request.POST)) if
                     f'dots-{x}-name' in request.POST]
        note_forms = [NoteForm(request.POST, prefix=str(x)) for x in range(len(request.POST)) if
                      f'notes-{x}-text' in request.POST]

        if route_form.is_valid() and len(dot_forms) != 0:
            route = route_form.save(commit=False)
            route.author = request.user
            route.length = (route.date_out - route.date_in).days  # Calculate length in days
            route.month = calendar.month_name[route.date_in.month]
            route.year = route.date_in.year  # Extract year from date_in
            route.save()

            for dot_form in dot_forms:
                dot_data = dot_form.data
                dot_date = datetime.strptime(dot_data[f'dots-{dot_form.prefix}-date'], '%Y-%m-%d').date()
                if dot_date > route.date_out.date() or dot_date < route.date_in.date():
                    messages.success(request, 'Даты точек должны находиться в пределах путешествия.')
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
                    api_vision=dot_data.get(f'dots-{dot_form.prefix}-api_vision'),
                    date=None,
                    note=dot_data.get(f'dots-{dot_form.prefix}-note'),
                    information=dot_data.get(f'dots-{dot_form.prefix}-information'),

                )

                if f'dots-{dot_form.prefix}-date' in dot_data and dot_data[f'dots-{dot_form.prefix}-date']:
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

            route.tags.set(route_form.cleaned_data['tags'])

            return redirect(reverse('profile', kwargs={'stat': 'reading'}))
        elif len(dot_forms) == 0:
            messages.success(request, 'Необходимо добавить хотя бы одну точку.')
        else:
            pass
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
    error_text = ''
    data = get_object_or_404(PublicRoute, pk=pk)
    if request.method == 'POST':
        print(request.POST)
        route_form = PrivateRouteForm(request.POST)
        dot_forms = [PrivateDotForm(request.POST, prefix=str(x)) for x in range(len(request.POST)) if
                     f'dots-{x}-name' in request.POST]
        note_forms = [NoteForm(request.POST, prefix=str(x)) for x in range(len(request.POST)) if
                      f'notes-{x}-text' in request.POST]

        if len(dot_forms) + len(request.POST.getlist('date')) != 0:
            route = route_form.save(commit=False)
            route.author = request.user
            route.length = (route.date_out - route.date_in).days
            route.month = calendar.month_name[route.date_in.month]
            route.year = route.date_in.year
            route.save()

            for i in range(len(request.POST.getlist('date'))):
                #этот for позволяет обрабатывать точки, которые были до создания и сохранять их
                dot_date = datetime.strptime(request.POST.getlist('date')[i], '%Y-%m-%d').date()
                if dot_date > route.date_out.date() or dot_date < route.date_in.date():
                    messages.success(request, 'Даты точек должны находиться в пределах путешествия.')
                    context = {
                        'bar': get_bar_context(request),
                        'route_form': route_form,
                        'dot_forms': dot_forms,
                        'note_forms': note_forms,
                    }
                    route.delete()
                    return render(request, 'new_route.html', context)
                dot = PrivateDot(
                    name=request.POST.getlist('name')[i],
                    api_vision=request.POST.getlist('api_vision')[i],
                    date=request.POST.getlist('date')[i],
                    note=request.POST.getlist('note')[i],
                    information=request.POST.getlist('information')[i],
                )
                dot.save()
                route.dots.add(dot)

            for dot_form in dot_forms:
                dot_data = dot_form.data
                dot_date = datetime.strptime(dot_data[f'dots-{dot_form.prefix}-date'], '%Y-%m-%d').date()
                if dot_date > route.date_out.date() or dot_date < route.date_in.date():
                    messages.success(request, 'Даты точек должны находиться в пределах путешествия.')
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
                    api_vision=dot_data.get(f'dots-{dot_form.prefix}-api_vision'),
                    date=None,
                    note=dot_data.get(f'dots-{dot_form.prefix}-note'),
                    information=dot_data.get(f'dots-{dot_form.prefix}-information'),

                )

                if f'dots-{dot_form.prefix}-date' in dot_data and dot_data[f'dots-{dot_form.prefix}-date']:
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

            route.tags.set(route_form.cleaned_data['tags'])

            return redirect(reverse('profile', kwargs={'stat': 'reading'}))
        elif len(dot_forms) + len(request.POST.getlist('date')) == 0:
            messages.success(request, 'Необходимо добавить хотя бы одну точку.')
            return redirect(reverse('public_route_detail', kwargs={'route_id': pk}))
        else:
            pass
    else:
        route = data
        route_form = PrivateRouteForm(initial={
            'Name': route.Name,
            'comment': route.comment,
            'rate': route.rate,
        })
        note_forms = []
        dots = route.dots.all()
        dot_forms = []
        for dot in dots:
            dot_forms.append(PrivateDotForm(initial={
                'name': dot.name,
                'api_vision': dot.api_vision,
                'information': dot.information,
            }))

    context = {
        'bar': get_bar_context(request),
        'route_form': route_form,
        'dot_forms': dot_forms,
        'note_forms': note_forms,
        'error_text': error_text,
    }
    return render(request, 'new_route.html', context)


@login_required()
def route_detail(request, route_id):
    route = PrivateRoute.objects.get(id=route_id)
    dots = route.dots.all()
    notes = route.note.all()
    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
        'notes': notes,
    }
    return render(request, 'route_detail.html', context)


@login_required()
def public_route_detail(request, route_id):
    route = get_object_or_404(PublicRoute, id=route_id)
    dots = route.dots.all()
    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
    }
    return render(request, 'public_route_detail.html', context)


@login_required()
def editing_route(request, route_id):
    if request.user != PrivateRoute.objects.get(id=route_id).author:
        return redirect(reverse('main_menu'))

    if request.method == 'POST':
        route = PrivateRoute.objects.get(id=route_id)
        route_form = PrivateRouteForm(request.POST)
        if route_form.is_valid():
            PrivateRoute.objects.filter(id=route_id).update(Name=route_form.data['Name'],
                                                            date_in=route_form.data['date_in'],
                                                            date_out=route_form.data['date_out'],
                                                            comment=route_form.data['comment'],
                                                            baggage=route_form.data['baggage'],
                                                            rate=route_form.data['rate'],
                                                            length=(route.date_out - route.date_in).days,
                                                            month=calendar.month_name[route.date_in.month],
                                                            year=route.date_in.year
                                                            )
            new_notes = {"new_text": request.POST.getlist('text')}
            notes = route.note.all()
            for index_note in range(len(notes)):
                Note.objects.filter(id=notes[index_note].id).update(text=new_notes["new_text"][index_note])
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
            for index_note in range(len(dots)):
                PrivateDot.objects.filter(id=dots[index_note].id).update(name=new_dots['new_name'][index_note],
                                                                         note=new_dots['new_note'][index_note],
                                                                         information=new_dots['new_information'][
                                                                             index_note],
                                                                         date=new_dots['new_date'][index_note],
                                                                         )
            for index_note in range(len(dots), len(new_dots["new_name"])):
                dot = PrivateDot(name=new_dots['new_name'][index_note],
                                 note=new_dots['new_note'][index_note],
                                 information=new_dots['new_information'][index_note],
                                 date=new_dots['new_date'][index_note],
                                 )
                dot.save()
                route.dots.add(dot)
            return redirect(reverse('route_detail', kwargs={'route_id': route_id}))
    else:
        route = PrivateRoute.objects.get(id=route_id)
        route_form = PrivateRouteForm(initial={
            'Name': route.Name,
            'date_in': route.date_in,
            'date_out': route.date_out,
            'baggage': route.baggage,
            'comment': route.comment,
            'rate': route.rate,
        })
        notes = route.note.all()
        notes_form = []
        for note in notes:
            notes_form.append(NoteForm(initial={'text': note.text, }))
        dots = route.dots.all()
        dots_form = []
        for dot in dots:
            dots_form.append(PrivateDotForm(initial={
                'name': dot.name,
                'note': dot.note,
                'date': dot.date,
                'api_vision': dot.api_vision,
                'information': dot.information,
            }))

        return render(request, 'editing_route.html',
                      {'route_form': route_form, 'dots_form': dots_form, 'notes_form': notes_form})


def update_note(request, note_id):
    if request.method == 'PATCH':
        try:
            note = Note.objects.get(id=note_id)
            done = json.loads(request.body.decode('utf-8')).get('done')  # Преобразование в булево значение
            note.done = done
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Состояние задачи успешно обновлено'})
        except Note.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Задача не найдена'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


@login_required()
def complaints(request):
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
def creat_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            saver_form = Complaint(text=form.data['text'], author=request.user, data=datetime.datetime.now())
            saver_form.save()

            context = {
                'bar': get_bar_context(request),
                'form': form,
                'text': form.data['text']
            }

    else:
        form = ComplaintForm

        context = {
            'bar': get_bar_context(request),
            'form': form
        }

    return render(request, 'creat_complaint.html', context)


@login_required()
def comlaint_answer(request, id):
    if request.method == 'POST':
        answer_form = AnswerComplaintForm(request.POST)
        comlaint = Complaint.objects.filter(id=id)

        if answer_form.is_valid():
            comlaint.update(answer=answer_form.data["answer"])

            return redirect(reverse('complaints'))
        else:
            answer_form = AnswerComplaintForm(initial={
                'answer': comlaint.answer,
            })

        context = {
            'bar': get_bar_context(request),
            'text': comlaint.text,
            'author': comlaint.author,
            'answer': comlaint.answer,
            'data': comlaint.data,
            'form': answer_form
        }

        return render(request, 'complaints.html', context)


@login_required()
def post_route(request, id):
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
            api_vision=dot.api_vision,
            information=dot.information
        )
        public_dots.append(public_dot)

    public_route.dots.set(public_dots)
    public_route.tags.add(*private_route.tags.names())

    return redirect(reverse('public_route_detail', kwargs={'route_id': public_route.id}))
