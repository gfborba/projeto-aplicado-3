from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required

def cadastro(request):
    if request.method == "GET":
        return render(request, 'pages/cadastro.html')
    else:
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if User.objects.filter(username=username).exists():
            contexto = {'useralredyexist': 'Usuário já existe'}
            return render (request, 'pages/cadastro.html', contexto)
        
        user = User.objects.create_user(
            username=username, 
            first_name = firstname, 
            last_name = lastname, 
            email=email, 
            password = senha)
        user.save()

        print('Cadastro realizado')
        return render (request, 'pages/login.html')

def login(request):

    if request.method == "GET":
        return render(request, 'pages/login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        verificar_usuario = authenticate(username=username, password=senha)

        if (verificar_usuario != None):
            login_django(request, verificar_usuario)

            return redirect ('index')
        else:
            contexto = {'error': 'Usuário ou senha incorretos'}
            return render (request, 'pages/login.html', contexto)


@login_required
def sair(request):
    logout(request)
    return render(request, 'pages/login.html')