import json


class AppException(Exception):
    code = 100000
    reason = '应用程序异常'

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            self.code = kwargs.pop('code')
        if 'reason' in kwargs:
            self.reason = kwargs.pop('reason')
        self.kwargs = kwargs

    def to_dict(self):
        data = dict(
            code=self.code,
            reason=self.reason,
        )
        if self.kwargs:
            data['data'] = self.kwargs
        return data

    def __str__(self):
        data = self.to_dict()
        return json.dumps(data)


class UnimplementedError(AppException):
    code = 100900
    reason = '功能未实现'


class ClientError(AppException):
    code = 400000
    reason = '请求错误'
