from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('criar-evento/', views.criar_evento, name='criar_evento'),
    path('editar-evento/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('excluir-evento/<int:evento_id>/', views.excluir_evento, name='excluir_evento'),
]
   