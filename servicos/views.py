from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from .models import Servico, Item, ImagemServico, SolicitacaoOrcamento, HistoricoOrcamento
from usuarios.models import Fornecedor, Organizador
from usuarios.utils import verificar_cobertura_fornecedor
import json
import unicodedata
from django.utils.translation import gettext as _

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
    
    #PRIMEIRO FILTRO OBRIGATÓRIO: Verificar se o fornecedor atende o organizador baseado no raio de cobertura
    servicos_filtrados = []
    for servico in servicos:
        atende, distancia = verificar_cobertura_fornecedor(servico.fornecedor, organizador)
        if atende:
            servico.distancia_km = distancia  #Adicionar distância ao objeto para usar no template
            servicos_filtrados.append(servico)
    servicos = servicos_filtrados
    
    #SEGUNDO FILTRO OPCIONAL: Filtro por distância máxima do organizador (complementar)
    distancia_maxima = request.GET.get('distancia_maxima', '').strip()
    if distancia_maxima:
        try:
            distancia_maxima = float(distancia_maxima)
            servicos_filtrados = []
            for servico in servicos:
                if servico.distancia_km is not None and servico.distancia_km <= distancia_maxima:
                    servicos_filtrados.append(servico)
            servicos = servicos_filtrados
        except ValueError:
            #Se o valor não for válido, não aplicar filtro
            pass
    
    #Obter categorias disponíveis para o filtro
    categorias_disponiveis = Fornecedor.CATEGORIA_CHOICES
    
    return render(request, 'pages/todos_servicos.html', {
        'servicos': servicos,
        'organizador': organizador,
        'categorias_disponiveis': categorias_disponiveis,
        'categoria_atual': categoria,
        'tag_atual': tag_busca,
        'distancia_maxima': distancia_maxima
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
    
    #Buscar eventos do organizador para o modal de orçamento
    from eventos.models import Evento
    eventos_organizador = Evento.objects.filter(idUsuario=organizador).order_by('-dataEvento')
    
    return render(request, 'pages/visualizar_servico.html', {
        'servico': servico,
        'organizador': organizador,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'eventos_organizador': eventos_organizador
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
        'fornecedor': fornecedor,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
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

@login_required
def solicitar_orcamento(request):
    """Processa a solicitação de orçamento"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Acesso restrito apenas para organizadores'})
    
    try:
        import json
        data = json.loads(request.body)
        
        evento_id = data.get('evento_id')
        servico_id = data.get('servico_id')
        itens_selecionados = data.get('itens_selecionados', [])
        consideracoes = data.get('consideracoes', '')
        
        #ID Eventos
        try:
            evento_id = int(evento_id)
            servico_id = int(servico_id)
            itens_selecionados = [int(item_id) for item_id in itens_selecionados]
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'IDs inválidos'})
        
        #Valida dados
        if not evento_id or not servico_id:
            return JsonResponse({'success': False, 'error': 'Dados incompletos'})
        
        #Verifica se o evento pertence ao organizador
        from eventos.models import Evento
        evento = get_object_or_404(Evento, id=evento_id, idUsuario=organizador)
        
        #Verifica se o serviço existe e está ativo
        servico = get_object_or_404(Servico, id=servico_id, ativo=True)
        
        #Cria a solicitação de orçamento
        solicitacao = SolicitacaoOrcamento.objects.create(
            organizador=organizador,
            fornecedor=servico.fornecedor,
            servico=servico,
            evento=evento,
            itens_selecionados=itens_selecionados,
            consideracoes=consideracoes
        )
        
        #Cria primeiro registro no histórico
        if consideracoes:
            HistoricoOrcamento.objects.create(
                solicitacao=solicitacao,
                tipo_usuario='organizador',
                mensagem=consideracoes
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação de orçamento enviada com sucesso!',
            'solicitacao_id': solicitacao.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def minhas_solicitacoes_organizador(request):
    #Lista as solicitações de orçamento feitas pelo organizador
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para organizadores.')
        return redirect('index')
    
    solicitacoes = SolicitacaoOrcamento.objects.filter(organizador=organizador).select_related(
        'fornecedor__user', 'servico', 'evento'
    ).order_by('-data_solicitacao')
    
    return render(request, 'pages/minhas_solicitacoes_organizador.html', {
        'solicitacoes': solicitacoes,
        'organizador': organizador
    })

@login_required
def minhas_solicitacoes_fornecedor(request):
    #Lista as solicitações de orçamento recebidas pelo fornecedor
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Acesso restrito apenas para fornecedores.')
        return redirect('index')
    
    solicitacoes = SolicitacaoOrcamento.objects.filter(fornecedor=fornecedor).select_related(
        'organizador__user', 'servico', 'evento'
    ).order_by('-data_solicitacao')
    
    return render(request, 'pages/minhas_solicitacoes_fornecedor.html', {
        'solicitacoes': solicitacoes,
        'fornecedor': fornecedor
    })

@login_required
def detalhes_solicitacao(request, solicitacao_id):
    #Mostra os detalhes de uma solicitação de orçamento
    solicitacao = get_object_or_404(SolicitacaoOrcamento, id=solicitacao_id)
    
    #Verifica permissão
    try:
        organizador = Organizador.objects.get(user=request.user)
        if solicitacao.organizador != organizador:
            messages.error(request, 'Você não tem permissão para acessar esta solicitação.')
            return redirect('minhas_solicitacoes_organizador')
        tipo_usuario = 'organizador'
    except Organizador.DoesNotExist:
        try:
            fornecedor = Fornecedor.objects.get(user=request.user)
            if solicitacao.fornecedor != fornecedor:
                messages.error(request, 'Você não tem permissão para acessar esta solicitação.')
                return redirect('minhas_solicitacoes_fornecedor')
            tipo_usuario = 'fornecedor'
        except Fornecedor.DoesNotExist:
            messages.error(request, 'Acesso negado.')
            return redirect('index')
    
    return render(request, 'pages/detalhes_solicitacao.html', {
        'solicitacao': solicitacao,
        'tipo_usuario': tipo_usuario
    })

@login_required
def adicionar_mensagem_orcamento(request, solicitacao_id):
    #Adiciona uma mensagem ao histórico do orçamento
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    solicitacao = get_object_or_404(SolicitacaoOrcamento, id=solicitacao_id)
    mensagem = request.POST.get('mensagem', '').strip()
    
    if not mensagem:
        return JsonResponse({'success': False, 'error': 'Mensagem não pode estar vazia'})
    
    #Verifica permissão e determinar tipo de usuário
    try:
        organizador = Organizador.objects.get(user=request.user)
        if solicitacao.organizador != organizador:
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
        tipo_usuario = 'organizador'
    except Organizador.DoesNotExist:
        try:
            fornecedor = Fornecedor.objects.get(user=request.user)
            if solicitacao.fornecedor != fornecedor:
                return JsonResponse({'success': False, 'error': 'Permissão negada'})
            tipo_usuario = 'fornecedor'
        except Fornecedor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Acesso negado'})
    
    #Cria mensagem no histórico
    historico = HistoricoOrcamento.objects.create(
        solicitacao=solicitacao,
        tipo_usuario=tipo_usuario,
        mensagem=mensagem
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Mensagem adicionada com sucesso!'
    })

@login_required
def atualizar_status_orcamento(request, solicitacao_id):
    #Atualiza o status de uma solicitação de orçamento
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    solicitacao = get_object_or_404(SolicitacaoOrcamento, id=solicitacao_id)
    novo_status = request.POST.get('status', '').strip()
    
    if not novo_status:
        return JsonResponse({'success': False, 'error': 'Status não informado'})
    
    #Verifica permissão e determinar tipo de usuário
    try:
        organizador = Organizador.objects.get(user=request.user)
        if solicitacao.organizador != organizador:
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
        tipo_usuario = 'organizador'
    except Organizador.DoesNotExist:
        try:
            fornecedor = Fornecedor.objects.get(user=request.user)
            if solicitacao.fornecedor != fornecedor:
                return JsonResponse({'success': False, 'error': 'Permissão negada'})
            tipo_usuario = 'fornecedor'
        except Fornecedor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Acesso negado'})
    
    #Valida status permitido para cada tipo de usuário
    status_permitidos = {
        'fornecedor': ['em_analise', 'orcamento_enviado', 'recusado'],
        'organizador': ['aceito', 'recusado', 'em_revisao']
    }
    
    if novo_status not in status_permitidos[tipo_usuario]:
        return JsonResponse({'success': False, 'error': 'Status não permitido para este usuário'})
    
    #Verifica se o organizador pode alterar o status
    if tipo_usuario == 'organizador':
        #Verifica se o fornecedor já alterou o status pelo menos uma vez
        historico_fornecedor = solicitacao.historico.filter(tipo_usuario='fornecedor').exists()
        if not historico_fornecedor and solicitacao.status == 'pendente':
            return JsonResponse({
                'success': False, 
                'error': 'Você só pode alterar o status após o fornecedor ter respondido'
            })
    
    #Atualizar status
    status_anterior = solicitacao.status
    solicitacao.status = novo_status
    solicitacao.save()
    
    # Criar mensagem no histórico sobre a mudança de status
    status_choices = dict(SolicitacaoOrcamento.STATUS_CHOICES)
    status_anterior_display = status_choices.get(status_anterior, status_anterior)
    status_novo_display = status_choices.get(novo_status, novo_status)
    
    mensagem_status = f"Status alterado de '{status_anterior_display}' para '{status_novo_display}'"
    HistoricoOrcamento.objects.create(
        solicitacao=solicitacao,
        tipo_usuario=tipo_usuario,
        mensagem=mensagem_status
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Status atualizado para "{solicitacao.get_status_display()}"',
        'novo_status': novo_status,
        'status_display': solicitacao.get_status_display()
    })

@login_required
def atualizar_valor_orcamento(request, solicitacao_id):
    #Atualiza o valor do orçamento de uma solicitação
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    solicitacao = get_object_or_404(SolicitacaoOrcamento, id=solicitacao_id)
    valor_orcamento = request.POST.get('valor_orcamento', '').strip()
    
    #Verifica se é o fornecedor da solicitação
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if solicitacao.fornecedor != fornecedor:
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
    except Fornecedor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Acesso restrito apenas para fornecedores'})
    
    #Valida valor
    if not valor_orcamento:
        return JsonResponse({'success': False, 'error': 'Valor não informado'})
    
    try:
        valor = float(valor_orcamento.replace(',', '.'))
        if valor <= 0:
            return JsonResponse({'success': False, 'error': 'Valor deve ser maior que zero'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Valor inválido'})
    
    #Atualiza valor
    solicitacao.valor_orcamento = valor
    solicitacao.save()
    
    #Cria mensagem no histórico sobre a atualização do valor
    mensagem_valor = f"Valor do orçamento definido: R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    HistoricoOrcamento.objects.create(
        solicitacao=solicitacao,
        tipo_usuario='fornecedor',
        mensagem=mensagem_valor
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Valor do orçamento atualizado para R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
        'valor_formatado': f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    })
