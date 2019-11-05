"""
Helper functions
"""

import re
from random import randint

PHONE_REGEX = re.compile(r'^(0|\+98)?9\d{9}$')
PERCENTLIMIT = 70

USE_KAVE_NEGAR = True

def jwt_encode(dic):
    """Encode a dic into a JWT"""
    return jwt.encode(dic, settings.JWT_SECRET, algorithm='HS256', headers={})

def jwt_decode(inp):
    """Decode a JWT into a dic"""
    try:
        return jwt.decode(inp, settings.JWT_SECRET, algorithm='HS256')
    except:
        raise PermissionDenied()

def jwt_auth(request):
    """Decode a request object's JWT"""
    user_jwt = None
    if 'HTTP_Authorization' in request.META:
        user_jwt = request.META['HTTP_Authorization']
    elif 'HTTP_AUTHORIZATION' in request.META:
        user_jwt = request.META['HTTP_AUTHORIZATION']
    else:
        raise PermissionDenied()
    if user_jwt.startswith('Bearer '):
        user_jwt = user_jwt[7:]
        return jwt_decode(user_jwt)
    raise PermissionDenied()


def send_sms(phone, key):
    """Sends a verification sms to phone number"""
    req = requests.post(
        'https://api.kavenegar.com/v1/%s/verify/lookup.json'%(settings.KAVENEGAR_API),
        {'token': key, 'receptor': phone, 'template': 'verify', 'type': 'sms'}
    )
    req.json()

def send_call(phone, key):
    """Sends a verification call to phone number"""
    req = requests.post(
        'https://api.kavenegar.com/v1/%s/verify/lookup.json'%(settings.KAVENEGAR_API),
        {'token': key, 'receptor': phone, 'template': 'verify', 'type': 'call'}
    )
    req.json()

def set_cache(key, value, timeout=600):
    """Set an item in cache"""
    cache.set(key, value, timeout)

def get_cache(key):
    """Get an item from cache"""
    return cache.get(key)

def del_cache(key):
    """Delete a value from cache"""
    return cache.delete(key)

def get_verification_code():
    """Generate a random verification code"""
    return ''.join(['%s' % randint(0, 9) for i in range(4)])

def send_msg(phone):
    """Set a password and send it to user"""
    val = get_cache('u'+phone)
    if val:
        set_cache('u'+phone, val) # Reset
        if USE_KAVE_NEGAR:
            send_call(phone, val)
        else:
            print(phone, '  ', val) #DEBUG
    else:
        val = get_verification_code()
        set_cache('u'+phone, val)
        if USE_KAVE_NEGAR:
            send_sms(phone, val)
        else:
            print(phone, '  ', val) #DEBUG

def check_phone(phone):
    if not PHONE_REGEX.match(phone):
        raise ValidationError
    if phone[0] == '+':
        return '0' + phone[3:]
    elif phone[0] == '9':
        return '0' + phone
    return phone

def coach_stats(coach):
    items = Item.objects.filter(coach=coach).order_by('id')
    play = Played.objects.filter(item__in=items, percent__gte= PERCENTLIMIT).count()
    like_c = Feedback.objects.filter(item__in=items).count()
    like = Feedback.objects.filter(item__in=items, liked = True).count()
    return {"play": play, "like": like, "dislike": like_c - like}

def coach_points(coach):
    pass
    return {"points": 0}

def coach_pay(coach):
    pass
    return {"pay": 0}

def package_pay(package):
    pass
    return {"url": "https://google.com"}
