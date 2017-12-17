from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http.response import Http404, HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .forms import LoginForm, UserCreationForm
from .models import CustomUser


@require_http_methods(["GET", "POST"])
def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        form.data._mutable = True
        form.data['is_active'] = False
        if form.is_valid():
            form.save(request=request)
            return HttpResponse('Check your email')
    else:
        form = UserCreationForm()
    return render(request, 'common/registration.html', {'create_user': form})


@require_http_methods(["GET", "POST"])
def authentication_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['email'], password=request.POST['password'])
            if user:
                login(request, user)
                return redirect('posts:home_page')
            return HttpResponse('Your account is not active. Check your email')
    else:
        form = LoginForm()
    return render(request, 'common/login.html', {'auth_user': form})


def logout_view(request):
    logout(request)
    return redirect('common:authentication_user')


def complete_email(request, code=None):
    try:
        uidb64, token = code.split('-', 1)
        assert uidb64 is not None and token is not None
        uid = urlsafe_base64_decode(uidb64)
        user = CustomUser.objects.get(pk=uid)
    except (AssertionError, TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('posts:main_page')
    raise Http404()
