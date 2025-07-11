from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Fornecedor, Organizador
from usuarios.utils import geocodificar_cep, atualizar_coordenadas_usuario
from .models import Evento, Pergunta, Resposta, AvaliacaoFornecedor
from .forms import EventoForm, PerguntaForm, RespostaForm, AvaliacaoFornecedorForm
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from agenda.models import EventoAgenda
from datetime import datetime
import json

@login_required(login_url='login')
def index(request):
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        is_fornecedor = True
        # Para fornecedores: mostra todos os eventos
        eventos = Evento.objects.all().order_by('-dataEvento')
    except Fornecedor.DoesNotExist:
        is_fornecedor = False
        eventos = None
    
    try:
        organizador = Organizador.objects.get(user=request.user)
        is_organizador = True
        # Para organizadores: mostra apenas seus eventos
        eventos = Evento.objects.filter(idUsuario=organizador).order_by('-dataEvento')
    except Organizador.DoesNotExist:
        is_organizador = False
    
    return render(request, 'pages/index.html', {
        'is_fornecedor': is_fornecedor,
        'is_organizador': is_organizador,
        'eventos': eventos  # Passa os eventos para o template
    })

@login_required(login_url='login')
def criar_evento(request):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        return redirect('index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.idUsuario = organizador
            
            # Geocodificar o CEP para obter coordenadas e endereço completo
            cep = form.cleaned_data['cep']
            if cep:
                latitude, longitude = geocodificar_cep(cep)
                if latitude and longitude:
                    evento.latitude = latitude
                    evento.longitude = longitude
                    
                    # Buscar endereço completo via ViaCEP
                    import requests
                    try:
                        cep_limpo = cep.replace('-', '').replace('.', '').strip()
                        viacep_url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
                        response = requests.get(viacep_url, timeout=5)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if not data.get('erro'):
                                endereco_parts = []
                                if data.get('logradouro'):
                                    endereco_parts.append(data['logradouro'])
                                if data.get('bairro'):
                                    endereco_parts.append(data['bairro'])
                                if data.get('localidade'):
                                    endereco_parts.append(data['localidade'])
                                if data.get('uf'):
                                    endereco_parts.append(data['uf'])
                                if data.get('cep'):
                                    endereco_parts.append(data['cep'])
                                
                                evento.endereco_completo = ', '.join(endereco_parts)
                    except:
                        #Se não conseguir buscar o endereço completo, usar apenas o CEP
                        evento.endereco_completo = f"CEP: {cep}"
            
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('index')
    else:
        form = EventoForm()
    
    return render(request, 'pages/criar_evento.html', {'form': form})

@login_required(login_url='login')
def editar_evento(request, evento_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem editar eventos.')
        return redirect('index')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verifica se o organizador é o dono do evento
    if evento.idUsuario != organizador:
        messages.error(request, 'Você só pode editar seus próprios eventos.')
        return redirect('index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save(commit=False)
            
            # Geocodificar o CEP para obter coordenadas e endereço completo
            cep = form.cleaned_data['cep']
            if cep:
                latitude, longitude = geocodificar_cep(cep)
                if latitude and longitude:
                    evento.latitude = latitude
                    evento.longitude = longitude
                    
                    # Buscar endereço completo via ViaCEP
                    import requests
                    try:
                        cep_limpo = cep.replace('-', '').replace('.', '').strip()
                        viacep_url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
                        response = requests.get(viacep_url, timeout=5)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if not data.get('erro'):
                                endereco_parts = []
                                if data.get('logradouro'):
                                    endereco_parts.append(data['logradouro'])
                                if data.get('bairro'):
                                    endereco_parts.append(data['bairro'])
                                if data.get('localidade'):
                                    endereco_parts.append(data['localidade'])
                                if data.get('uf'):
                                    endereco_parts.append(data['uf'])
                                if data.get('cep'):
                                    endereco_parts.append(data['cep'])
                                
                                evento.endereco_completo = ', '.join(endereco_parts)
                    except:
                        # Se não conseguir buscar o endereço completo, usar apenas o CEP
                        evento.endereco_completo = f"CEP: {cep}"
            
            evento.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('index')
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'pages/editar_evento.html', {
        'form': form,
        'evento': evento
    })

@login_required(login_url='login')
def excluir_evento(request, evento_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem excluir eventos.')
        return redirect('index')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verifica se o organizador é o dono do evento
    if evento.idUsuario != organizador:
        messages.error(request, 'Você só pode excluir seus próprios eventos.')
        return redirect('index')
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('index')
    
    return render(request, 'pages/confirmar_exclusao.html', {'evento': evento})

@login_required(login_url='login')
def fazer_pergunta(request, evento_id):
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
    except Fornecedor.DoesNotExist:
        messages.error(request, 'Apenas fornecedores podem fazer perguntas.')
        return redirect('index')
    
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = PerguntaForm(request.POST)
        if form.is_valid():
            pergunta = form.save(commit=False)
            pergunta.evento = evento
            pergunta.fornecedor = fornecedor
            pergunta.save()
            messages.success(request, 'Pergunta enviada com sucesso!')
            return redirect('detalhes_evento', evento_id=evento.id)
    else:
        form = PerguntaForm()
    
    return render(request, 'pages/fazer_pergunta.html', {
        'form': form,
        'evento': evento
    })

@login_required(login_url='login')
def responder_pergunta(request, pergunta_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem responder perguntas.')
        return redirect('index')
    
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    
    # Verifica se o organizador é o dono do evento
    if pergunta.evento.idUsuario != organizador:
        messages.error(request, 'Você só pode responder perguntas sobre seus próprios eventos.')
        return redirect('index')
    
    if request.method == 'POST':
        form = RespostaForm(request.POST)
        if form.is_valid():
            resposta = form.save(commit=False)
            resposta.pergunta = pergunta
            resposta.organizador = organizador
            resposta.save()
            
            # Marcar a pergunta como respondida
            pergunta.respondida = True
            pergunta.save()
            
            messages.success(request, 'Resposta enviada com sucesso!')
            return redirect('detalhes_evento', evento_id=pergunta.evento.id)
    else:
        form = RespostaForm()
    
    return render(request, 'pages/responder_pergunta.html', {
        'form': form,
        'pergunta': pergunta
    })

@login_required
def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verificar se o usuário é fornecedor ou organizador dono do evento
    is_fornecedor = False
    is_organizador_dono = False
    
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        is_fornecedor = True
    except Fornecedor.DoesNotExist:
        pass
    
    try:
        organizador = Organizador.objects.get(user=request.user)
        if evento.idUsuario == organizador:
            is_organizador_dono = True
    except Organizador.DoesNotExist:
        pass
    
    perguntas = evento.perguntas.all().order_by('-data_criacao')
    
    # Buscar fornecedores vinculados através de orçamentos aceitos
    fornecedores_vinculados = Fornecedor.objects.filter(
        solicitacoes_recebidas__evento=evento,
        solicitacoes_recebidas__status='aceito'
    ).distinct()
    
    return render(request, 'pages/detalhes_evento.html', {
        'evento': evento,
        'perguntas': perguntas,
        'is_fornecedor': is_fornecedor,
        'is_organizador_dono': is_organizador_dono,
        'fornecedores_vinculados': fornecedores_vinculados
    })

    
@login_required
def avaliar_fornecedor(request, fornecedor_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem avaliar fornecedores.')
        return redirect('index')
    
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)
    
    # Verifica se já existe uma avaliação deste organizador para este fornecedor
    try:
        avaliacao_existente = AvaliacaoFornecedor.objects.get(
            organizador=organizador,
            fornecedor=fornecedor
        )
        # Se já existe, redireciona para edição
        return redirect('editar_avaliacao', avaliacao_id=avaliacao_existente.id)
    except AvaliacaoFornecedor.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = AvaliacaoFornecedorForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.organizador = organizador
            avaliacao.fornecedor = fornecedor
            avaliacao.save()
            messages.success(request, 'Avaliação registrada com sucesso!')
            return redirect('detalhes_fornecedor', fornecedor_id=fornecedor.id)
    else:
        form = AvaliacaoFornecedorForm()
    
    return render(request, 'pages/avaliar_fornecedor.html', {
        'form': form,
        'fornecedor': fornecedor
    })

@login_required
def editar_avaliacao(request, avaliacao_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem editar avaliações.')
        return redirect('index')
    
    avaliacao = get_object_or_404(AvaliacaoFornecedor, id=avaliacao_id)
    
    # Verifica se o organizador é o autor da avaliação
    if avaliacao.organizador != organizador:
        messages.error(request, 'Você só pode editar suas próprias avaliações.')
        return redirect('index')
    
    if request.method == 'POST':
        form = AvaliacaoFornecedorForm(request.POST, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avaliação atualizada com sucesso!')
            return redirect('detalhes_fornecedor', fornecedor_id=avaliacao.fornecedor.id)
    else:
        form = AvaliacaoFornecedorForm(instance=avaliacao)
    
    return render(request, 'pages/editar_avaliacao.html', {
        'form': form,
        'avaliacao': avaliacao,
        'fornecedor': avaliacao.fornecedor  # Adicionando fornecedor ao contexto
    })

@login_required
def detalhes_fornecedor(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)
    avaliacoes = fornecedor.avaliacoes.all().order_by('-data_criacao')
    
    # Verifica se o usuário atual é um organizador que já avaliou este fornecedor
    ja_avaliou = False
    avaliacao_usuario = None
    
    try:
        organizador = Organizador.objects.get(user=request.user)
        try:
            avaliacao_usuario = AvaliacaoFornecedor.objects.get(
                organizador=organizador,
                fornecedor=fornecedor
            )
            ja_avaliou = True
        except AvaliacaoFornecedor.DoesNotExist:
            pass
    except Organizador.DoesNotExist:
        pass
    
    media_avaliacoes = fornecedor.avaliacoes.aggregate(models.Avg('nota'))['nota__avg']
    media_avaliacoes = round(media_avaliacoes, 1) if media_avaliacoes is not None else None
    
    return render(request, 'pages/detalhes_fornecedor.html', {
        'fornecedor': fornecedor,
        'avaliacoes': avaliacoes,
        'media_avaliacoes': media_avaliacoes,
        'ja_avaliou': ja_avaliou,
        'avaliacao_usuario': avaliacao_usuario,
        'is_organizador': hasattr(request.user, 'organizador')
    })

@login_required
def todos_fornecedores(request):
    fornecedores = Fornecedor.objects.all().order_by('categoria', 'user__first_name')
    
    # Verifica se o usuário é um organizador
    is_organizador = hasattr(request.user, 'organizador')
    
    return render(request, 'pages/todos_fornecedores.html', {
        'fornecedores': fornecedores,
        'is_organizador': is_organizador
    })

@login_required
def excluir_avaliacao(request, avaliacao_id):
    try:
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        messages.error(request, 'Apenas organizadores podem excluir avaliações.')
        return redirect('index')
    
    avaliacao = get_object_or_404(AvaliacaoFornecedor, id=avaliacao_id)
    
    # Verifica se o organizador é o autor da avaliação
    if avaliacao.organizador != organizador:
        messages.error(request, 'Você só pode excluir suas próprias avaliações.')
        return redirect('index')
    
    if request.method == 'POST':
        fornecedor_id = avaliacao.fornecedor.id
        avaliacao.delete()
        messages.success(request, 'Avaliação excluída com sucesso!')
        return redirect('detalhes_fornecedor', fornecedor_id=fornecedor_id)
    
    return render(request, 'pages/confirmar_exclusao_avaliacao.html', {
        'avaliacao': avaliacao
    })

@login_required
def adicionar_compromisso_evento(request):
    """Adiciona um compromisso relacionado ao evento na agenda"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        # Verificar se é organizador
        organizador = Organizador.objects.get(user=request.user)
    except Organizador.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Acesso restrito apenas para organizadores'})
    
    try:
        # Obter dados do formulário
        evento_id = request.POST.get('evento_id')
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        local = request.POST.get('local', '').strip()
        tipo = request.POST.get('tipo', 'reuniao')
        prioridade = request.POST.get('prioridade', 'media')
        fornecedores_ids = request.POST.getlist('fornecedores')
        
        # Validações
        if not evento_id or not titulo or not data_inicio or not data_fim:
            return JsonResponse({'success': False, 'error': 'Campos obrigatórios não preenchidos'})
        
        # Verificar se o evento existe e pertence ao organizador
        evento = get_object_or_404(Evento, id=evento_id, idUsuario=organizador)
        
        # Converter datas
        try:
            data_inicio = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            data_fim = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Formato de data inválido'})
        
        # Verificar se data_fim é posterior a data_inicio
        if data_fim <= data_inicio:
            return JsonResponse({'success': False, 'error': 'Data de fim deve ser posterior à data de início'})
        
        # Criar o evento na agenda
        evento_agenda = EventoAgenda.objects.create(
            titulo=titulo,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            local=local,
            tipo=tipo,
            prioridade=prioridade,
            usuario=request.user,
            organizador=organizador,
            evento_relacionado=evento
        )
        
        # Vincular fornecedores selecionados
        if fornecedores_ids:
            fornecedores = Fornecedor.objects.filter(
                id__in=fornecedores_ids,
                solicitacoes_recebidas__evento=evento,
                solicitacoes_recebidas__status='aceito'
            )
            for fornecedor in fornecedores:
                # Criar uma cópia do evento para cada fornecedor vinculado
                EventoAgenda.objects.create(
                    titulo=f"{titulo} - {fornecedor.user.get_full_name() or fornecedor.user.username}",
                    descricao=descricao,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    local=local,
                    tipo=tipo,
                    prioridade=prioridade,
                    usuario=fornecedor.user,
                    fornecedor=fornecedor,
                    evento_relacionado=evento
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Compromisso adicionado com sucesso!',
            'evento_id': evento_agenda.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})