from django.urls import path
from . import views

urlpatterns = [
    path('', views.agenda_view, name='agenda'),
    path('eventos/', views.eventos_json, name='eventos_json'),
    path('eventos-miniatura/', views.eventos_miniatura, name='eventos_miniatura'),
    path('evento/criar/', views.criar_evento, name='criar_evento'),
    path('evento/<int:evento_id>/atualizar/', views.atualizar_evento, name='atualizar_evento'),
    path('evento/<int:evento_id>/deletar/', views.deletar_evento, name='deletar_evento'),
    path('evento/<int:evento_id>/detalhes/', views.detalhes_evento, name='detalhes_evento'),
]
