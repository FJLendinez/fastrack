from base64 import b64decode
from typing import Optional
from urllib.parse import urlparse, parse_qs
from uuid import uuid4

from django.conf import settings
from fastapi import APIRouter, Request, Response, Header, HTTPException

from pixel.models import PageViewModel, UserModel
from pixel.schemas import TestSchema

router = APIRouter()

JAVASCRIPT = """
    var fastrack_start = new Date();
    
    function httpGetAsync(theUrl)
    {{
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open("GET", theUrl, true); 
        xmlHttp.send(null);
    }}

    function fastrack_identify(email) {{
    var e=encodeURIComponent;
    var h = localStorage.getItem('h');
    if (!h) {{ return false }};
    httpGetAsync('{domain}/identify?email='+e(email)+'&h='+h);
    }}
    function fastrack_trackview(){{
        try {{
        var time_spent = (new Date() - fastrack_start) / 1000;
        
        var h = localStorage.getItem('h');
        if (!h) {{ localStorage.setItem('h', '{history_uuid}') }};
        h = localStorage.getItem('h');

        var s = sessionStorage.getItem('s');
        if (!s) {{ sessionStorage.setItem('s','{session_uuid}') }};
        s = sessionStorage.getItem('s');
        var d=document, e=encodeURIComponent;
        httpGetAsync('{domain}/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&s='+e(s)+'&h='+e(h)+'&ts='+(time_spent));
        }} catch(error) {{localStorage.setItem('error', error.message)}}
    }};
    window.addEventListener('beforeunload', fastrack_trackview);""".replace('\n', '')

PIXEL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


@router.get('/a.gif')
async def analyze(request: Request,
                  response: Response,
                  url: str,
                  t: Optional[str],
                  ts: Optional[float],
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
        "time_spent": ts or 0,
        "domain": parsed.netloc,
        "url": parsed.path,
        "query": parse_qs(parsed.query),
        "session_uuid": s or '',
        "history_uuid": h or '',
    }
    PageViewModel.objects.create(**page_view)
    return {"msg": "ok"}


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

    if UserModel.objects.filter(history_uuid=h).exclude(email=email).exists():
        raise HTTPException(status_code=400, detail="Identifier previously assigned to another user")

    if not UserModel.objects.filter(history_uuid=h, email=email).exists():
        UserModel.objects.create(**user)
    return {"msg": "assigned"}


@router.get('/test', response_model=TestSchema)
async def identify():
    return UserModel.objects.last()
