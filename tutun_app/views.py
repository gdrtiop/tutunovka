from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required

from .models import User, Route, Route_for_list, Dot
from .forms import UserRegisterForm, RouteForm, DotForm


def get_bar_context(request):
    menu = []
    if request.user.is_authenticated:
        menu.append(dict(title=str(request.user), url=reverse('me-my')))
        menu.append(dict(title='новый маршрут', url=reverse('new_route')))
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

class IndexView(generic.ListView):
    template_name = 'tutun_app/index.html'
    context_object_name = 'routes_list'

    def get_queryset(self):
        return Route_for_list.objects



@login_required()
def memy_page(request):
    user = request.user
    routes = Route.objects.filter(author=user)

    profile_info = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    context = {
        'bar': get_bar_context(request),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'routes': routes,
        'profile_info': profile_info
    }
    return render(request, 'me-my.html', context)


@login_required()
def create_route(request):
    if request.method == 'POST':
        route_form = RouteForm(request.POST)
        dot_forms = [DotForm(request.POST, prefix=str(x)) for x in range(5) if f'dots-{x}-name' in request.POST]
        if route_form.is_valid() and len(dot_forms) != 0:
            route = route_form.save(commit=False)
            route.author = request.user
            route.save()
            for dot_form in dot_forms:
                dot_data = dot_form.data
                if f'dots-{dot_form.prefix}-name' in dot_data:
                    dot = Dot(
                        name=dot_data[f'dots-{dot_form.prefix}-name'],
                        api_vision=dot_data.get(f'dots-{dot_form.prefix}-api_vision'),
                        note=dot_data.get(f'dots-{dot_form.prefix}-note'),
                        information=dot_data.get(f'dots-{dot_form.prefix}-information')
                    )
                    dot.save()
                    route.dots.add(dot)
            return redirect('me-my')
        else:
            '''
            print("Форма неверна или не все точки валидны.")
            print("Ошибки основной формы:", route_form.errors)
            for dot_form in dot_forms:
                print(f"Ошибки формы точки {dot_form.prefix}: {dot_form.errors}")
                '''
            pass
    else:
        route_form = RouteForm()
        dot_forms = [DotForm(prefix=str(x)) for x in range(5)]

    return render(request, 'new_route.html', {'route_form': route_form, 'dot_forms': dot_forms})


@login_required()
def route_detail(request, route_id):
    route = Route.objects.get(id=route_id)
    dots = Dot.objects.filter(route=route)
    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
    }
    return render(request, 'route_detail.html', context)
