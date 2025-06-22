from django.contrib import admin
from .models import EventoAgenda

@admin.register(EventoAgenda)
class EventoAgendaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'data_inicio', 'data_fim', 'prioridade', 'usuario', 'ativo']
    list_filter = ['tipo', 'prioridade', 'ativo', 'data_inicio', 'data_fim']
    search_fields = ['titulo', 'descricao', 'local']
    date_hierarchy = 'data_inicio'
    list_editable = ['ativo', 'prioridade']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tipo', 'prioridade', 'local')
        }),
        ('Datas e Horários', {
            'fields': ('data_inicio', 'data_fim', 'todo_dia')
        }),
        ('Aparência', {
            'fields': ('cor',)
        }),
        ('Relacionamentos', {
            'fields': ('usuario', 'fornecedor', 'organizador', 'evento_relacionado'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'fornecedor', 'organizador', 'evento_relacionado')
