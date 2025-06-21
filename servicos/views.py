from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Servico, Item, ImagemServico
from usuarios.models import Fornecedor, Organizador
import json
import unicodedata

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
def todos_servicos(request):
    #Lista todos os serviços disponíveis para organizadores
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para organizadores.')
        return redirect('index')
    
    #Busca todos os serviços ativos
    servicos = Servico.objects.filter(ativo=True).select_related('fornecedor__user').order_by('-data_criacao')
    
    #Filtro por categoria
    categoria = request.GET.get('categoria', 'todas')
    if categoria != 'todas':
        servicos = servicos.filter(fornecedor__categoria=categoria)
    
    #Filtro por tags
    tag_busca = request.GET.get('tag', '').strip()
    if tag_busca:
        #Padroniza a tag de busca
        tag_busca_normalizada = unicodedata.normalize('NFD', tag_busca.lower()).encode('ASCII', 'ignore').decode('ASCII')
        
        #Busca serviços com a tag inserida
        servicos_filtrados = []
        for servico in servicos:
            tags_servico = servico.get_tags_list()
            for tag in tags_servico:
                tag_normalizada = unicodedata.normalize('NFD', tag.lower()).encode('ASCII', 'ignore').decode('ASCII')
                if tag_busca_normalizada in tag_normalizada or tag_normalizada in tag_busca_normalizada:
                    servicos_filtrados.append(servico)
                    break
        servicos = servicos_filtrados
    
    #Obter categorias disponíveis para o filtro
    categorias_disponiveis = Fornecedor.CATEGORIA_CHOICES
    
    return render(request, 'pages/todos_servicos.html', {
        'servicos': servicos,
        'organizador': organizador,
        'categorias_disponiveis': categorias_disponiveis,
        'categoria_atual': categoria,
        'tag_atual': tag_busca
    })

@login_required
def visualizar_servico(request, servico_id):
    #Permite que organizadores visualizem detalhes de um serviço
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verifica se o usuário é organizador
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para organizadores.')
        return redirect('index')
    
    #Verifica se o serviço está ativo
    if not servico.ativo:
        messages.error(request, 'Este serviço não está disponível.')
        return redirect('todos_servicos')
    
    return render(request, 'pages/visualizar_servico.html', {
        'servico': servico,
        'organizador': organizador
    })

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
        tags_json = request.POST.get('tags', '[]')
        
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return render(request, 'pages/cadastrar_servico.html', {
                'fornecedor': fornecedor,
                'nome': nome,
                'descricao': descricao
            })
        
        try:
            tags = json.loads(tags_json) if tags_json else []
        except:
            tags = []
        
        servico = Servico.objects.create(
            fornecedor=fornecedor,
            nome=nome,
            descricao=descricao,
            tags=tags
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
def adicionar_tag(request, servico_id):
    #Adiciona uma tag ao serviço
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            return JsonResponse({'erro': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        return JsonResponse({'erro': 'Acesso restrito para fornecedores'}, status=403)
    
    if request.method == 'POST':
        tag = request.POST.get('tag', '').strip()
        
        if not tag:
            return JsonResponse({'erro': 'Tag não pode estar vazia'}, status=400)
        
        #Verificar se a tag já existe
        tags = servico.get_tags_list()
        if tag in tags:
            return JsonResponse({'erro': 'Esta tag já existe'}, status=400)
        
        servico.add_tag(tag)
        
        return JsonResponse({
            'mensagem': 'Tag adicionada com sucesso',
            'tags': servico.get_tags_list()
        })
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def remover_tag(request, servico_id):
    #Remove uma tag do serviço
    servico = get_object_or_404(Servico, id=servico_id)
    
    #Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if servico.fornecedor != fornecedor:
            return JsonResponse({'erro': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        return JsonResponse({'erro': 'Acesso restrito para fornecedores'}, status=403)
    
    if request.method == 'POST':
        tag = request.POST.get('tag', '').strip()
        
        if not tag:
            return JsonResponse({'erro': 'Tag não pode estar vazia'}, status=400)
        
        servico.remove_tag(tag)
        
        return JsonResponse({
            'mensagem': 'Tag removida com sucesso',
            'tags': servico.get_tags_list()
        })
    
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
        tags_json = request.POST.get('tags', '[]')
        ativo = request.POST.get('ativo') == 'on'
        
        if not nome or not descricao:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return render(request, 'pages/editar_servico.html', {
                'servico': servico,
                'fornecedor': fornecedor
            })
        
        try:
            tags = json.loads(tags_json) if tags_json else []
        except:
            tags = []
        
        servico.nome = nome
        servico.descricao = descricao
        servico.tags = tags
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
