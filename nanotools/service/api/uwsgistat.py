from nanotools.service.api import BaseHandler, resp_raw
from nanotools.service.controller import uwsgistats


class UWSGIStat(BaseHandler):
    """Grafana uWSGI stat 请求入口"""

    url = '/api/v1/uwsgistat'

    @resp_raw()
    async def get(self, *args, **kwargs):
        return {}


class UWSGIStatSearch(BaseHandler):
    """Grafana uWSGI stat search入口"""

    url = '/api/v1/uwsgistat/search'

    @resp_raw()
    async def post(self, *args, **kwargs):
        return []


class UWSGIStatQuery(BaseHandler):
    """Grafana uWSGI stat query入口"""

    url = '/api/v1/uwsgistat/query'

    @resp_raw()
    async def post(self, *args, **kwargs):
        request_data = self.json_body()
        targets = request_data.get('targets', [])
        if not targets:
            return []
        target = targets[0]
        params = target.get('data', {})
        app_name = None
        if isinstance(params, dict):
            app_name = params.get('app_name', None)
        cols = uwsgistats.get_columns()
        data = await uwsgistats.query(
            app_name) if app_name else dict(items=[])
        ret_data = [{
            "type": "table",
            "columns": cols,
            "rows": sorted(data['items']),
        }]
        return ret_data
