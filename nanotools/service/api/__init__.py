import json

from tornado.web import RequestHandler

from nanotools.common import safe_loads
from nanotools.common.logging import logger
from nanotools.common.config import app_config
from nanotools.common.constants import DEFAULT_CONTENT_TYPE
from nanotools.common.exceptions import AppException


class Result:
    """返回结果"""

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            self.code = kwargs.pop('code')
        if 'status' in kwargs:
            self.status = kwargs.pop('status')
        self.kwargs = kwargs

    def to_dict(self):
        data = dict(
            code=getattr(self, 'code', 0),
            status=getattr(self, 'status', 'ok'),
        )
        if self.kwargs:
            data['data'] = self.kwargs
        return data

    def __str__(self):
        data = self.to_dict()
        return json.dumps(data)


class BaseHandler(RequestHandler):
    """请求处理基类"""

    def __init__(self, *args, **kwargs):
        """装载"""
        super(BaseHandler, self).__init__(*args, **kwargs)

    def set_default_headers(self):
        self.set_header(
            'Access-Control-Allow-Origin',
            app_config['cors']['origin allowed'])
        self.set_header(
            'Access-Control-Allow-Headers',
            app_config['cors']['headers allowed'])
        self.set_header(
            'Access-Control-Allow-Methods',
            app_config['cors']['methods allowed'])

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def initialize(self):
        method = self.request.method
        uri = self.request.uri
        logger.info(f'{method} {uri}')

    def json_body(self):
        return safe_loads(self.request.body)

    def write_json(self, errcode, data=''):
        """
            返回json数据
            TODO 废弃
        """
        self.finish(self.write(str(Result(err_code=errcode, data=data))))

    def get_ip_addr(self):
        """获取客户端IP地址"""
        headers = self.request.headers
        if 'X-Real-Ip' in headers:
            return headers['X-Real-Ip']
        return self.request.remote_ip


def resp(content_type=DEFAULT_CONTENT_TYPE):
    """自动响应"""
    def decorator(func):
        async def wrapper(handler, *args, **kwargs):
            handler.set_status(status_code=200, reason='ok')
            try:
                reply = await func(handler, *args, **kwargs)
                if isinstance(reply, dict):
                    reply = Result(**reply)
            except AppException as e:
                reply = e
            reply_str = str(reply)
            handler.write(reply_str)
            handler.set_header('Content-Type', content_type)
            handler.finish()
        return wrapper
    return decorator


def resp_raw(content_type=DEFAULT_CONTENT_TYPE):
    """自动响应"""
    def decorator(func):
        async def wrapper(handler, *args, **kwargs):
            handler.set_status(status_code=200, reason='ok')
            try:
                reply = await func(handler, *args, **kwargs)
                reply_str = json.dumps(reply)
            except AppException as e:
                reply_str = str(e)
            handler.write(reply_str)
            handler.set_header('Content-Type', content_type)
            handler.finish()
        return wrapper
    return decorator
