from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=40,
        min_length=4,
        required=True,
        widget=forms.TextInput()
    )
    email = forms.EmailField(
        max_length=40,
        min_length=4,
        required=True,
        widget=forms.EmailInput()
    )
    password = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )
    password_confirmation = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords do not match.")
        username = cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return cleaned_data
