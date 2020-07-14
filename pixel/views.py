from base64 import b64decode
from typing import Optional
from urllib.parse import urlparse, parse_qs
from uuid import uuid4

from django.conf import settings
from fastapi import APIRouter, Request, Response, Header

from pixel.models import PageViewModel, UserModel

router = APIRouter()

JAVASCRIPT = """
    function fastrack_identify(email) {{
    var e=encodeURIComponent;
    var h = localStorage.getItem('h');
    if (!h) {{ return false }};
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='{domain}/identify?email='+e(email)+'&h='+h;
    }}
    (function(){{
    var h = localStorage.getItem('h');
    if (!h) {{ localStorage.setItem('h', '{history_uuid}') }};
    h = localStorage.getItem('h');

    var s = sessionStorage.getItem('s');
    if (!s) {{ sessionStorage.setItem('s','{session_uuid}') }};
    s = sessionStorage.getItem('s');
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='{domain}/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&s='+e(s)+'&h='+e(h);
    }})()""".replace('\n', '')

PIXEL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


@router.get('/a.gif')
async def analyze(request: Request,
                  response: Response,
                  url: str,
                  t: Optional[str],
                  s: Optional[str],
                  h: Optional[str],
                  ref: Optional[str],
                  referer: Optional[str] = Header(None)):
    ip = request.headers.get('HTTP_X_FORWARDED_FOR', request.headers.get('REMOTE_ADDR', ''))
    parsed = urlparse(url)
    page_view = {
        "headers": dict(request.headers),
        "params": dict(request.query_params),
        "referrer": referer or ref or '',
        "ip": ip,
        "title": t or '',
        "domain": parsed.netloc,
        "url": parsed.path,
        "query": parse_qs(parsed.query),
        "session_uuid": s or '',
        "history_uuid": h or '',
    }
    PageViewModel.objects.create(**page_view)
    response.headers['Cache-Control'] = 'private, no-cache'
    return Response(content=PIXEL, media_type='image/gif')


@router.get('/a.js')
async def script():
    return Response(content=JAVASCRIPT.format(domain=settings.DOMAIN,
                                              history_uuid=uuid4(),
                                              session_uuid=uuid4()),
                    media_type="application/javascript")


@router.get('/identify')
async def identify(email: str,
                   h: str):
    user = {
        "email": email,
        "history_uuid": h,
    }
    UserModel.objects.create(**user)
    return {"msg": "assigned"}
