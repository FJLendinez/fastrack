from urllib.parse import unquote, urlparse

from fastapi.testclient import TestClient

from main import app
from pixel.models import PageViewModel, UserModel

client = TestClient(app)


def test_received_js():
    response = client.get('/a.js')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/javascript'


def test_tracker():
    url = "http%3A%2F%2F127.0.0.1%3A8000%2Fdocs%3Futm_source%3Dgoogle%26utm_asdf%3Dtururu%23%2Fpixel%2Fanalyze_a_gif_get"
    h = "626330fc-7b0f-49c6-b120-89611afeabaf"
    s = "5fdb53d1-7895-41bb-885f-bb0359686720"
    t = "fastrack%20-%20Swagger%20UI"
    ref = "google.com%2Fbest"
    request = f"/a.gif?url={url}&ref={ref}&t={t}&s={s}&h={h}"
    response = client.get(request)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/gif'
    pv: PageViewModel = PageViewModel.objects.last()
    assert str(pv.session_uuid) == s
    assert str(pv.history_uuid) == h
    assert pv.title == unquote(t)
    assert pv.url == urlparse(unquote(url)).path
    assert pv.domain == urlparse(unquote(url)).netloc
    assert pv.referrer == unquote(ref)


def test_identifier():
    email = "lendi@fakemail.com"
    h = "626330fc-7b0f-49c6-b120-89611afeabaf"
    request = f"/identify?email={email}&h={h}"
    response = client.get(request)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    user: UserModel = UserModel.objects.last()
    assert str(user.history_uuid) == h
    assert user.email == email
