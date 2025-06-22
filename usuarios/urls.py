from django.urls import path
from . import views

urlpatterns = [
    path('', views.escolha_cadastro, name='escolha_cadastro'),
    path('cadastro/organizador/', views.cadastro_organizador, name='cadastro_organizador'),
    path('cadastro/fornecedor/', views.cadastro_fornecedor, name='cadastro_fornecedor'),
    path('login/', views.login, name='login'),
    path('sair/', views.sair, name='sair'),
    path('buscar-cep/', views.buscar_cep, name='buscar_cep'),
    path('configurar-raio-cobertura/', views.configurar_raio_cobertura, name='configurar_raio_cobertura'),
]