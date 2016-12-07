from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db import Error
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import Argon2PasswordHasher, make_password, check_password

from ssh_search.forms import ConnectGithubForm, SearchGithubUserForm, LoginFormInput, RegisterFormInput
from ssh_search.models import SiteUser, SocialLogin

import requests, json, uuid

# All VIEWS and CONTROLLERS to be written below this line
###################################################################################################
# HELPER FUNCTIONS

def render_blank_forms():
    connect_form = ConnectGithubForm(auto_id=False)
    input_form = SearchGithubUserForm(auto_id=False)
    return connect_form, input_form

def create_session(request, name):
    session_id = uuid.uuid4().hex
    request.session['session_user'] = name.title()
    request.session['sid'] = session_id

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

    context = {}
    if request.session.__contains__('context'):
        context = request.session.get('context')
        request.session.__delitem__('context')

    if not context:
        context = {
            'ssh_keys': 'No SSH key defined for the user',
        }

    context.update(render_page='home', name=request.session['session_user'],
        gh_connect_form=gh_connect_form, gh_input_form=gh_input_form)

    return render(request, 'ssh_search/base.html', context=context)

###################################################################################################
# FORM ACTIONS

@csrf_protect
def login(request):
    if request.method == 'POST':
        login_form = LoginFormInput(data=request.POST)

        if not login_form.is_valid():
            return redirect('index')

        user_name = login_form.cleaned_data.get('user_name')
        password = login_form.cleaned_data.get('password')

        try:
            user = SiteUser.objects.get(email__exact=user_name)

        except ObjectDoesNotExist:
            print('No User') # Do better redirection for the user


        if not check_password(password, user.password):
            return redirect('index')

        create_session(request, user.first_name)
        return redirect('home')

@csrf_protect
def register(request):
    if request.method == 'POST':
        register_form = RegisterFormInput(data=request.POST)

        if not register_form.is_valid():
            # Redirect with Unknown Error
            return redirect('index')

        full_name = register_form.cleaned_data.get('full_name')
        user_name = register_form.cleaned_data.get('user_name')
        password = register_form.cleaned_data.get('password')
        repeat_password = register_form.cleaned_data.get('repeat_password')

        # Check whether user_name is available to be taken or not
        try:
            user = SiteUser.objects.get(email__exact=user_name)

        except ObjectDoesNotExist:
            user = SiteUser(email=user_name)

        # Check whether user has properly entered the password
        if password != repeat_password:
            # Inform user that password entered doesn't match so backing off to index
            return redirect('index')

        user.password = make_password(password, hasher=Argon2PasswordHasher())

        # Split to obtain first and last name of the user
        name = full_name.split()
        if(len(name) == 1):
            user.first_name = name[0]

        else:
            user.first_name = name[0]
            user.last_name = ' '.join(name[1:])

        # Finally generate a Session ID
        session_id = uuid.uuid4().hex
        user.session_id = session_id

        try:
            user.save()
            create_session(request, name[0])

        except Error:
            print('Data not inserted')

            # Inform user there was some problem creating the user report to administrator
            return redirect('index')

        return redirect('home')

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
