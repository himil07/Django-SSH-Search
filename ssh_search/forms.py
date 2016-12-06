from django import forms


class ConnectGithubForm(forms.Form):
    user_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
