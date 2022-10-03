from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Message, Comment


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['recipient']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Topic of the message. . .'}),
            'body': forms.Textarea(
                attrs={"placeholder": "Share what's happening around you . . ."}),
        }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'email', 'bio']
