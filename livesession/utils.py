import time
from django.conf import settings
from agora_token_builder import RtcTokenBuilder

def generate_agora_token(channel_name, uid, role=1, privilege_expired_ts=None):
    """
    Generate Agora RTC token.
    role: 1 for Publisher, 2 for Subscriber
    uid: 0 to let Agora generate it, or a specific integer
    """
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    
    if not privilege_expired_ts:
        expiration_time_in_seconds = 3600
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expiration_time_in_seconds
        
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, 
        app_certificate, 
        channel_name, 
        uid, 
        role, 
        privilege_expired_ts
    )
    return token
