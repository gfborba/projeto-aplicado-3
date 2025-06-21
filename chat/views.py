from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from usuarios.models import Organizador, Fornecedor
from .models import Room, Message

@login_required
def chat_room(request, username):
    #View para acessar uma sala de chat específica
    try:
        target_user = get_object_or_404(User, username=username)
        
        #Verifica se o usuário atual não está tentando conversar consigo mesmo
        if target_user == request.user:
            messages.error(request, 'Você não pode conversar consigo mesmo.')
            return redirect('index')
        
        #Busca ou cria a sala de chat
        room_qs = Room.objects.filter(users=target_user).filter(users=request.user)
        if not room_qs.exists():
            room = Room.objects.create()
            room.users.set([target_user, request.user])
        else:
            room = room_qs.first()
        
        #Busca mensagens da sala
        messages_list = Message.objects.filter(room=room).order_by('timestamp')
        
        return render(request, 'chat/room.html', {
            'room': room,
            'target_user': target_user,
            'messages': messages_list,
        })
        
    except User.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('index')

@login_required
def chat_list(request):
    #View para listar todas as conversas do usuário
    user_rooms = Room.objects.filter(users=request.user)
    
    #Para cada sala, busca o outro usuário
    conversations = []
    for room in user_rooms:
        other_user = room.users.exclude(id=request.user.id).first()
        if other_user:
            #Busca a última mensagem da sala
            last_message = Message.objects.filter(room=room).order_by('-timestamp').first()
            
            conversations.append({
                'room': room,
                'other_user': other_user,
                'last_message': last_message,
            })
    
    # Ordena pela última mensagem
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else x['room'].created_at, reverse=True)
    
    return render(request, 'chat/list.html', {
        'conversations': conversations,
    })
