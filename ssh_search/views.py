from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from ssh_search.forms import ConnectGithubForm, SearchGithubUserForm, LoginFormInput, RegisterFormInput

import requests, json

# All VIEWS and CONTROLLERS to be written below this line
###################################################################################################
# HELPER FUNCTIONS

def render_blank_forms():
    connect_form = ConnectGithubForm(auto_id=False)
    input_form = SearchGithubUserForm(auto_id=False)
    return connect_form, input_form

###################################################################################################
# BASE TEMPLATE RENDERS

def index(request):
    login_form = LoginFormInput(auto_id=False)
    register_form = RegisterFormInput(auto_id=False)

    return render(request, 'ssh_search/base.html', context={
        'render_page': 'index',
        'login_form': login_form,
        'register_form': register_form
    })

def home(request):
    gh_connect_form, gh_input_form = render_blank_forms()

    if request.session.__contains__('context'):
        context = request.session.get('context')
        request.session.__delitem__('context')

    else:
        context = {
            'ssh_key': 'No SSH key defined for the user',
        }

    context.update(render_page='home', name='Shreyas', gh_connect_form=gh_connect_form,
        gh_input_form=gh_input_form)

    return render(request, 'ssh_search/base.html', context=context)

###################################################################################################
# FORM ACTIONS

def connect(request):
    if request.method == 'GET':
        gh_connect_form = ConnectGithubForm(data=request.GET)

        if gh_connect_form.is_valid():
            # Store this in DB for further reference
            user_name = form.cleaned_data.get('user_name', '')

            # redirect to GitHub for authorizations
            params = 'client_id={0}&client_secret={1}'.format(settings.CLIENT_ID,
                settings.CLIENT_SECRET)

            return redirect('https://github.com/login/oauth/authorize?' + params, permanent=True)

        else:
            print(gh_connect_form.errors)

    return render(request, 'ssh_search/base.html', context={'render_page': 'home', 'name': 'Shreyas',
        'ssh_key': 'No SSH key defined for the user', 'gh_connect_form': gh_connect_form})

def redirect_oauth(request):
    if request.method == 'GET' and request.GET.__contains__('code'):
        auth_code = request.GET.get('code', None)

        if not auth_code:
            # More verbose logging with alerts for error messages
            return redirect('home') # Failure in obtaining the code from Github. Retry Later

        # Redirect to Github for access token
        headers = {'Accept': 'application/json'}
        params = {'client_id': settings.CLIENT_ID, 'client_secret': settings.CLIENT_SECRET,
            'code': auth_code}

        response = requests.post('https://github.com/login/oauth/access_token', headers=headers,
            params=params)

        if response.status_code != 200:
            # More verbose logging with alerts for error messages
            return redirect('home') # Failure Token already present or some other error

        auth_token = response.json().get('access_token', '')
        # This auth token needs to stored with social login table against user id
        print (auth_token) # Temporary needs to be removed

        # More verbose logging with alerts for error messages
        return redirect('home') # Success in Obtaining an Auth Token

    else:
        # More verbose logging with alerts for error messages
        return redirect('home') # Failure with the request

def retrieve_ssh_key(request):
    gh_connect_form, gh_input_form = render_blank_forms()

    # This will be retrieved from the database using ORM
    access_token = 'f13990846e2c071fe5f89e20c2efe17dba37a16c'

    if request.method == 'GET':
        gh_input_form = SearchGithubUserForm(data=request.GET)

        if gh_input_form.is_valid():
            gh_user = gh_input_form.cleaned_data.get('gh_user', '')

            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'access_token': access_token
            }

            url = 'https://api.github.com/users/{0}/keys'.format(gh_user)

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return redirect('home')

            # Retrieve all the keys for a GitHub user
            ssh_keys = []
            if (not response.json()):
                request.session['context'] = {'ssh_keys': 'No SSH key present for the user on GitHub'}
                return redirect('home')

            for element in response.json():
                ssh_keys.append(str(element.get('key') + '\n-------\n'))

            request.session['context'] = {'ssh_keys': ssh_keys}
            return redirect('home')

        else:
            print(gh_input_form.errors)

    # Need Better Redirect
    return HttpResponse(content=ssh_keys)
