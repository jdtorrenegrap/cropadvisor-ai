from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    GET_READS = os.getenv('endpoint_get_read')
    GET_ALERTS = os.getenv('endpoint_alert_config')
    GET_ALERTS_ACTIVATED = os.getenv('endpoint_alert_activated')
    
    #Redis
    REDIS_HOST = os.getenv('host')
    REDIS_PORT = os.getenv('redis_port')
    REDIS_DECODE = os.getenv('decode_responses')
    REDIS_USER = os.getenv('username')
    REDIS_PASSWORD = os.getenv('password')