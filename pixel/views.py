import json
from base64 import b64decode
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from uuid import uuid4

from django.conf import settings
from django.db.models import Max, Count, Min, Avg, Sum, Q
from fastapi import APIRouter, Request, Response, Header, HTTPException, Depends
from starlette.responses import JSONResponse

from pixel.models import PageViewModel, UserModel
from pixel.schemas import PageView

router = APIRouter()

with open('pixel/tracker.js', 'r') as tracker:
    JAVASCRIPT = tracker.read()

PIXEL = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')
page_view_fields = [field.name for field in PageViewModel._meta.fields]


@router.get('/a.gif')
async def analyze(request: Request,
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

    path = parsed.path[:250]
    if path.endswith('/'):
        path = path[:-1]

    if parsed.netloc not in settings.FASTRACK_ALLOWED_HOSTS:
        return JSONResponse({"msg": "Invalid host"}, status_code=400)

    page_view = {
        "headers": dict(request.headers),
        "params": dict(request.query_params),
        "referrer": (ref or request.headers.get('referer') or '')[:255],
        "ip": ip,
        "title": (t or '')[:200],
        "time_spent": ts or 0,
        "domain": parsed.netloc,
        "url": path,
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


def have_access_key(x_access_key=Header(None)):
    if x_access_key not in settings.PRIVATE_ACCESS_KEYS:
        raise HTTPException(status_code=401, detail="You can not access to this resource")
    return x_access_key


def page_view_filters(request: Request):
    filters = []
    for k, v in request.query_params.items():
        if k in page_view_fields:
            filters.append(Q(**{k: v}))
        if "__" in k and k.split('__')[0] in page_view_fields:
            if k.split('__')[1] == 'isnull':
                filters.append(Q(**{k: v == 'true'}))
            else:
                filters.append(Q(**{k: v}))
    return filters


@router.get('/track', response_model=List[PageView])
async def get_track_of_email(email: str,
                             timestamp: datetime = None,
                             filters=Depends(page_view_filters),
                             x_access_key=Depends(have_access_key)):
    queryset = PageViewModel.objects.filter(
        history_uuid__in=UserModel.objects.filter(email=email).values_list('history_uuid', flat=True)).filter(*filters)
    if timestamp:
        queryset = queryset.filter(timestamp__gte=timestamp)
    return list(queryset)


@router.get('/analytics')
async def analytics(request: Request,
                    groupby: str = "id",
                    operations: str = "count",
                    operation_value: str = "id",
                    filters=Depends(page_view_filters),
                    x_access_key=Depends(have_access_key)):
    """
    This endpoint automatically calculate the operations max, min, count and avg
    of a value, grouped by a selected field.
    Each combination of operator and values are cached during ANALYTICS_CACHE seconds.
    In certain cases this could be better than get an endpoint with all the needed queries collected.
    Params:
      *  operation (default count)
      *  operation_value: field to apply the operator (default id)
      *  groupby: field to group (default id)
      *  [...] All the filters added automatically by model
    Return:
      A collection of dictionaries that follows this format
      {'field_grouped': 'field_grouped_value', <operator>: <operator value>}
    """
    operators = {'max': Max, 'count': Count, 'min': Min, 'avg': Avg, 'sum': Sum}

    queryset = PageViewModel.objects.all().filter(*filters)
    if groupby not in page_view_fields:
        raise HTTPException(status_code=400,
                            detail=f"You can group by {groupby}, try with one of this {page_view_fields}")

    queryset = queryset.order_by(groupby).values(groupby)

    if operation_value not in page_view_fields:
        raise HTTPException(status_code=400,
                            detail=f"You can operate with {operation_value}, try with one of this {page_view_fields}")

    operation_names = operations.split(',')

    annotations = dict(
        (operation_name, operators.get(operation_name, Count)(operation_value)) for operation_name in
        operation_names)

    queryset = queryset.annotate(**annotations)
    return list(queryset.values(groupby, *operation_names))
