from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from core.models import Usuario


def landing_view(request):
    return render(request, 'landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            destination = request.GET.get('next')
            if not destination:
                destination = 'adminhub_view' if user.is_staff else 'home'
            return redirect(destination)

        messages.error(request, 'El usuario o la contraseña no son válidos.')

    return render(request, 'Auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        run = request.POST.get('run', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')

        if not username or not run or not email or not password:
            messages.error(request, 'Completa todos los campos obligatorios.')
        elif password != password_confirmation:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya está registrado.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Ese correo ya está registrado.')
        elif Usuario.objects.filter(run=run).exists():
            messages.error(request, 'Ese RUT ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Usuario.objects.create(auth_user=user, username=username, run=run, email=email)
            login(request, user)
            return redirect('home')

    return render(request, 'Auth/register.html')
