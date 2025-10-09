from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    GET_READS = os.getenv('ENDPOINT_GET_READ')
    GET_ALERTS = os.getenv('ENDPOINT_ALERT_CONFIG')
    GET_ALERTS_ACTIVATED = os.getenv('ENDPOINT_ALERT_ACTIVATED')

    #Redis
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_HOST = os.getenv('HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DECODE = os.getenv('DECODE_RESPONSES')
    REDIS_USER = os.getenv('USERNAME')
    REDIS_PASSWORD = os.getenv('PASSWORD')
