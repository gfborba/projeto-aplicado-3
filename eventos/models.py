from django.db import models
from django.contrib.auth.models import User

class Avaliacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField()
    comentario = models.CharField(max_length=500)
    data = models.DateTimeField(auto_now_add=True)

    