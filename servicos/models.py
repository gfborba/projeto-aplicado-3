from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from usuarios.models import Fornecedor, Organizador
import json

class Servico(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} - {self.fornecedor.user.username}"
    
    def get_tags_list(self):
        if isinstance(self.tags, str):
            try:
                return json.loads(self.tags)
            except:
                return []
        return self.tags or []
    
    def add_tag(self, tag):
        """Adiciona uma tag ao serviço"""
        tags = self.get_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.tags = tags
            self.save()
    
    def remove_tag(self, tag):
        #Remove uma tag do serviço
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.tags = tags
            self.save()
    
    @property
    def total_itens(self):
        return self.itens.count()
    
    @property
    def tem_imagens(self):
        return self.imagens.exists()

class Item(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='itens/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.servico.nome}"

class ImagemServico(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='servicos/')
    legenda = models.CharField(max_length=200, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagem do Serviço'
        verbose_name_plural = 'Imagens dos Serviços'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"Imagem de {self.servico.nome}"

class SolicitacaoOrcamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('orcamento_enviado', 'Orçamento Enviado'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
        ('cancelado', 'Cancelado'),
    ]
    
    organizador = models.ForeignKey(Organizador, on_delete=models.CASCADE, related_name='solicitacoes_orcamento')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='solicitacoes_recebidas')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='solicitacoes')
    evento = models.ForeignKey('eventos.Evento', on_delete=models.CASCADE, related_name='solicitacoes_orcamento')
    itens_selecionados = models.JSONField(default=list)  # Lista de IDs dos itens selecionados
    consideracoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Solicitação de Orçamento'
        verbose_name_plural = 'Solicitações de Orçamento'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação de {self.organizador.user.username} para {self.fornecedor.user.username} - {self.servico.nome}"
    
    def get_itens_selecionados_objects(self):
        return Item.objects.filter(id__in=self.itens_selecionados)
    
    @property
    def total_itens_selecionados(self):
        return len(self.itens_selecionados)

class HistoricoOrcamento(models.Model):
    TIPO_CHOICES = [
        ('organizador', 'Organizador'),
        ('fornecedor', 'Fornecedor'),
    ]
    
    solicitacao = models.ForeignKey(SolicitacaoOrcamento, on_delete=models.CASCADE, related_name='historico')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico de Orçamento'
        verbose_name_plural = 'Histórico de Orçamentos'
        ordering = ['data_criacao']
    
    def __str__(self):
        return f"Mensagem de {self.tipo_usuario} em {self.solicitacao} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"


