from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Card, Deck


class BootstrapAuthenticationForm(AuthenticationForm):
    """Форма входа со стилями Bootstrap 5."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegisterForm(UserCreationForm):
    """Форма регистрации пользователя со стилями Bootstrap 5."""

    email = forms.EmailField(
        label='Электронная почта (необязательно)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class DeckForm(forms.ModelForm):
    """Форма создания и редактирования языковой колоды."""

    class Meta:
        model = Deck
        fields = ('title', 'source_language', 'target_language')
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например: Английский: A1 Базовый',
                }
            ),
            'source_language': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Английский',
                }
            ),
            'target_language': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Русский',
                }
            ),
        }


class CardForm(forms.ModelForm):
    """Форма добавления и редактирования карточки."""

    class Meta:
        model = Card
        fields = ('front_text', 'back_text', 'example')
        widgets = {
            'front_text': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Слово или фраза (лицевая сторона)',
                }
            ),
            'back_text': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Перевод или толкование (оборот)',
                }
            ),
            'example': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Контекстный пример употребления (необязательно)',
                }
            ),
        }

