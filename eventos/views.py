from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Fornecedor, Organizador
from usuarios.utils import geocodificar_cep, atualizar_coordenadas_usuario
from .models import Evento, Pergunta, Resposta
from .forms import EventoForm, PerguntaForm, RespostaForm

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
    
    return render(request, 'pages/detalhes_evento.html', {
        'evento': evento,
        'perguntas': perguntas,
        'is_fornecedor': is_fornecedor,
        'is_organizador_dono': is_organizador_dono
    })