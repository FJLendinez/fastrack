import json
from base64 import b64decode
from json.decoder import JSONDecodeError
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from uuid import uuid4

from django.conf import settings
from django.db.models import F
from fastapi import APIRouter, Request, Response, Header, HTTPException

from pixel.models import PageViewModel, UserModel
from pixel.schemas import PageView

router = APIRouter()

with open('pixel/tracker.js', 'r') as tracker:
    JAVASCRIPT = tracker.read()

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
                  meta: Optional[str], ):
    ip = request.headers.get('x-forwarded-for') \
         or request.headers.get('remote_addr') \
         or request.headers.get('x-real-ip')
    msg = "ok"
    try:
        meta = json.loads(meta)
    except JSONDecodeError:
        meta = None
        msg = "Metadata invalid"
    parsed = urlparse(url)
    page_view = {
        "headers": dict(request.headers),
        "params": dict(request.query_params),
        "referrer": ref or request.headers.get('referer') or '',
        "ip": ip,
        "title": t or '',
        "time_spent": ts or 0,
        "domain": parsed.netloc,
        "url": parsed.path,
        "query": parse_qs(parsed.query),
        "session_uuid": s or '',
        "history_uuid": h or '',
        "metadata": meta
    }
    PageViewModel.objects.create(**page_view)
    return {"msg": msg}


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

    if not UserModel.objects.filter(**user).exists():
        UserModel.objects.create(**user)
    return {"msg": "assigned"}


@router.get('/track', response_model=List[PageView])
async def get_track_of_email(email: str,
                             x_access_key=Header(None)):
    if x_access_key not in settings.PRIVATE_ACCESS_KEYS:
        raise HTTPException(status_code=401, detail="You can not access to this resource")

    queryset = list(PageViewModel.objects.filter(
        history_uuid__in=UserModel.objects.filter(email=email).values_list('history_uuid', flat=True)))
    return queryset