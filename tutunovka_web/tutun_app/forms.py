"""
forms for the tutun_app application
"""

from django import forms

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from taggit.models import Tag

from .models import PrivateRoute, PrivateDot, Note, Complaint


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """

    class Meta(UserCreationForm.Meta):
        """
        Метамодель

        @param: fields: поля пользователя при регистрации
        @type: fields: list

        """
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def clean_email(self):
        """
        Проверка email на уникальность

        @return: значение email
        @rtype: basestring

        @raise: :class:'django.core.exceptions.ValidationError' если email уже есть в базе данных
        """

        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Такой email уже используется в системе')

        return email

    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """

        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields['username'].widget.attrs.update({"placeholder": 'Придумайте свой логин'})
            self.fields['email'].widget.attrs.update({"placeholder": 'Введите свой E-mail'})
            self.fields['first_name'].widget.attrs.update({"placeholder": 'Ваше имя'})
            self.fields["last_name"].widget.attrs.update({"placeholder": 'Ваша фамилия'})
            self.fields['password1'].widget.attrs.update({"placeholder": 'Придумайте свой пароль'})
            self.fields['password2'].widget.attrs.update({"placeholder": 'Повторите пароль'})
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class ProfileForm(forms.Form):
    """
    Форма профиля

    @param: username: Логин
    @type: username: basestring

    @param: email: Почта
    @type: email: basestring

    @param: first_name: Имя
    @type: first_name: basestring

    @param: second_name: Фимлия
    @type: second_name: basestring
    """

    username = forms.CharField(
        label='Логин',
        max_length=100,
        min_length=4,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите свой логин'}
        )
    )
    email = forms.EmailField(
        label='Email',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите свой E-mail'}
        )
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        min_length=2,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}
        )
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        min_length=2,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия'}
        )
    )


class PrivateDotForm(forms.ModelForm):
    """
    Форма точки для приватного маршрута
    """
    date = forms.DateField(
        label='Дата',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    note = forms.CharField(
        label='Заметка',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    class Meta:
        """
        Метамодель
        """

        model = PrivateDot
        fields = ['name', 'information', 'date', 'note']
        labels = {
            'name': 'Имя',
            'information': 'Адрес/Название',
            'date': 'Дата',
            'note': 'Заметка',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'information': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PrivateRouteForm(forms.ModelForm):
    """
    Форма приватного маршрута
    """

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Теги'
    )

    rate = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '-1', 'max': '10'}),
        initial=0
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label='Комментарий'
    )

    baggage = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label='Багаж'
    )

    class Meta:
        """
        Метамодель
        """

        model = PrivateRoute
        fields = ['Name', 'comment', 'date_in', 'date_out', 'baggage', 'rate', 'tags']
        labels = {
            'Name': 'Название',
            'comment': 'Комментарий',
            'date_in': 'Дата начала',
            'date_out': 'Дата окончания',
            'baggage': 'Багаж',
            'rate': 'Оценка',
            'tags': 'Теги',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class NoteForm(forms.ModelForm):
    """
    Форма заметок
    """

    text = forms.CharField(label='Заметка')

    class Meta:
        """
        Метамодель
        """

        model = Note
        fields = ['text']
        labels = {
            'text': 'Заметка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }


class TagSelectMultiple(forms.SelectMultiple):
    """
    Выбор тэгов
    """

    def render_options(self, *args, **kwargs):
        """
        Override render_options to include selected attribute for selected tags.

        @return: строку тэгов
        @rtype: basestring
        """

        selected_choices = set([str(v) for v in self.value()])
        output = []

        for group in self.choices:
            group_output = []

            for value, label in group:
                if str(value) in selected_choices:
                    group_output.append(
                        '<option value="%s" selected="selected">%s</option>' % (
                            forms.html.escape(value), forms.html.escape(label)
                        )
                    )
                else:
                    group_output.append(
                        '<option value="%s">%s</option>' % (
                            forms.html.escape(value), forms.html.escape(label)
                        )
                    )

            output.append('\n'.join(group_output))

        return '\n'.join(output)


class TagsField(forms.MultipleChoiceField):
    """
    Поле для выбора тегов
    """

    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """
        super().__init__(*args, **kwargs)
        self.queryset = Tag.objects.all()
        self.widget = TagSelectMultiple()


class ComplaintForm(forms.ModelForm):
    """
    Форма для записи жалобы
    """

    class Meta:
        """
        Метамодель

        @param: model: модель жалоб
        @type: model: :class:'Complaint'

        @param: fields: поля жалоб
        @type: fields: list

        @param: widgets: словарь полей ввода для жалоб
        @type: widgets: dict
        """

        model = Complaint
        fields = ['text']
        labels = {
            'text': 'Текст',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }


class AnswerComplaintForm(forms.ModelForm):
    """
    Метамодель

    @param: model: модель жалоб
    @type: model: :class:'Complaint'

    @param: fields: поля ответа на жалобу
    @type: fields: list

    @param: widgets: словарь полей ввода для ответа на жалобу
    @type: widgets: dict
    """

    class Meta:
        model = Complaint
        fields = ['answer']
        labels = {
            'answer': 'Ответ',
        }
        widgets = {
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }


class AuthTokenBotForm(forms.Form):
    """
    Форма токена

    @param: token: telegram токен для телеграмм бота
    @type: token: basestring
    """

    token = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'placeholder': 'Ваш токен для авторизации в телеграмм боте'}
        ),
        label='Ваш токен:'
    )
