from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "px-4 py-2 md:ml-1 rounded-lg border-2 border-blue-800 text-lg text-black"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "px-4 md:ml-11 py-2 rounded-lg border-2 border-blue-800 text-lg text-black"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "px-4 py-2 rounded-lg border-2 border-blue-800 text-lg text-black"})
    )