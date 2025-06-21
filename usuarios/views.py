from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Organizador, Fornecedor
import json
import requests

#-------------------------CADASTRO-------------------------

def escolha_cadastro(request):
    return render(request, 'pages/escolha_cadastro.html')

def buscar_cep(request):
    #Busca CEP através da API ViaCep
    if request.method == 'GET':
        cep = request.GET.get('cep', '').replace('-', '').replace('.', '')
        
        if len(cep) != 8:
            return JsonResponse({'erro': 'CEP deve ter 8 dígitos'}, status=400)
        
        try:
            url = f'https://viacep.com.br/ws/{cep}/json/'
            response = requests.get(url)
            data = response.json()
            
            if 'erro' in data:
                return JsonResponse({'erro': 'CEP não encontrado'}, status=404)
            
            return JsonResponse({
                'cep': data.get('cep', ''),
                'logradouro': data.get('logradouro', ''),
                'bairro': data.get('bairro', ''),
                'cidade': data.get('localidade', ''),
                'estado': data.get('uf', '')
            })
            
        except requests.RequestException:
            return JsonResponse({'erro': 'Erro ao consultar CEP'}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Erro ao processar resposta'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def cadastro_organizador(request):
    if request.method == "GET":
        return render(request, 'pages/cadastro_organizador.html')
    else:
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        cep = request.POST.get('cep')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        bairro = request.POST.get('bairro')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        telefone = request.POST.get('telefone')

        if User.objects.filter(username=username).exists():
            contexto = {'useralredyexist': 'Usuário já existe'}
            return render(request, 'pages/cadastro_organizador.html', contexto)
        
        user = User.objects.create_user(
            username=username, 
            first_name=firstname, 
            last_name=lastname, 
            email=email, 
            password=senha)
        user.save()

        organizador = Organizador.objects.create(
            user=user,
            cep=cep,
            estado=estado,
            cidade=cidade,
            bairro=bairro,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            telefone=telefone
        )
        organizador.save()
        return render(request, 'pages/login.html')

def cadastro_fornecedor(request):
    if request.method == "GET":
        return render(request, 'pages/cadastro_fornecedor.html')
    else:
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        cep = request.POST.get('cep')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        bairro = request.POST.get('bairro')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        telefone = request.POST.get('telefone')
        categoria = request.POST.get('categoria')

        if User.objects.filter(username=username).exists():
            contexto = {'useralredyexist': 'Usuário já existe'}
            return render(request, 'pages/cadastro_fornecedor.html', contexto)
        
        user = User.objects.create_user(
            username=username, 
            first_name=firstname, 
            last_name=lastname, 
            email=email, 
            password=senha)
        user.save()

        fornecedor = Fornecedor.objects.create(
            user=user,
            cep=cep,
            estado=estado,
            cidade=cidade,
            bairro=bairro,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            telefone=telefone,
            categoria=categoria
        )
        fornecedor.save()

        return render(request, 'pages/login.html')
    
#-------------------------LOGIN-------------------------

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

#-------------------------LOGOUT-------------------------
@login_required
def sair(request):
    logout(request)
    return render(request, 'pages/login.html')