from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=40,
        min_length=3,
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


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=40,
        min_length=3,
        required=True,
        widget=forms.TextInput()
    )
    password = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )


class MyProfileForm(forms.Form):
    username = forms.CharField(
        max_length=40,
        min_length=3,
        required=True,
        widget=forms.TextInput()
    )
    email = forms.EmailField(
        max_length=40,
        min_length=4,
        required=True,
        widget=forms.EmailInput()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract the user instance
        super().__init__(*args, **kwargs)

    def clean_email(self):        
        email = self.cleaned_data.get("email")
        # Ensure `self.user` is not None before accessing `pk`
        if self.user and User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            print("Email already exists.")
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if self.user and User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            print("Username already exists.")
            raise forms.ValidationError("Username already exists.")
        return username

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Old Password"})
    )
    new_password = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "New Password"})
    )
    confirm_new_password = forms.CharField(
        max_length=40,
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract the user instance
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        # Validate old password
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")

        # Validate new passwords match
        if new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data
