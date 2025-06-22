from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Organizador, Fornecedor
from .utils import atualizar_coordenadas_usuario
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
        
        #Tentar geocodificar o CEP
        try:
            atualizar_coordenadas_usuario(organizador)
        except Exception as e:
            #Se falhar, não impede o cadastro
            print(f"Erro ao geocodificar CEP: {e}")
        
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
        
        #Tentar geocodificar o CEP
        try:
            atualizar_coordenadas_usuario(fornecedor)
        except Exception as e:
            #Se falhar, não impede o cadastro
            print(f"Erro ao geocodificar CEP: {e}")

        return render(request, 'pages/login.html')

@login_required
def configurar_raio_cobertura(request):
    #Permite que fornecedores configurem seu raio de cobertura
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')
    
    if request.method == 'GET':
        return render(request, 'pages/configurar_raio_cobertura.html', {
            'fornecedor': fornecedor
        })
    else:
        tipo_raio = request.POST.get('tipo_raio')
        
        #Definir o valor baseado no tipo selecionado
        if tipo_raio == 'ilimitado':
            fornecedor.raio_cobertura = 0
            fornecedor.save()
            messages.success(request, 'Raio de cobertura configurado como ilimitado.')
        else:
            raio_cobertura = request.POST.get('raio_cobertura')
            try:
                raio_cobertura = int(raio_cobertura)
                if raio_cobertura < 1 or raio_cobertura > 1000:
                    raise ValueError("Raio deve estar entre 1 e 1000 km")
                
                fornecedor.raio_cobertura = raio_cobertura
                fornecedor.save()
                messages.success(request, f'Raio de cobertura configurado para {raio_cobertura} km.')
                
            except (ValueError, TypeError):
                messages.error(request, 'Raio de cobertura deve ser um número válido entre 1 e 1000 km.')
                return render(request, 'pages/configurar_raio_cobertura.html', {
                    'fornecedor': fornecedor
                })
        
        return redirect('index')

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