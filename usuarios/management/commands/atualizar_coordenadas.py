from django.core.management.base import BaseCommand
from django.conf import settings
from usuarios.models import Organizador, Fornecedor
from usuarios.utils import atualizar_coordenadas_usuario
import time

class Command(BaseCommand):
    help = 'Atualiza as coordenadas de latitude e longitude para todos os usuários baseado em seus CEPs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['organizadores', 'fornecedores', 'todos'],
            default='todos',
            help='Tipo de usuário para atualizar (organizadores, fornecedores, todos)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay entre requisições em segundos (padrão: 1.0)'
        )

    def handle(self, *args, **options):
        if not settings.GOOGLE_MAPS_API_KEY:
            self.stdout.write(
                self.style.ERROR('Google Maps API Key não configurada. Configure a variável GOOGLE_MAPS_API_KEY no arquivo .env')
            )
            return

        tipo = options['tipo']
        delay = options['delay']
        
        self.stdout.write(f"Iniciando atualização de coordenadas para: {tipo}")
        
        total_atualizados = 0
        total_erros = 0
        
        if tipo in ['organizadores', 'todos']:
            organizadores = Organizador.objects.filter(cep__isnull=False).exclude(cep='N/D')
            self.stdout.write(f"Processando {organizadores.count()} organizadores...")
            
            for organizador in organizadores:
                try:
                    if atualizar_coordenadas_usuario(organizador):
                        total_atualizados += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Organizador {organizador.user.username}: {organizador.latitude}, {organizador.longitude}")
                        )
                    else:
                        total_erros += 1
                        self.stdout.write(
                            self.style.WARNING(f"✗ Organizador {organizador.user.username}: CEP não geocodificado")
                        )
                    
                    time.sleep(delay)  # Delay para não sobrecarregar a API
                    
                except Exception as e:
                    total_erros += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Erro ao processar organizador {organizador.user.username}: {e}")
                    )
        
        if tipo in ['fornecedores', 'todos']:
            fornecedores = Fornecedor.objects.filter(cep__isnull=False).exclude(cep='N/D')
            self.stdout.write(f"Processando {fornecedores.count()} fornecedores...")
            
            for fornecedor in fornecedores:
                try:
                    if atualizar_coordenadas_usuario(fornecedor):
                        total_atualizados += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Fornecedor {fornecedor.user.username}: {fornecedor.latitude}, {fornecedor.longitude}")
                        )
                    else:
                        total_erros += 1
                        self.stdout.write(
                            self.style.WARNING(f"✗ Fornecedor {fornecedor.user.username}: CEP não geocodificado")
                        )
                    
                    time.sleep(delay)  # Delay para não sobrecarregar a API
                    
                except Exception as e:
                    total_erros += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Erro ao processar fornecedor {fornecedor.user.username}: {e}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nProcesso concluído!\n"
                f"Total atualizados: {total_atualizados}\n"
                f"Total com erro: {total_erros}"
            )
        ) 