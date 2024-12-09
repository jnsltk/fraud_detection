import io
import json
import os
import subprocess
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .form import RegisterForm, LoginForm, ChangePasswordForm, MyProfileForm
import pandas as pd

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
    if request.method == "POST":
        # Get form data
        merchant_category = request.POST.get('merchant_category')
        merchant_type = request.POST.get('merchant_type')
        country = request.POST.get('country')
        currency = request.POST.get('currency')
        # amount = request.POST.get('amount')
        # Cast amount to float to ensure it passes validation
        try:
            amount = float(request.POST.get('amount', 0))  # Convert amount to float
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid amount. Please enter a valid number."
            }, status=400)
        city_size = request.POST.get('city_size')
        distance_from_home = request.POST.get('distance_from_home')
        transaction_hour = request.POST.get('transaction_hour')
        weekend_transaction = request.POST.get('weekend_transaction')
        high_risk_merchant = request.POST.get('high_risk_merchant')
        card_type = request.POST.get('card_type')

        # Build the data into a dictionary
        input_data = {
            'merchant_category': merchant_category,
            'merchant_type': merchant_type,
            'country': country,
            'currency': currency,
            'amount': amount,
            'city_size': city_size,
            'distance_from_home': distance_from_home,
            'transaction_hour': transaction_hour,
            'weekend_transaction': weekend_transaction,
            'high_risk_merchant': high_risk_merchant,
            'card_type': card_type
        }


        # Data validation

        # Convert input data into a DataFrame
        df = pd.DataFrame([input_data])
        # Create an in-memory CSV file
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Validate the file using the Great Expectations script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../"))
        validation_script = os.path.join(
            project_root, "gx", "scripts", "validate_data.py"
        )
        anaconda_python = "/opt/anaconda3/envs/prj/bin/python"
        try:
            print("Start data validation......")

            result = subprocess.run(
                [anaconda_python, validation_script],
                input=csv_data,
                capture_output=True,
                text=True,
            )
            try:
                # Parse the result
                output = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Raw output: {repr(result.stdout)}")
                return {"status": "error", "message": "Validation script returned invalid or empty output."}
            # Check the validation result
            if result.returncode != 0:
                # Extract the invalid fields from the failures
                failed_fields = list(set(failure['column'] for failure in output.get("failures", []) if failure.get('column')))
                # Join the list of failed field names into a single string, separated by commas
                failed_fields_message = ', '.join(failed_fields)

                failure_details = "\n".join([
                    f"\t- Expectation: {failure['expectation']} on column '{failure['column']}', "
                    f"Unexpected Count: {failure['unexpected_count']}, "
                    f"Unexpected Percent: {failure['unexpected_percent']}%, "
                    f"Sample Unexpected: {failure['partial_unexpected_list']}"
                    for failure in output.get("failures", [])
                ])
                print(f"\033[1;91mData validation failed! Failure details as below:\033[0m") # Log the failure result in red
                print(f"\033[1;91m{failure_details}\033[0m") # Log the failure details in red
                
                # Render the detection_page.html with an error message
                return render(request, 'detection/detection_page.html', {
                    "error_message": f"Your input for the following fields is not valid: {failed_fields_message}.<br>Please refill the form with valid input.",
                })

            else:            
                print(f"\033[1;92mValidation succeeded!\033[0m") # Log the successful result in green
        except Exception as e:
            print(f"Error during validation: {e}")
            return JsonResponse({
                "status": "error", 
                "message": f"An error occurred during validation: {str(e)}"
            }, status=500)  # Return 500 status for server error


        # Get the model predictions



        
    return render(request, 'detection/detection_result.html')
