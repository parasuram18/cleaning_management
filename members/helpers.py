from members.models import IuMaster
from django.conf import settings
from members.jwt import custom_decode_handler

def get_iu_obj(request):
    try:
        # scheme = request.scheme #META.get('wsgi.url_scheme')
        # host = request.get_host() #.META.get('HTTP_HOST')
        # domain = f'{scheme}://{host}/'
        domain = request.META['HTTP_ORIGIN']
    except:
        domain = settings.DEV_HOST
    try:
        iu_obj = IuMaster.objects.filter(domain_name__icontains=domain).first()
    except:
        iu_obj = None
    return iu_obj

def get_role_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    token = auth_header.split(' ')[1]
    payload = custom_decode_handler(token)

    return payload.get('role')

from django.db import transaction
from contextlib import contextmanager

@contextmanager
def ManualCommit():
    transaction.set_autocommit(False)
    try:
        yield
        transaction.commit()
    except:
        transaction.rollback()
        raise
    finally:
        transaction.set_autocommit(True)
