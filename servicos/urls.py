from django.urls import path
from . import views

urlpatterns = [
    path('', views.meus_servicos, name='meus_servicos'),
    path('todos/', views.todos_servicos, name='todos_servicos'),
    path('visualizar/<int:servico_id>/', views.visualizar_servico, name='visualizar_servico'),
    path('cadastrar/', views.cadastrar_servico, name='cadastrar_servico'),
    path('<int:servico_id>/', views.detalhes_servico, name='detalhes_servico'),
    path('<int:servico_id>/editar/', views.editar_servico, name='editar_servico'),
    path('<int:servico_id>/adicionar-item/', views.adicionar_item, name='adicionar_item'),
    path('<int:servico_id>/remover-item/<int:item_id>/', views.remover_item, name='remover_item'),
    path('<int:servico_id>/adicionar-tag/', views.adicionar_tag, name='adicionar_tag'),
    path('<int:servico_id>/remover-tag/', views.remover_tag, name='remover_tag'),
    path('solicitar-orcamento/', views.solicitar_orcamento, name='solicitar_orcamento'),
    path('minhas-solicitacoes-organizador/', views.minhas_solicitacoes_organizador, name='minhas_solicitacoes_organizador'),
    path('minhas-solicitacoes-fornecedor/', views.minhas_solicitacoes_fornecedor, name='minhas_solicitacoes_fornecedor'),
    path('detalhes-solicitacao/<int:solicitacao_id>/', views.detalhes_solicitacao, name='detalhes_solicitacao'),
    path('adicionar-mensagem-orcamento/<int:solicitacao_id>/', views.adicionar_mensagem_orcamento, name='adicionar_mensagem_orcamento'),
    path('atualizar-status-orcamento/<int:solicitacao_id>/', views.atualizar_status_orcamento, name='atualizar_status_orcamento'),
]