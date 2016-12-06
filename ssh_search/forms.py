from django import forms


class ConnectGithubForm(forms.Form):
    user_name = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


class SearchGithubUserForm(forms.Form):
    gh_user = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


class LoginFormInput(forms.Form):
    user_name = forms.EmailField(max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control text-box'}))

    password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))


class RegisterFormInput(forms.Form):
    full_name = forms.CharField(max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control text-box'}))

    user_name = forms.EmailField(max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control text-box'}))

    password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))

    repeat_password = forms.CharField(max_length=254,
        widget=forms.PasswordInput(attrs={'class': 'form-control text-box'}))
