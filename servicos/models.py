from django.db import models
from usuarios.models import Fornecedor

class Servico(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.fornecedor.user.first_name}"
    
    def total_itens(self):
        return self.itens.count()
    
    def tem_imagens(self):
        return self.imagens.exists()

class Item(models.Model):
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='itens')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
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


