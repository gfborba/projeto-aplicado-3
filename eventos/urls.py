from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('criar-evento/', views.criar_evento, name='criar_evento'),
    path('editar-evento/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('excluir-evento/<int:evento_id>/', views.excluir_evento, name='excluir_evento'),
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    path('evento/<int:evento_id>/perguntar/', views.fazer_pergunta, name='fazer_pergunta'),
    path('pergunta/<int:pergunta_id>/responder/', views.responder_pergunta, name='responder_pergunta'),
    path('fornecedores/', views.todos_fornecedores, name='todos_fornecedores'),
    path('fornecedor/<int:fornecedor_id>/', views.detalhes_fornecedor, name='detalhes_fornecedor'),
    path('fornecedor/<int:fornecedor_id>/avaliar/', views.avaliar_fornecedor, name='avaliar_fornecedor'),
    path('avaliacao/<int:avaliacao_id>/editar/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacao/<int:avaliacao_id>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),
]
   