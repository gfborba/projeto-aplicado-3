from django.db import models
from usuarios.models import Organizador, Fornecedor
from decimal import Decimal

class Evento(models.Model):
    nomeEvento = models.CharField(max_length=100,verbose_name='Nome do Evento',null=False,blank=False)
    dataEvento = models.DateTimeField(verbose_name='Data e Hora do Evento',null=False,blank=False)  
    localEvento = models.CharField(max_length=200,verbose_name='Local do Evento',null=False,blank=False)
    descricaoEvento = models.TextField(verbose_name='Descrição do Evento',null=False,blank=False) 
    idUsuario = models.ForeignKey(Organizador,on_delete=models.CASCADE,verbose_name='Organizador',null=False,blank=False,related_name='eventos')
    cep = models.CharField(max_length=9, verbose_name='CEP', null=True, blank=True)
    endereco_completo = models.TextField(verbose_name='Endereço Completo', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude', null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude', null=True, blank=True)
    previsao_participantes = models.PositiveIntegerField(verbose_name='Previsão de Participantes', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-dataEvento']
    
    def __str__(self):
        return f"{self.nomeEvento} - {self.dataEvento.strftime('%d/%m/%Y')}"
    
    def tem_coordenadas(self):
        return self.latitude is not None and self.longitude is not None
    
class Pergunta(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='perguntas')
    fornecedor = models.ForeignKey('usuarios.Fornecedor', on_delete=models.CASCADE, related_name='perguntas_feitas')
    texto = models.TextField(verbose_name='Pergunta', null=False, blank=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    respondida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'

    def __str__(self):
        return f"Pergunta de {self.fornecedor.user.username} sobre {self.evento.nomeEvento}"

class Resposta(models.Model):
    pergunta = models.OneToOneField(Pergunta, on_delete=models.CASCADE, related_name='resposta')
    organizador = models.ForeignKey(Organizador, on_delete=models.CASCADE, related_name='respostas_dadas')
    texto = models.TextField(verbose_name='Resposta', null=False, blank=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_criacao']
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    def __str__(self):
        return f"Resposta de {self.organizador.user.username} para pergunta #{self.pergunta.id}"
    
    
class AvaliacaoFornecedor(models.Model):
    NOTA_CHOICES = [
        (1, '1 - Péssimo'),
        (2, '2 - Ruim'),
        (3, '3 - Regular'),
        (4, '4 - Bom'),
        (5, '5 - Excelente'),
    ]
    
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='avaliacoes')
    organizador = models.ForeignKey(Organizador, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    nota = models.PositiveSmallIntegerField(choices=NOTA_CHOICES)
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fornecedor', 'organizador') 
        verbose_name = 'Avaliação de Fornecedor'
        verbose_name_plural = 'Avaliações de Fornecedores'

    def __str__(self):
        return f"Avaliação de {self.organizador} para {self.fornecedor} - Nota: {self.nota}"
    
    def delete_avaliacao(self):
        """Método personalizado para deletar avaliação"""
        self.delete()