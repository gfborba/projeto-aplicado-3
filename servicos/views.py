from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Servico, Item, ImagemServico
from usuarios.models import Fornecedor
import json

@login_required
def meus_servicos(request):
    #Lista todos os serviços do fornecedor logado
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        servicos = Servico.objects.filter(fornecedor=fornecedor).order_by('-data_criacao')
        return render(request, 'pages/meus_servicos.html', {
            'servicos': servicos,
            'fornecedor': fornecedor
        })
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')

@login_required
def cadastrar_servico(request):
    #Cadastra um novo serviço
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')
    
    if request.method == 'GET':
        return render(request, 'pages/cadastrar_servico.html', {
            'fornecedor': fornecedor
        })
    else:
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return render(request, 'pages/cadastrar_servico.html', {
                'fornecedor': fornecedor,
                'nome': nome,
                'descricao': descricao
            })
        
        servico = Servico.objects.create(
            fornecedor=fornecedor,
            nome=nome,
            descricao=descricao
        )
        
        #Imagens do serviço
        imagens = request.FILES.getlist('imagens')
        for imagem in imagens:
            ImagemServico.objects.create(
                servico=servico,
                imagem=imagem
            )
        
        messages.success(request, f'Serviço "{nome}" cadastrado com sucesso!')
        return redirect('detalhes_servico', servico_id=servico.id)

@login_required
def detalhes_servico(request, servico_id):
    #Mostra detalhes de um serviço específico
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verifica se o usuário é o fornecedor do serviço
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            messages.error(request, 'Você não tem permissão para acessar este serviço.')
            return redirect('meus_servicos')
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')
    
    return render(request, 'pages/detalhes_servico.html', {
        'servico': servico,
        'fornecedor': fornecedor
    })

@login_required
def adicionar_item(request, servico_id):
    #Adiciona um item ao serviço
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verifica permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            return JsonResponse({'erro': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        return JsonResponse({'erro': 'Acesso restrito para fornecedores'}, status=403)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        imagem = request.FILES.get('imagem')
        
        if not nome:
            return JsonResponse({'erro': 'Nome do item é obrigatório'}, status=400)
        
        item = Item.objects.create(
            servico=servico,
            nome=nome,
            descricao=descricao,
            imagem=imagem
        )
        
        return JsonResponse({
            'id': item.id,
            'nome': item.nome,
            'descricao': item.descricao,
            'tem_imagem': bool(item.imagem),
            'data_criacao': item.data_criacao.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def remover_item(request, servico_id, item_id):
    #Remove um item do serviço
    servico = get_object_or_404(Servico, id=servico_id)
    item = get_object_or_404(Item, id=item_id, servico=servico)
    
    #Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            return JsonResponse({'erro': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        return JsonResponse({'erro': 'Acesso restrito para fornecedores'}, status=403)
    
    if request.method == 'POST':
        item.delete()
        return JsonResponse({'mensagem': 'Item removido com sucesso'})
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def editar_servico(request, servico_id):
    #Edita um serviço existente
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verifica permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            messages.error(request, 'Você não tem permissão para editar este serviço.')
            return redirect('meus_servicos')
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')
    
    if request.method == 'GET':
        return render(request, 'pages/editar_servico.html', {
            'servico': servico,
            'fornecedor': fornecedor
        })
    else:
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        ativo = request.POST.get('ativo') == 'on'
        
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return render(request, 'pages/editar_servico.html', {
                'servico': servico,
                'fornecedor': fornecedor
            })
        
        servico.nome = nome
        servico.descricao = descricao
        servico.ativo = ativo
        servico.save()
        
        #Processa novas imagens do serviço
        imagens = request.FILES.getlist('imagens')
        for imagem in imagens:
            ImagemServico.objects.create(
                servico=servico,
                imagem=imagem
            )
        
        messages.success(request, f'Serviço "{nome}" atualizado com sucesso!')
        return redirect('detalhes_servico', servico_id=servico.id)
