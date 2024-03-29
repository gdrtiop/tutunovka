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

from .models import User, PrivateRoute, PublicRoute, PrivateDot
from .forms import UserRegisterForm, PrivateRouteForm, PrivateDotForm, ProfileForm


def get_bar_context(request):
    menu = []
    if request.user.is_authenticated:
        menu.append(dict(title=str(request.user), url=reverse('profile', kwargs={'stat': 'reading'})))
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


@login_required()
def create_route(request):
    if request.method == 'POST':
        route_form = PrivateRouteForm(request.POST)
        dot_forms = [PrivateDotForm(request.POST, prefix=str(x)) for x in range(5) if f'dots-{x}-name' in request.POST]
        if route_form.is_valid() and len(dot_forms) != 0:
            route = route_form.save(commit=False)
            route.author = request.user
            route.save()
            for dot_form in dot_forms:
                dot_data = dot_form.data
                if f'dots-{dot_form.prefix}-name' in dot_data:
                    dot = PrivateDot(
                        name=dot_data[f'dots-{dot_form.prefix}-name'],
                        api_vision=dot_data.get(f'dots-{dot_form.prefix}-api_vision'),
                        note=dot_data.get(f'dots-{dot_form.prefix}-note'),
                        information=dot_data.get(f'dots-{dot_form.prefix}-information')
                    )
                    dot.save()
                    route.dots.add(dot)
            return redirect(reverse('profile', kwargs={'stat': 'reading'}))
        else:
            '''
            print("Форма неверна или не все точки валидны.")
            print("Ошибки основной формы:", route_form.errors)
            for dot_form in dot_forms:
                print(f"Ошибки формы точки {dot_form.prefix}: {dot_form.errors}")
                '''
            pass
    else:
        route_form = PrivateRouteForm()
        dot_forms = [PrivateDotForm(prefix=str(x)) for x in range(5)]

    return render(request, 'new_route.html', {'route_form': route_form, 'dot_forms': dot_forms})


@login_required()
def route_detail(request, route_id):
    route = PrivateRoute.objects.get(id=route_id)
    dots = PrivateDot.objects.filter(privateroute=route)
    context = {
        'bar': get_bar_context(request),
        'route': route,
        'dots': dots,
    }
    return render(request, 'route_detail.html', context)


@login_required()
def reduction_route(request, route_id):
    if request.user != PrivateRoute.objects.get(id=route_id).author:
        return redirect(reverse('main_menu'))

    if request.method == 'POST':
        route_form = PrivateRouteForm(request.POST)
        dot_forms = [PrivateDotForm(request.POST, prefix=str(x)) for x in range(5) if f'dots-{x}-name' in request.POST]
        if route_form.is_valid() and len(dot_forms) != 0:
            PrivateRoute.objects.filter(id=route_id).update(Name=route_form.data['Name'],
                                                            date_in=route_form.data['title'],
                                                            date_out=route_form.data['date_out'],
                                                            comment=route_form.data['comment'],
                                                            baggage=route_form.data['baggage'],
                                                            note=route_form.data['note'],
                                                            rate=route_form.data['rate'],
                                                            dots=route_form.data['dots'],
                                                            )
            for dot_form in dot_forms:
                dot_data = dot_form.data
                if f'dots-{dot_form.prefix}-name' in dot_data:
                    PrivateDot.objects.filter(privateroute=PrivateRoute.objects.get(id=route_id)).update(
                        name=dot_form.data['name'],
                        api_vision=dot_form.data['api_vision'],
                        note=dot_form.data['note'],
                        information=dot_form.data['information'],
                        )
            return redirect(reverse('profile', kwargs={'stat': 'reading'}))
        else:
            '''
            print("Форма неверна или не все точки валидны.")
            print("Ошибки основной формы:", route_form.errors)
            for dot_form in dot_forms:
                print(f"Ошибки формы точки {dot_form.prefix}: {dot_form.errors}")
                '''
            pass
    else:
        route_form = PrivateRouteForm()
        dot_forms = [PrivateDotForm(prefix=str(x)) for x in range(5)]

    return render(request, 'new_route.html', {'route_form': route_form, 'dot_forms': dot_forms})
