from django.db import models
from django.contrib.auth.models import User

class Organizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    endereco = models.TextField(max_length=500)
    telefone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Organizador"

class Fornecedor(models.Model):
    CATEGORIA_CHOICES = [
        ('alimentacao', 'Alimentação'),
        ('decoracao', 'Decoração'),
        ('logistica', 'Logística'),
        ('musica', 'Música e Entretenimento'),
        ('fotografia', 'Fotografia e Vídeo'),
        ('locacao', 'Locação de Equipamentos'),
        ('seguranca', 'Segurança'),
        ('outros', 'Outros'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    endereco = models.TextField(max_length=500)
    telefone = models.CharField(max_length=20)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_categoria_display()}"
