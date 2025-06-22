from django.db import models
from usuarios.models import Organizador

class Evento(models.Model):
    nomeEvento = models.CharField(max_length=100,verbose_name='Nome do Evento',null=False,blank=False)
    dataEvento = models.DateTimeField(verbose_name='Data e Hora do Evento',null=False,blank=False)  
    localEvento = models.CharField(max_length=200,verbose_name='Local do Evento',null=False,blank=False)
    descricaoEvento = models.TextField(verbose_name='Descrição do Evento',null=False,blank=False) 
    idUsuario = models.ForeignKey(Organizador,on_delete=models.CASCADE,verbose_name='Organizador',null=False,blank=False,related_name='eventos')
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-dataEvento']
    
    def __str__(self):
        return f"{self.nomeEvento} - {self.dataEvento.strftime('%d/%m/%Y')}"