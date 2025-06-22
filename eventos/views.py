from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Fornecedor, Organizador
from .models import Evento
from .forms import EventoForm  # Criaremos este form depois

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
            evento.save()
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
            form.save()
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