from base64 import b64decode
from typing import Optional
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
from fastapi import FastAPI, Request, Header
from fastapi.responses import Response

from db import database, pageviews, users
from env import DOMAIN, PROTOCOL

app = FastAPI()

JAVASCRIPT = """
    function fastrack_identify(email) {{
    var e=encodeURIComponent;
    var h = localStorage.getItem('h');
    if (!h) {{ return false }};
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='{protocol}://{domain}/identify?email='+e(email)+'&h='+h;
    }}
    (function(){{
    var h = localStorage.getItem('h');
    if (!h) {{ localStorage.setItem('h', '{history_uuid}') }};
    h = localStorage.getItem('h');

    var s = sessionStorage.getItem('s');
    if (!s) {{ sessionStorage.setItem('s','{session_uuid}') }};
    s = sessionStorage.getItem('s');
    var d=document,i=new Image,e=encodeURIComponent;
    i.src='{protocol}://{domain}/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title)+'&s='+e(s)+'&h='+e(h);
    }})()""".replace('\n', '')

BEACON = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


@app.get('/a.gif')
async def analyze(request: Request,
                  response: Response,
                  url: str,
                  t: Optional[str],
                  s: Optional[str],
                  h: Optional[str],
                  referer=Header(None),
                  x_forwarder_for=Header(None)):
    parsed = urlparse(url)
    page_view = {
        "headers": dict(request.headers),
        "params": dict(request.query_params),
        "referrer": referer or '',
        "ip": x_forwarder_for,
        "title": t or '',
        "domain": parsed.netloc,
        "url": parsed.path,
        "query": parse_qs(parsed.query),
        "session_uuid": s or '',
        "history_uuid": h or '',
    }
    query = pageviews.insert().values(**page_view)
    await database.execute(query)
    response.headers['Cache-Control'] = 'private, no-cache'
    return Response(content=BEACON, media_type='image/gif')


@app.get('/a.js')
async def script():
    return Response(content=JAVASCRIPT.format(domain=DOMAIN,
                                              protocol=PROTOCOL,
                                              history_uuid=uuid4(),
                                              session_uuid=uuid4()),
                    media_type="application/javascript")


@app.get('/identify')
async def analyze(email: str,
                  h: str):
    user = {
        "email": email,
        "history_uuid": h,
    }
    query = users.insert().values(**user)
    await database.execute(query)
    return {"msg": "assigned"}
