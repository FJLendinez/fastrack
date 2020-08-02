from unittest import TestCase
from urllib.parse import unquote, urlparse
from uuid import uuid4

from django.core.management import call_command
from fastapi.testclient import TestClient

from main import app
from pixel.models import PageViewModel, UserModel

client = TestClient(app)


class ASDFTestCase(TestCase):

    def setUp(self) -> None:
        self.email = 'email@indb.com'
        self.history_uuid = uuid4()
        self.user = UserModel.objects.create(email=self.email,
                                             history_uuid=self.history_uuid)

    def tearDown(self) -> None:
        # Hard way to avoid database changes and isolate unit tests
        call_command('flush', verbosity=0, interactive=False)

    def test_received_js(self):
        response = client.get('/a.js')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/javascript')

    def test_tracker(self):
        url = "http%3A%2F%2F127.0.0.1%3A8000%2Fdocs%3Futm_source%3Dgoogle%26utm_asdf%3Dtururu%23%2Fpixel" \
              "%2Fanalyze_a_gif_get"
        h = "626330fc-7b0f-49c6-b120-89611afeabaf"
        s = "5fdb53d1-7895-41bb-885f-bb0359686720"
        t = "fastrack%20-%20Swagger%20UI"
        ref = "google.com%2Fbest"
        ts = 146.24
        request = f"/a.gif?url={url}&ref={ref}&t={t}&s={s}&h={h}&ts={ts}"
        response = client.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        pv: PageViewModel = PageViewModel.objects.last()
        self.assertEqual(str(pv.session_uuid), s)
        self.assertEqual(str(pv.history_uuid),  h)
        self.assertEqual(pv.title, unquote(t))
        self.assertEqual(pv.url, urlparse(unquote(url)).path)
        self.assertEqual(pv.domain, urlparse(unquote(url)).netloc)
        self.assertEqual(pv.referrer, unquote(ref))
        self.assertEqual(pv.time_spent, ts)

    def test_identifier(self):
        email = "lendi@fakemail.com"
        h = "626330fc-7b0f-49c6-b120-89611afeabaf"
        request = f"/identify?email={email}&h={h}"
        response = client.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')
        user: UserModel = UserModel.objects.get(history_uuid=h)
        self.assertEqual(user.email, email)


    def test_assert_identification_is_unique(self):
        email = "lendi2@fakemail.com"
        request = f"/identify?email={email}&h={self.history_uuid}"
        response = client.get(request)
        self.assertEqual(response.status_code, 400)
