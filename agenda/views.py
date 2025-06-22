from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
import json
from datetime import datetime, timedelta

from .models import EventoAgenda
from usuarios.models import Fornecedor, Organizador
from eventos.models import Evento

@login_required
def agenda_view(request):
    #View principal da agenda com o calendário FullCalendar
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        tipo_usuario = 'fornecedor'
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            tipo_usuario = 'organizador'
        except Organizador.DoesNotExist:
            messages.error(request, 'Acesso negado.')
            return redirect('index')
    
    return render(request, 'agenda/agenda.html', {
        'tipo_usuario': tipo_usuario
    })

@login_required
def eventos_json(request):
    #Retorna os eventos em formato JSON para o FullCalendar
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        eventos = EventoAgenda.objects.filter(fornecedor=fornecedor, ativo=True)
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            eventos = EventoAgenda.objects.filter(organizador=organizador, ativo=True)
        except Organizador.DoesNotExist:
            return JsonResponse({'error': 'Usuário não encontrado'}, status=400)
    
    eventos_data = []
    for evento in eventos:
        eventos_data.append({
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.data_inicio.isoformat(),
            'end': evento.data_fim.isoformat(),
            'allDay': evento.todo_dia,
            'backgroundColor': evento.cor,
            'borderColor': evento.cor,
            'textColor': '#ffffff',
            'extendedProps': {
                'descricao': evento.descricao or '',
                'tipo': evento.tipo,
                'prioridade': evento.prioridade,
                'local': evento.local or '',
                'status': evento.status
            }
        })
    
    return JsonResponse(eventos_data, safe=False)

@login_required
def criar_compromisso(request):
    #Cria um novo evento via AJAX
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        #Determinar tipo de usuário
        try:
            fornecedor = Fornecedor.objects.get(user=request.user)
            tipo_usuario = 'fornecedor'
        except Fornecedor.DoesNotExist:
            try:
                organizador = Organizador.objects.get(user=request.user)
                tipo_usuario = 'organizador'
            except Organizador.DoesNotExist:
                return JsonResponse({'error': 'Usuário não encontrado'}, status=400)
        
        #Criar evento
        evento = EventoAgenda(
            titulo=data.get('title', ''),
            descricao=data.get('description', ''),
            data_inicio=datetime.fromisoformat(data['start'].replace('Z', '+00:00')),
            data_fim=datetime.fromisoformat(data['end'].replace('Z', '+00:00')),
            tipo=data.get('tipo', 'evento'),
            prioridade=data.get('prioridade', 'media'),
            local=data.get('local', ''),
            cor=data.get('backgroundColor', '#3788d8'),
            todo_dia=data.get('allDay', False),
            usuario=request.user
        )
        
        #Associar ao tipo de usuário correto
        if tipo_usuario == 'fornecedor':
            evento.fornecedor = fornecedor
        else:
            evento.organizador = organizador
        
        evento.save()
        
        return JsonResponse({
            'success': True,
            'event': {
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.data_inicio.isoformat(),
                'end': evento.data_fim.isoformat(),
                'allDay': evento.todo_dia,
                'backgroundColor': evento.cor,
                'borderColor': evento.cor,
                'textColor': '#ffffff'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def atualizar_compromisso(request, evento_id):
    #Atualiza um evento existente via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    evento = get_object_or_404(EventoAgenda, id=evento_id)
    
    # Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if evento.fornecedor != fornecedor:
            return JsonResponse({'error': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            if evento.organizador != organizador:
                return JsonResponse({'error': 'Permissão negada'}, status=403)
        except Organizador.DoesNotExist:
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Atualizar campos
        if 'title' in data:
            evento.titulo = data['title']
        if 'description' in data:
            evento.descricao = data['description']
        if 'start' in data:
            evento.data_inicio = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
        if 'end' in data:
            evento.data_fim = datetime.fromisoformat(data['end'].replace('Z', '+00:00'))
        if 'backgroundColor' in data:
            evento.cor = data['backgroundColor']
        if 'allDay' in data:
            evento.todo_dia = data['allDay']
        if 'tipo' in data:
            evento.tipo = data['tipo']
        if 'prioridade' in data:
            evento.prioridade = data['prioridade']
        if 'local' in data:
            evento.local = data['local']
        
        evento.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def deletar_compromisso(request, evento_id):
    """Deleta um evento via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    evento = get_object_or_404(EventoAgenda, id=evento_id)
    
    # Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if evento.fornecedor != fornecedor:
            return JsonResponse({'error': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            if evento.organizador != organizador:
                return JsonResponse({'error': 'Permissão negada'}, status=403)
        except Organizador.DoesNotExist:
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    evento.delete()
    return JsonResponse({'success': True})

@login_required
def detalhes_compromisso(request, evento_id):
    """Retorna detalhes de um evento específico"""
    evento = get_object_or_404(EventoAgenda, id=evento_id)
    
    # Verificar permissão
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        if evento.fornecedor != fornecedor:
            return JsonResponse({'error': 'Permissão negada'}, status=403)
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            if evento.organizador != organizador:
                return JsonResponse({'error': 'Permissão negada'}, status=403)
        except Organizador.DoesNotExist:
            return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    return JsonResponse({
        'id': evento.id,
        'title': evento.titulo,
        'description': evento.descricao,
        'start': evento.data_inicio.isoformat(),
        'end': evento.data_fim.isoformat(),
        'allDay': evento.todo_dia,
        'backgroundColor': evento.cor,
        'tipo': evento.tipo,
        'prioridade': evento.prioridade,
        'local': evento.local,
        'status': evento.status,
        'duracao': evento.duracao
    })

@login_required
def eventos_miniatura(request):
    """Retorna eventos para exibição em miniatura na página index"""
    try:
        fornecedor = Fornecedor.objects.get(user=request.user)
        eventos = EventoAgenda.objects.filter(
            fornecedor=fornecedor, 
            ativo=True,
            data_inicio__gte=timezone.now().date()
        ).order_by('data_inicio')[:5]  # Limita a 5 eventos
    except Fornecedor.DoesNotExist:
        try:
            organizador = Organizador.objects.get(user=request.user)
            eventos = EventoAgenda.objects.filter(
                organizador=organizador, 
                ativo=True,
                data_inicio__gte=timezone.now().date()
            ).order_by('data_inicio')[:5]  # Limita a 5 eventos
        except Organizador.DoesNotExist:
            eventos = []
    
    eventos_data = []
    for evento in eventos:
        eventos_data.append({
            'id': evento.id,
            'titulo': evento.titulo,
            'data_inicio': evento.data_inicio.strftime('%d/%m/%Y %H:%M'),
            'tipo': evento.get_tipo_display(),
            'cor': evento.cor,
            'status': evento.status
        })
    
    return JsonResponse(eventos_data, safe=False)
