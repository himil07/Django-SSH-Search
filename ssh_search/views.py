from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from ssh_search.forms import ConnectGithubForm

import requests, json

# All VIEWS and CONTROLLERS to be written below this line
###################################################################################################

def index(request):
    return render(request, 'ssh_search/base.html', context={'render_page': 'index'})

def home(request):
    form = ConnectGithubForm(auto_id=False)
    return render(request, 'ssh_search/base.html', context={'render_page': 'home', 'name': 'Shreyas',
        'ssh_key': 'No SSH key defined for the user', 'form': form})

def connect(request):
    if request.method == 'GET':
        form = ConnectGithubForm(data=request.GET)

        if form.is_valid():
            # Store this in DB for further reference
            user_name = form.cleaned_data.get('user_name', '')

            # redirect to GitHub for authorizations
            params = 'client_id={0}&client_secret={1}'.format(settings.CLIENT_ID,
                settings.CLIENT_SECRET)

            return redirect('https://github.com/login/oauth/authorize?' + params, permanent=True)

        else:
            print(form.errors)

    return render(request, 'ssh_search/base.html', context={'render_page': 'home', 'name': 'Shreyas',
        'ssh_key': 'No SSH key defined for the user', 'form': form})

####################################################################################################
def redirect_oauth(request):
    if request.method == 'GET' and request.GET.__contains__('code'):
        auth_code = request.GET.get('code', None)

        if auth_code:
            # Redirect to Github for access token
            headers = {'Accept': 'application/json'}
            params = {'client_id': settings.CLIENT_ID, 'client_secret': settings.CLIENT_SECRET,
                'code': auth_code}

            response = requests.post('https://github.com/login/oauth/access_token', headers=headers,
                params=params)

            if response.status_code == 200:
                auth_token = response.json().get('access_token', '')
                # This auth token needs to stored with social login table against user id
                print (auth_token) # Temporary needs to be removed

                # More verbose logging with alerts for error messages
                return redirect('home') # Success in Obtaining an Auth Token
            else:
                # More verbose logging with alerts for error messages
                return redirect('home') # Failure Token already present or some other error

        else:
            # More verbose logging with alerts for error messages
            return redirect('home') # Failure in obtaining the code from Github. Retry Later

    else:
        # More verbose logging with alerts for error messages
        return redirect('home') # Failure with the request
