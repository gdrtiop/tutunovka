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
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required

from .models import User
from .forms import UserRegisterForm


def get_bar_context(request):
    menu = []
    if request.user.is_authenticated:
        menu.append(dict(title=str(request.user), url=reverse('me-my')))
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


def memy_page(request):
    context = {
        'bar': get_bar_context(request),
        'test': 'it works!'
    }
    return render(request, 'me-my.html', context)
