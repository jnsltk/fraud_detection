'''
    Made by: Omid Khodaparast
    Made by: Shiyao Xin
    Made by: Yingchao Ji
'''

import io
import json
import os
import subprocess
import sys
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from core.predictor_singleton import PredictorSingleton
from .forms import RegisterForm, LoginForm, ChangePasswordForm, MyProfileForm
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
    # ---------------------- Handle POST request to collect ---------------------- #
    if request.method == "POST":
        # Get form data
        merchant_category = request.POST.get('merchant_category')
        country = request.POST.get('country')
        currency = request.POST.get('currency')

        # Adjust 'currency' if it is 'Unknown' for model compatibility and validation purposes
        ori_currency = currency
        if currency == 'Unknown':
            ori_currency = 'unknown' # Change the string for the model
            currency = 'OTH' # Change the string for validation purpose

        try:
            amount = float(request.POST.get('amount', 0))  # Convert amount to float
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid amount. Please enter a valid number."
            }, status=400)
        transaction_hour = request.POST.get('transaction_hour')
        card_type = request.POST.get('card_type')
        device = request.POST.get('device')
        channel = request.POST.get('channel')
        # Transform boolean fields for validation compatibility
        card_present = bool(int(request.POST.get('card_present')))
        distance_from_home = bool(int(request.POST.get('distance_from_home')))
        weekend_transaction = bool(int(request.POST.get('weekend_transaction')))

        # Build the data into a dictionary
        input_data = {
            'merchant_category': merchant_category,
            'country': country,
            'currency': currency,
            'amount': amount,
            'transaction_hour': transaction_hour,
            'weekend_transaction': weekend_transaction,
            'card_type': card_type,
            'card_present': card_present,
            'device': device,
            'channel': channel,
            'distance_from_home': distance_from_home,
        }

        # ------------------------------ Data validation ----------------------------- #
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
        anaconda_python = sys.executable  # Dynamic, works on Windows, Linux, and macOS
        
        try:
            print("Start data validation......")

            # Run the validation script
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
                return JsonResponse({
                    "status": "error",
                    "message": "Validation script returned invalid or empty output."
                }, status=400)
            
            # Check the validation result
            if result.returncode != 0:
                # Extract the invalid fields from the failures
                failed_fields = list(set(failure['column'] for failure in output.get("failures", []) if failure.get('column')))
                failed_fields_message = ', '.join(failed_fields)

                failure_details = "\n".join([
                    f"\t- Expectation: {failure['expectation']} on column '{failure['column']}', "
                    f"Unexpected Count: {failure['unexpected_count']}, "
                    f"Unexpected Percent: {failure['unexpected_percent']}%, "
                    f"Sample Unexpected: {failure['partial_unexpected_list']}"
                    for failure in output.get("failures", [])
                ])
                print(f"\033[1;91mData validation failed! Failure details as below:\033[0m")
                print(f"\033[1;91m{failure_details}\033[0m")

                if request.headers.get('Accept') == 'application/json': 
                    return JsonResponse({
                        "status": "error",
                        "message": output.get("message", "Validation failed."),
                        "failures": output.get('failures', []),
                    }, status=400)
                else:
                    return render(request, 'detection/detection_page.html', {
                        "error_message": f"Your input for the following fields is not valid: {failed_fields_message}.<br>Please refill the form with valid input.",
                        "input_data": input_data
                    })
            else:            
                print(f"\033[1;92mValidation succeeded!\033[0m")
        except Exception as e:
            print(f"Error during validation: {e}")
            # Return to the page with a clear error message
            return render(request, 'detection/detection_page.html', {
                "error_message": f"An error occurred during validation.<br>Please try again.",
                "input_data": input_data,
            })

        # ------------------------- Get the model predictions ------------------------ #
        try:
            predictor = PredictorSingleton.get_instance().get_predictor()

            # Convert the values to the values required by the model after DataFrame creation
            df['amount'] = df['amount'].astype(int)
            df['card_present'] = df['card_present'].astype(int)
            df['distance_from_home'] = df['distance_from_home'].astype(int)
            df['weekend_transaction'] = df['weekend_transaction'].astype(int)
            df['transaction_hour'] = pd.to_datetime(df['transaction_hour'], errors='coerce').dt.hour
            df['currency'] = ori_currency

            input_data = df.iloc[0].to_dict() # Extract the first row of the df as a dictionary
            prediction = predictor.predict(input_data) # Pass the input data dictionary to the prediction model (predictor)

            print("Prediction:", prediction) 
            # Convert probability to a percentage and round to 2 decimal places
            prediction.probability = round(prediction.probability * 100, 2)

            # Determine risk level based on the probability and is_fraud value
            if prediction.is_fraud:
                if prediction.probability > 0.9:  # High risk if probability > 90%
                    detection_result = "high_risk"
                elif prediction.probability > 0.6:  # Medium risk if probability > 60%
                    detection_result = "medium_risk"
                else:  # If is_fraud is True but probability is low
                    detection_result = "low_risk"
            else:
                detection_result = "safe"  # If is_fraud is False, it’s secure

            # Pass prediction and detection result to the template
            context = {
                "status": "success",
                "prediction": prediction,  # Pass the whole prediction object to the template
                "detection_result": detection_result  # Pass the risk level for the icon logic
            }
            return render(request, 'detection/detection_result.html', context)

        except Exception as e:
            print(f"Error during prediction: {e}")
            # Return to the page with a clear error message
            return render(request, 'detection/detection_page.html', {
                "error_message": f"An error occurred during prediction.<br>Please try again.",
                "input_data": input_data,
            })

    return render(request, 'detection/detection_result.html')

