from django.urls import path
from . import views

urlpatterns = [
    path('', views.meus_servicos, name='meus_servicos'),
    path('cadastrar/', views.cadastrar_servico, name='cadastrar_servico'),
    path('<int:servico_id>/', views.detalhes_servico, name='detalhes_servico'),
    path('<int:servico_id>/editar/', views.editar_servico, name='editar_servico'),
    path('<int:servico_id>/adicionar-item/', views.adicionar_item, name='adicionar_item'),
    path('<int:servico_id>/remover-item/<int:item_id>/', views.remover_item, name='remover_item'),
]