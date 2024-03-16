from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import Route, Dot


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """
    tg_username = forms.CharField(max_length=100)  # Add the tg_username field here

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'tg_username')

    def clean_email(self):
        """
        Проверка email на уникальность
        """
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Такой email уже используется в системе')
        return email

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields['username'].widget.attrs.update({"placeholder": 'Придумайте свой логин'})
            self.fields['email'].widget.attrs.update({"placeholder": 'Введите свой email'})
            self.fields['first_name'].widget.attrs.update({"placeholder": 'Ваше имя'})
            self.fields["last_name"].widget.attrs.update({"placeholder": 'Ваша фамилия'})
            self.fields['password1'].widget.attrs.update({"placeholder": 'Придумайте свой пароль'})
            self.fields['password2'].widget.attrs.update({"placeholder": 'Повторите придуманный пароль'})
            self.fields['tg_username'].widget.attrs.update({"placeholder": 'Введите ваш тг ник'})
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class DotForm(forms.ModelForm):
    class Meta:
        model = Dot
        fields = ['name', 'api_vision', 'note', 'information']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'information': forms.TextInput(attrs={'class': 'form-control'})
        }


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['Name', 'date_in', 'date_out', 'baggage', 'note', 'dots']
        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'}),
            'date_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'baggage': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '1', 'max': '10'}),
            'dots': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        self.fields['dots'].required = False
