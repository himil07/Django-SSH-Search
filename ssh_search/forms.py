# Django Imports
from django import forms

# Form: Connect to GitHub
class ConnectGithubForm(forms.Form):
    user_name = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


# Form: Search field for GitHub SSH key search
class SearchGithubUserForm(forms.Form):
    gh_user = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


# Form: Login Form
class LoginFormInput(forms.Form):
    user_name = forms.EmailField(max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control text-box'}))

    password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))


# Form: Register new user
class RegisterFormInput(forms.Form):
    full_name = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control text-box'}))

    user_name = forms.EmailField(max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control text-box'}))

    password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))

    repeat_password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))
