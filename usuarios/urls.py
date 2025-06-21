from django.urls import path
from . import views

urlpatterns = [
    path('escolha-cadastro/', views.escolha_cadastro, name='escolha_cadastro'),
    path('cadastro/organizador/', views.cadastro_organizador, name='cadastro_organizador'),
    path('cadastro/fornecedor/', views.cadastro_fornecedor, name='cadastro_fornecedor'),
    path('login/', views.login, name='login'),
    path('sair/', views.sair, name='sair'),]