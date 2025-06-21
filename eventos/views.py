from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from usuarios.models import Fornecedor, Organizador


@login_required(login_url='login')
def index(request):
    #Verifica se o usuário é fornecedor ou organizador
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        is_fornecedor = True
    except Fornecedor.DoesNotExist:
        is_fornecedor = False
    
    try:
        organizador = Organizador.objects.get(user=request.user)
        is_organizador = True
    except Organizador.DoesNotExist:
        is_organizador = False
    
    return render(request, 'pages/index.html', {
        'is_fornecedor': is_fornecedor,
        'is_organizador': is_organizador
    })

