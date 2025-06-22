from django.db import models
from django.contrib.auth.models import User
from usuarios.models import Fornecedor, Organizador
from eventos.models import Evento

class EventoAgenda(models.Model):
    TIPO_CHOICES = [
        ('evento', 'Evento'),
        ('reuniao', 'Reunião'),
        ('consulta', 'Consulta'),
        ('lembrete', 'Lembrete'),
        ('outro', 'Outro'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    data_inicio = models.DateTimeField(verbose_name='Data de Início')
    data_fim = models.DateTimeField(verbose_name='Data de Fim')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='evento', verbose_name='Tipo')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media', verbose_name='Prioridade')
    local = models.CharField(max_length=200, blank=True, null=True, verbose_name='Local')
    
    # Relacionamentos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_agenda', verbose_name='Usuário')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, null=True, blank=True, related_name='eventos_agenda', verbose_name='Fornecedor')
    organizador = models.ForeignKey(Organizador, on_delete=models.CASCADE, null=True, blank=True, related_name='eventos_agenda', verbose_name='Organizador')
    evento_relacionado = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_agenda', verbose_name='Evento Relacionado')
    
    # Configurações
    cor = models.CharField(max_length=7, default='#3788d8', verbose_name='Cor do Evento')  # Hex color
    todo_dia = models.BooleanField(default=False, verbose_name='Todo o Dia')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        verbose_name = 'Evento da Agenda'
        verbose_name_plural = 'Eventos da Agenda'
        ordering = ['data_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duracao(self):
        #Retorna a duração do evento em minutos
        if self.data_fim and self.data_inicio:
            return int((self.data_fim - self.data_inicio).total_seconds() / 60)
        return 0
    
    @property
    def status(self):
        #Retorna o status do evento baseado na data atual
        from django.utils import timezone
        now = timezone.now()
        
        if self.data_fim < now:
            return 'concluido'
        elif self.data_inicio <= now <= self.data_fim:
            return 'em_andamento'
        else:
            return 'agendado'
