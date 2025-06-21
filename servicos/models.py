from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json
from usuarios.models import Fornecedor

class Servico(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    tags = models.JSONField(default=list, blank=True, encoder=DjangoJSONEncoder)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.fornecedor.user.first_name}"
    
    @property
    def total_itens(self):
        return self.itens.count()
    
    @property
    def tem_imagens(self):
        return self.imagens.exists()
    
    def get_tags_list(self):
        #Retorna as tags como uma lista
        if isinstance(self.tags, list):
            return self.tags
        elif isinstance(self.tags, str):
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    def add_tag(self, tag):
        #Adiciona uma tag ao serviço
        tags = self.get_tags_list()
        if tag.strip() and tag.strip() not in tags:
            tags.append(tag.strip())
            self.tags = tags
            self.save()
    
    def remove_tag(self, tag):
        #Remove uma tag do serviço
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.tags = tags
            self.save()

class Item(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='itens/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.servico.nome}"

class ImagemServico(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='servicos/')
    legenda = models.CharField(max_length=200, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Imagem de {self.servico.nome}"


