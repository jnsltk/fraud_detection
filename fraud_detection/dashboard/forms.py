from django import forms

class NewModelForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()