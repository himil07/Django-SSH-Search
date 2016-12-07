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

def set_alert(request, alert_template_name):
    request.session['alert'] = alert_template_name

def delete_alert(request):
    request.session.pop('alert')

def render_blank_forms():
    connect_form = ConnectGithubForm(auto_id=False)
    input_form = SearchGithubUserForm(auto_id=False)
    return connect_form, input_form

def create_session(request, user_name, name):
    session_id = uuid.uuid4().hex
    request.session['session_user'] = user_name
    request.session['session_user_name'] = name.title()
    request.session['sid'] = session_id

###################################################################################################
# BASE TEMPLATE RENDERS

def index(request):
    login_form = LoginFormInput(auto_id=False)
    register_form = RegisterFormInput(auto_id=False)

    alert = request.session.get('alert', None)
    if alert:
        delete_alert(request)

    return render(request, 'ssh_search/base.html', context={
        'render_page': 'index',
        'login_form': login_form,
        'register_form': register_form,
        'alert': alert
    })

def home(request):
    gh_connect_form, gh_input_form = render_blank_forms()

    # Clean all the alerts raised on the Login/Register Form
    alert = ''
    if request.session.get('alert', None):
        alert = request.session.get('alert')
        delete_alert(request)

    context = {}
    if request.session.__contains__('context'):
        context = request.session.get('context')
        del request.session['context']

    if not context:
        context = {
            'ssh_keys': 'No SSH key defined for the user',
        }

    context.update(render_page='home', name=request.session['session_user_name'],
        gh_connect_form=gh_connect_form, gh_input_form=gh_input_form, alert=alert)

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
            set_alert(request, 'user_not_exist')
            return redirect('index')


        if not check_password(password, user.password):
            set_alert(request, 'usr_password_mismatch')
            return redirect('index')

        create_session(request, user.email, user.first_name)
        set_alert(request, 'user_logged_in')
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

        # User already exists in the database
        if user:
            set_alert(request, 'user_exists')
            return redirect('index')

        # Check whether user has properly entered the password
        if password != repeat_password:
            set_alert(request, 'password_mismatch')
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
            create_session(request, user_name)

        except Error:
            # Inform user there was some problem creating the user report to administrator
            set_alert(request, 'generic_error')
            return redirect('index')

        return redirect('home')

def connect(request):
    if request.method == 'GET':
        gh_connect_form = ConnectGithubForm(data=request.GET)

        if gh_connect_form.is_valid():
            # Store this in DB for further reference
            user_name = gh_connect_form.cleaned_data.get('user_name', '')

            # redirect to GitHub for authorizations
            params = 'client_id={0}&client_secret={1}'.format(settings.CLIENT_ID,
                settings.CLIENT_SECRET)

            return redirect('https://github.com/login/oauth/authorize?' + params, permanent=True)

        else:
            print(gh_connect_form.errors)
            return render(request, 'ssh_search/base.html', context={
                'render_page': 'home',
                'name': 'Shreyas',
                'ssh_key': 'No SSH key defined for the user',
                'gh_connect_form': gh_connect_form
            })

def redirect_oauth(request):
    if SocialLogin.objects.get(user_id=request.session['session_user']):
        set_alert(request, 'github_connection_exists')
        return redirect('home')

    if request.method == 'GET' and request.GET.__contains__('code'):
        auth_code = request.GET.get('code', None)

        # Failure in obtaining the code from Github. Retry Later
        if not auth_code:
            set_alert(request, 'err_connecting_github')
            return redirect('home')

        # Redirect to Github for access token
        headers = {'Accept': 'application/json'}
        params = {'client_id': settings.CLIENT_ID, 'client_secret': settings.CLIENT_SECRET,
            'code': auth_code}

        response = requests.post('https://github.com/login/oauth/access_token', headers=headers,
            params=params)

        # Failure Token already present or some other error
        if response.status_code != 200:
            set_alert(request, 'err_connecting_github')
            return redirect('home')

        auth_token = response.json().get('access_token', '')

        # This auth token needs to stored with social login table against user id
        social_login = SocialLogin(auth_token=auth_token)
        social_login.site_name = 'github'
        social_login.user_id = request.session.get('session_user', None)

        try:
            social_login.save()

        except Error:
            set_alert(request, 'err_connecting_github')
            print('Not able to insert token in Database')

        # Success in Obtaining an Auth Token
        set_alert(request, 'connected_github')
        return redirect('home')

    else:
        # Failure with the request
        set_alert(request, 'err_connecting_github')
        return redirect('home')

def retrieve_ssh_key(request):
    gh_connect_form, gh_input_form = render_blank_forms()

    # This will be retrieved from the database using ORM
    user_id = request.session.get('session_user', None)
    github_account = SocialLogin.objects.get(site_name='github', user_id=user_id)

    if request.method == 'GET':
        gh_input_form = SearchGithubUserForm(data=request.GET)

        if gh_input_form.is_valid():
            gh_user = gh_input_form.cleaned_data.get('gh_user', '')

            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'access_token': github_account.auth_token
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
    else:
        set_alert(request, 'generic_error')
