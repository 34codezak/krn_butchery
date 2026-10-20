from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hints = {
            'username': 'Choose a username',
            'email': 'you@example.com',
            'phone': '07XX XXX XXX',
            'password1': 'Create a password',
            'password2': 'Repeat the password',
        }
        for name, text in hints.items():
            self.fields[name].widget.attrs['placeholder'] = text
        self.fields['username'].widget.attrs['autofocus'] = True

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user


class CheckoutForm(forms.Form):
    phone = forms.CharField(max_length=20)
    delivery_address = forms.CharField(max_length=255)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)