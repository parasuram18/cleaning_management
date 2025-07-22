from members.models import IuMaster
from django.conf import settings
from members.jwt import custom_decode_handler

def get_iu_obj(request):
    try:
        scheme = request.META.get('wsgi.url_scheme')
        host = request.META.get('HTTP_HOST')
        domain = f'{scheme}://{host}/'
    except:
        domain = settings.DEV_HOST
    domain = settings.DEV_HOST
    iu_obj = IuMaster.objects.get(domain_name=domain)

    return iu_obj

def get_role_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    token = auth_header.split(' ')[1]
    payload = custom_decode_handler(token)

    return payload.get('role')