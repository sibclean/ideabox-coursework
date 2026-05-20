from django import forms
from .models import Idea, Category, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'categories', 'description', 'required_people_tags', 'contact_info', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Например: Онлайн-платформа для обучения'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'id': 'categories-select', 
                'style': 'width: 100%' 
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите суть идеи, цели, задачи...'
            }),
            'required_people_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Программист, Дизайнер, Маркетолог'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ссылка на соцсеть, email, Telegram...'
            }),
        }
        
        labels = {
            'required_people_tags': 'Кто нужен в команду',
            'contact_info': 'Ваши контакты',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['title'].widget.attrs['readonly'] = True
            self.fields['title'].widget.attrs['class'] += ' bg-light text-muted'
            self.fields['title'].help_text = "Название идеи нельзя изменить после создания."
            self.fields['title'].required = False

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 3:
            raise ValidationError("Название слишком короткое!")
        return title


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # Добавили first_name и last_name
        fields = ['first_name', 'last_name', 'university', 'course_year', 'avatar']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'university': 'Университет',
            'course_year': 'Курс',
            'avatar': 'Аватарка',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
            'course_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '6'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email адрес",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )
    
    agreement = forms.BooleanField(
        required=True,
        label="Я согласен с обработкой персональных данных",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email

