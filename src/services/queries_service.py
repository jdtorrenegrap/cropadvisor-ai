import requests
from src.core.config import Settings
from src.middleware.data_token import TokenUsers

class QueriesService:

    def __init__(self):
        self.settings = Settings()
        self.data_token = TokenUsers()

    def get_reads(self, token):
        username = self.data_token.extract_user_info(token)[1]
        headers = {"Authorization": f"Bearer {token}"}
    
        response = requests.get(f"{self.settings.GET_READS}{username}", headers=headers)
    
        if response.status_code == 200:
            data = response.json()
            if data:
                # Ordenar las lecturas por fecha (descendente) y tomar las últimas 10
                sorted_data = sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
                formatted_data = "**Últimas 10 lecturas de sensores:**\n"
                for i in sorted_data:
                    formatted_data += f"Sensor: {i.get('device_id', 'N/A')}\n"
                    formatted_data += f"Unidad de medida: {i.get('unit_id', 'N/A')}, Valor: {i.get('value', 'N/A')}\n"
                    formatted_data += f"Fecha: {i.get('created_at', 'N/A')}\n"
                return formatted_data.strip()
            else:
                return "No se encontraron lecturas de sensores."
        else:
            return f"Error al obtener lecturas. Código: {response.status_code}, Detalle: {response.text}"
        
    def get_alerts(self, token):
        user_id = self.data_token.extract_user_info(token)[0]
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(f"{self.settings.GET_ALERTS}{user_id}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data: 
                formatted_data = "**Alertas configuradas:**\n"
                for i in data:
                    formatted_data += f"Usuario: {self.data_token.extract_user_info(token)[1]}\n"
                    formatted_data += f"Umbral de Temperatura: {i.get('temperature', 'N/A')}\n"
                    formatted_data += f"Umbral de Humedad del aire: {i.get('air_humidity', 'N/A')}\n"
                    formatted_data += f"Umbral de Humedad del suelo: {i.get('soil_humidity', 'N/A')}\n"
                
                return formatted_data.strip()
            else:
                return "No se encontraron alertas configuradas."
        else:
            return f"Error al obtener alertas. Código: {response.status_code}, Detalle: {response.text}"
    
    def get_alerts_activated(self, token):
        user_id = self.data_token.extract_user_info(token)[0]
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(f"{self.settings.GET_ALERTS_ACTIVATED}{user_id}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data: 
                formatted_data = "**Alertas activadas:**\n"
                for i in data:
                    formatted_data += f"Umbral de Temperatura: {i.get('temperature', 'N/A')}\n"
                    formatted_data += f"Umbral de Humedad del aire: {i.get('air_humidity', 'N/A')}\n"
                    formatted_data += f"Umbral de Humedad del suelo: {i.get('soil_humidity', 'N/A')}\n"
                    formatted_data += f"Numero de alertas activadas: {i.get('alert_config_id', 'N/A')}\n"
                    formatted_data += f"Fecha: {i.get('alert_active_at', 'N/A')}\n"
                
                return formatted_data.strip()
            else:
                return "No se encontraron alertas activadas."
        else:
            return f"Error al obtener alertas. Código: {response.status_code}, Detalle: {response.text}"