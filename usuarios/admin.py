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
    list_display = ('user', 'telefone', 'endereco')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('user__date_joined',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('user', 'categoria', 'telefone', 'endereco')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('categoria', 'user__date_joined',)
