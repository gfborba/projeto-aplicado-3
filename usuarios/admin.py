from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Organizador, Fornecedor

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def tipo_usuario(self, obj):
        #Retorna tipo de usuário no admin (organizador, fornecedor ou sem perfil para testes)
        try:
            organizador = Organizador.objects.get(user=obj)
            return f"Organizador"
        except Organizador.DoesNotExist:
            try:
                fornecedor = Fornecedor.objects.get(user=obj)
                return f"Fornecedor ({fornecedor.get_categoria_display()})"
            except Fornecedor.DoesNotExist:
                return "Sem perfil"
    
    tipo_usuario.short_description = 'Tipo de Usuário'
    tipo_usuario.admin_order_field = 'username'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Organizador)
class OrganizadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'cidade_display', 'estado_display', 'telefone_display', 'endereco_completo_display')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'cidade', 'bairro')
    list_filter = ('estado', 'user__date_joined')
    
    def cidade_display(self, obj):
        return obj.cidade if obj.cidade != 'N/D' else 'Não informado'
    cidade_display.short_description = 'Cidade'
    
    def estado_display(self, obj):
        return obj.estado if obj.estado != 'N/D' else 'Não informado'
    estado_display.short_description = 'Estado'
    
    def telefone_display(self, obj):
        return obj.telefone if obj.telefone != 'N/D' else 'Não informado'
    telefone_display.short_description = 'Telefone'
    
    def endereco_completo_display(self, obj):
        if obj.cep == 'N/D':
            return 'Endereço não informado'
        return obj.endereco_completo()
    endereco_completo_display.short_description = 'Endereço Completo'

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('user', 'categoria', 'cidade_display', 'estado_display', 'telefone_display', 'endereco_completo_display')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'cidade', 'bairro')
    list_filter = ('categoria', 'estado', 'user__date_joined')
    
    def cidade_display(self, obj):
        return obj.cidade if obj.cidade != 'N/D' else 'Não informado'
    cidade_display.short_description = 'Cidade'
    
    def estado_display(self, obj):
        return obj.estado if obj.estado != 'N/D' else 'Não informado'
    estado_display.short_description = 'Estado'
    
    def telefone_display(self, obj):
        return obj.telefone if obj.telefone != 'N/D' else 'Não informado'
    telefone_display.short_description = 'Telefone'
    
    def endereco_completo_display(self, obj):
        if obj.cep == 'N/D':
            return 'Endereço não informado'
        return obj.endereco_completo()
    endereco_completo_display.short_description = 'Endereço Completo'
