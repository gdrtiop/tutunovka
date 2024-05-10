from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from taggit.models import Tag

from django import forms
from .models import PrivateRoute, PrivateDot, Note, Complaint


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


class ProfileForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=100,
        min_length=4,
    )
    email = forms.EmailField(
        label='Email',
        max_length=100,
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        min_length=2,
        required=False,
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        min_length=2,
        required=False,
    )
    tg_username = forms.CharField(
        label='TG логин',
        max_length=100,
        min_length=1,
        required=False,
    )


class PrivateDotForm(forms.ModelForm):
    class Meta:
        model = PrivateDot
        fields = ['name', 'api_vision', 'date', 'note', 'information']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'api_vision': forms.HiddenInput({'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'information': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PrivateDotForm, self).__init__(*args, **kwargs)
        self.fields['information'].required = False
        self.fields['note'].required = False
        self.fields['date'].required = False


class PrivateRouteForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False, label='Tags')

    def clean(self):
        cleaned_data = super().clean()
        date_in = cleaned_data.get('date_in')
        date_out = cleaned_data.get('date_out')
        if date_in and date_out and date_in > date_out:
            raise forms.ValidationError('Дата возвращения должна быть позже даты прибытия.')
        return cleaned_data

    class Meta:
        model = PrivateRoute
        fields = ['Name', 'comment', 'date_in', 'date_out', 'baggage', 'rate', 'tags']
        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'}),
            'date_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'baggage': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '-1', 'max': '10'}),
        }

    def __init__(self, *args, **kwargs):
        super(PrivateRouteForm, self).__init__(*args, **kwargs)
        self.fields['baggage'].required = False
        self.fields['comment'].required = False



class NoteForm(forms.ModelForm):
    text = forms.CharField(label='Заметка')

    class Meta:
        model = Note
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'done': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class TagSelectMultiple(forms.SelectMultiple):
    def render_options(self, *args, **kwargs):
        """Override render_options to include selected attribute for selected tags."""
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Tag.objects.all()
        self.widget = TagSelectMultiple()


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AnswerComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['answer']
        widgets = {
            'answer': forms.TextInput(attrs={'class': 'form-control'}),
        }
