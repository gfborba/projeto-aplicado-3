from django.db import models
from django.contrib.auth.models import User

class Organizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9, help_text="CEP no formato 00000-000", default='N/D')
    estado = models.CharField(max_length=2, default='N/D')
    cidade = models.CharField(max_length=100, default='N/D')
    bairro = models.CharField(max_length=100, default='N/D')
    logradouro = models.CharField(max_length=200, default='N/D')
    numero = models.CharField(max_length=10, default='N/D')
    complemento = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, default='N/D')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Organizador"

    def endereco_completo(self):
        """Retorna o endereço completo formatado"""
        endereco = f"{self.logradouro}"
        if self.numero and self.numero != 'N/D':
            endereco += f", {self.numero}"
        if self.complemento:
            endereco += f" - {self.complemento}"
        endereco += f", {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep}"
        return endereco

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
    cep = models.CharField(max_length=9, help_text="CEP no formato 00000-000", default='N/D')
    estado = models.CharField(max_length=2, default='N/D')
    cidade = models.CharField(max_length=100, default='N/D')
    bairro = models.CharField(max_length=100, default='N/D')
    logradouro = models.CharField(max_length=200, default='N/D')
    numero = models.CharField(max_length=10, default='N/D')
    complemento = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, default='N/D')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='outros')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_categoria_display()}"

    def endereco_completo(self):
        endereco = f"{self.logradouro}"
        if self.numero and self.numero != 'N/D':
            endereco += f", {self.numero}"
        if self.complemento:
            endereco += f" - {self.complemento}"
        endereco += f", {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep}"
        return endereco
