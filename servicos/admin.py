from django.contrib import admin
from .models import Servico, Item, ImagemServico

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fornecedor', 'categoria_fornecedor', 'total_itens_display', 'tem_imagens_display', 'tags_display', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao', 'fornecedor__categoria')
    search_fields = ('nome', 'descricao', 'tags', 'fornecedor__user__first_name', 'fornecedor__user__last_name')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def categoria_fornecedor(self, obj):
        return obj.fornecedor.get_categoria_display()
    categoria_fornecedor.short_description = 'Categoria do Fornecedor'
    
    def total_itens_display(self, obj):
        return obj.total_itens()
    total_itens_display.short_description = 'Total de Itens'
    
    def tem_imagens_display(self, obj):
        return "Sim" if obj.tem_imagens() else "Não"
    tem_imagens_display.short_description = 'Tem Imagens'
    
    def tags_display(self, obj):
        tags = obj.get_tags_list()
        return ', '.join(tags[:3]) + ('...' if len(tags) > 3 else '') if tags else '-'
    tags_display.short_description = 'Tags'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'servico', 'tem_imagem_display', 'data_criacao')
    list_filter = ('data_criacao', 'servico__fornecedor__categoria')
    search_fields = ('nome', 'descricao', 'servico__nome')
    readonly_fields = ('data_criacao',)
    
    def tem_imagem_display(self, obj):
        return "Sim" if obj.imagem else "Não"
    tem_imagem_display.short_description = 'Tem Imagem'

@admin.register(ImagemServico)
class ImagemServicoAdmin(admin.ModelAdmin):
    list_display = ('servico', 'legenda', 'data_upload')
    list_filter = ('data_upload', 'servico__fornecedor__categoria')
    search_fields = ('legenda', 'servico__nome')
    readonly_fields = ('data_upload',)
