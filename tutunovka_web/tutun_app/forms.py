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

    class Meta:
        """
        Метамодель

        @param: model: модель точки маршрута
        @type: model: :class:'PrivateDot'

        @param: fields: поля точки маршрута
        @type: fields: list

        @param: widgets: словарь полей ввода для точки маршрута
        @type: widgets: dict
        """

        model = PrivateDot
        fields = ['name', 'date', 'information', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'information': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """
        Обработка данных

        @param: cleaned_data: словарь данных
        @type: cleaned_data: dict

        @return: словрь обработанных данных
        @rtype: dict
        """

        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        route_start_date = cleaned_data.get('route_start_date')
        route_end_date = cleaned_data.get('route_end_date')

        if date and route_start_date and route_end_date:
            if date < route_start_date or date > route_end_date:
                messages.error(self.request, 'Дата точки должна быть в пределах дат маршрута.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """

        route_start_date = kwargs.pop('route_start_date', None)
        route_end_date = kwargs.pop('route_end_date', None)
        super(PrivateDotForm, self).__init__(*args, **kwargs)
        self.route_start_date = route_start_date
        self.route_end_date = route_end_date
        self.fields['information'].required = True
        self.fields['note'].required = False
        self.fields['date'].required = True


class PrivateRouteForm(forms.ModelForm):
    """
    Форма приватного маршрута

    @param: tags: теги маршрута
    @type: tags: list
    """

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False, label='Tags'
    )

    def check(self):
        """
        Проверка дат начала и окончания маршрута

        @param: data_checked: словарь данных
        @type: tags: dict

        @param: data_checked: словарь данных
        @type: tags: dict

        @param: data_checked: словарь данных
        @type: tags: dict
        """

        data_checked = super().clean()
        date_in = data_checked.get('date_in')
        date_out = data_checked.get('date_out')

        if date_in >= date_out:
            messages.error(self.request, "Дата возвращения должна быть позже даты прибытия.")

        return data_checked

    class Meta:
        """
        Метамодель

        @param: model: модель приватного маршрута
        @type: model: :class:'PrivateRoute'

        @param: fields: поля приватного маршрута
        @type: fields: list

        @param: widgets: словарь полей ввода для приватного маршрута
        @type: widgets: dict
        """

        model = PrivateRoute
        fields = ['Name', 'comment', 'date_in', 'date_out', 'baggage', 'rate', 'tags']
        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'}),
            'date_in': forms.DateInput(attrs={'class': 'form-control',
                                              'type': 'date'}),
            'date_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'baggage': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control',
                                             'type': 'number', 'min': '-1', 'max': '10'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """

        super(PrivateRouteForm, self).__init__(*args, **kwargs)
        self.fields['baggage'].required = False
        self.fields['comment'].required = False


class NoteForm(forms.ModelForm):
    """
    Форма заметок

    @param: text: текст заметок
    @type: text: basestring
    """

    text = forms.CharField(label='Заметка')

    class Meta:
        """
        Метамодель

        @param: model: модель заметок
        @type: model: :class:'Note'

        @param: fields: поля заметок
        @type: fields: list

        @param: widgets: словарь полей ввода для заметок
        @type: widgets: dict
        """

        model = Note
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'done': forms.CheckboxInput(attrs={'class': 'form-check-input'})
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
