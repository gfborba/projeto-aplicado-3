import requests
from django.conf import settings
from decimal import Decimal
import logging
import math

logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
 
    #Calcula a distância entre dois pontos usando a fórmula de Haversine
    R = 6371  #raio da Terra em km
    
    #Converte para radianos
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    #Diferença nas coordenadas
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    #Fórmula de Haversine
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) *
        math.cos(lat2_rad) *
        math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c  # distância em km

def calcular_distancia_entre_usuarios(usuario1, usuario2):
   
    #Calcula a distância entre dois usuários baseado em suas coordenadas

    if (not usuario1.latitude or not usuario1.longitude or 
        not usuario2.latitude or not usuario2.longitude):
        return None
    
    try:
        distancia = haversine(
            usuario1.latitude, usuario1.longitude,
            usuario2.latitude, usuario2.longitude
        )
        return distancia
    except Exception as e:
        logger.error(f"Erro ao calcular distância: {e}")
        return None

def verificar_cobertura_fornecedor(fornecedor, organizador):
   
    #Verifica se um fornecedor atende um organizador baseado no raio de cobertura
   
    # Se o fornecedor tem cobertura ilimitada, sempre atende
    if fornecedor.tem_cobertura_ilimitada():
        distancia = calcular_distancia_entre_usuarios(fornecedor, organizador)
        return True, distancia
    
    # Calcular distância
    distancia = calcular_distancia_entre_usuarios(fornecedor, organizador)
    
    if distancia is None:
        # Se não conseguir calcular a distância, não atende
        return False, None
    
    # Verificar se está dentro do raio de cobertura
    atende = distancia <= fornecedor.raio_cobertura
    
    return atende, distancia

def geocodificar_cep(cep):
    """
    Converte um CEP em coordenadas de latitude e longitude usando a Google Geocoding API
    
    Args:
        cep (str): CEP no formato 00000-000 ou 00000000
        
    Returns:
        tuple: (latitude, longitude) ou (None, None) se não conseguir geocodificar
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning("Google Maps API Key não configurada")
        return None, None
    
    # Limpar o CEP
    cep_limpo = cep.replace('-', '').replace('.', '').strip()
    
    if len(cep_limpo) != 8:
        logger.error(f"CEP inválido: {cep}")
        return None, None
    
    try:
        # Formatar o CEP para o formato brasileiro
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        
        # URL da API do Google Geocoding
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': cep_formatado,
            'key': settings.GOOGLE_MAPS_API_KEY,
            'region': 'br'  # Priorizar resultados do Brasil
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            # Pegar a primeira localização encontrada
            location = data['results'][0]['geometry']['location']
            latitude = Decimal(str(location['lat']))
            longitude = Decimal(str(location['lng']))
            
            logger.info(f"CEP {cep_formatado} geocodificado: {latitude}, {longitude}")
            return latitude, longitude
        
        elif data['status'] == 'ZERO_RESULTS':
            logger.warning(f"Nenhum resultado encontrado para o CEP: {cep_formatado}")
            return None, None
        
        elif data['status'] == 'REQUEST_DENIED':
            logger.error(f"Acesso negado à API do Google: {data.get('error_message', 'Erro desconhecido')}")
            return None, None
        
        else:
            logger.error(f"Erro na API do Google: {data['status']} - {data.get('error_message', '')}")
            return None, None
            
    except requests.RequestException as e:
        logger.error(f"Erro na requisição para a API do Google: {e}")
        return None, None
    
    except Exception as e:
        logger.error(f"Erro inesperado na geocodificação: {e}")
        return None, None

def atualizar_coordenadas_usuario(usuario):
    """
    Atualiza as coordenadas de um usuário (Organizador ou Fornecedor) baseado no CEP
    
    Args:
        usuario: Instância de Organizador ou Fornecedor
        
    Returns:
        bool: True se as coordenadas foram atualizadas com sucesso
    """
    if not usuario.cep or usuario.cep == 'N/D':
        logger.warning(f"Usuário {usuario.user.username} não possui CEP válido")
        return False
    
    latitude, longitude = geocodificar_cep(usuario.cep)
    
    if latitude is not None and longitude is not None:
        usuario.latitude = latitude
        usuario.longitude = longitude
        usuario.save(update_fields=['latitude', 'longitude'])
        logger.info(f"Coordenadas atualizadas para {usuario.user.username}: {latitude}, {longitude}")
        return True
    else:
        logger.warning(f"Não foi possível geocodificar o CEP {usuario.cep} para {usuario.user.username}")
        return False 