from nanotools.common.exceptions import ClientError
from nanotools.service.api import BaseHandler, resp
from nanotools.service.controller.test import get_list
from nanotools.tasks.test import proc


class TestHandler1(BaseHandler):
    url = '/api/v1/test'

    @resp()
    async def get(self, *args, **kwargs):
        proc.delay(10, 2)
        return await get_list()


class TestHandler2(BaseHandler):
    url = '/api/v2/test'

    @resp(content_type='text/html; charset=UTF-8')
    async def get(self, *args, **kwargs):
        data = '<html><title>200: Internal Server Error</title>'
        '<body>500: Internal Server Error</body></html>'
        return data


class TestHandler3(BaseHandler):
    url = '/api/v3/test'

    @resp()
    async def get(self, *args, **kwargs):
        raise ClientError(reason='你说什么？', answer='I have no idea.')


class TestHandler4(BaseHandler):
    url = '/api/v4/test'

    @resp()
    async def post(self, *args, **kwargs):
        raise ClientError(answer='I have no idea.')
