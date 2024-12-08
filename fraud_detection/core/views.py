from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .form import RegisterForm, LoginForm, ChangePasswordForm, MyProfileForm


@require_GET
def home_page(request):
    return render(request, 'home_page/index.html')

@require_GET
def get_register_form(request):
    form = RegisterForm()
    return render(request, 'registration/registration_form.html', {'form': form})

@require_POST
def post_register_form(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = User.objects.create_user(username, email, password)
        login(request, user)
        return redirect('core/index')
    return render(request, 'registration/registration_form.html', {'form': form})

@login_required
@require_http_methods(['GET', 'POST'])
def logout_view(request):
    logout(request)
    return redirect('core/index')

@require_GET
def login_view(request):
    form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@require_POST
def post_login_view(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect superusers to the Django admin page
            if user.is_superuser:
                return redirect('/admin/')
            # Redirect staff users to the dashboard
            elif user.is_staff:
                return redirect('dashboard/index')
            # Redirect regular users to the home page
            return redirect('core/index')
        else:
            # Return an error message for invalid credentials
            return render(request, 'registration/login.html', {
                'form': form,
                'error_message': 'Invalid username or password.'
            })
    return render(request, 'registration/login.html', {'form': form})

@login_required
@require_GET
def profile_view(request):
    form = MyProfileForm(
        user=request.user,
        initial={
            'username': request.user.username,
            'email': request.user.email,
        }
    )
    return render(request, 'my_profile/my_profile.html', {'form': form})

@login_required
@require_POST
@login_required
@require_POST
def update_profile_view(request):
    form = MyProfileForm(request.POST, user=request.user)
    if form.is_valid():
        new_username = form.cleaned_data["username"]
        new_email = form.cleaned_data["email"]
        
        # Update username and email
        request.user.username = new_username
        request.user.email = new_email

        login(request, request.user)
        
        # Save changes
        request.user.save()
        
        print(request.user)  # Optional: Debugging
        
        return render(request, 'my_profile/my_profile.html', {
            'form': form,
            'success_message': "Your profile has been updated successfully!"
        })
    return render(request, 'my_profile/my_profile.html', {'form': form})


@login_required
@require_GET
def get_change_password_view(request):
    form = ChangePasswordForm(user=request.user)  # Pass the user instance
    return render(request, 'my_profile/change_password.html', {'form': form})

@login_required
@require_POST
def post_change_password_view(request):
    form = ChangePasswordForm(request.POST, user=request.user)  # Pass the user instance
    if form.is_valid():
        new_password = form.cleaned_data["new_password"]
        
        # Update the user's password
        request.user.set_password(new_password)
        request.user.save()
        
        # Re-authenticate the user after password change
        login(request, request.user)
        
        return render(request, 'my_profile/change_password.html', {
            'form': form,
            'success_message': "Your password has been changed successfully!"
        })
    error_message = "The old password is incorrect."
    return render(request, 'my_profile/change_password.html', {'form': form, 'error_message': error_message})

@login_required
@require_GET
def detection_page_view(request):
    return render(request, 'detection/detection_page.html')

@login_required
@require_POST 
def detection_result(request):

    return render(request, 'detection/detection_result.html')