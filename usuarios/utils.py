import requests
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def geocodificar_cep(cep):
  
    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning("Google Maps API Key não configurada")
        return None, None
    
    #Limpa o CEP
    cep_limpo = cep.replace('-', '').replace('.', '').strip()
    
    if len(cep_limpo) != 8:
        logger.error(f"CEP inválido: {cep}")
        return None, None
    
    try:
       
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        
        #API do Google Geocoding
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': cep_formatado,
            'key': settings.GOOGLE_MAPS_API_KEY,
            'region': 'br'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            #Pegar a primeira localização encontrada
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