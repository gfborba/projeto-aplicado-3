from django.urls import path
from . import views

urlpatterns = [
    path('', views.agenda_view, name='agenda'),
    path('compromissos/', views.eventos_json, name='eventos_json'),
    path('compromissos-miniatura/', views.eventos_miniatura, name='eventos_miniatura'),
    path('compromisso/criar/', views.criar_compromisso, name='criar_compromisso'),
    path('compromisso/<int:evento_id>/atualizar/', views.atualizar_compromisso, name='atualizar_compromisso'),
    path('compromisso/<int:evento_id>/deletar/', views.deletar_compromisso, name='deletar_compromisso'),
    path('compromisso/<int:evento_id>/detalhes/', views.detalhes_compromisso, name='detalhes_compromisso'),
]
