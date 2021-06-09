import os
import os.path
import importlib
from glob import glob

from nanotools.service.api import BaseHandler
from nanotools.common.logging import logger


_urls = None


def get_web_apis():
    """动态加载所有处理器类"""
    global _urls
    if _urls:
        return _urls

    # 导入所有视图文件
    modules = list()
    file_path = os.path.abspath(__file__)
    dirname = os.path.dirname(file_path)
    view_path = os.path.join(dirname, '../service/api')
    for file in glob(os.path.join(view_path, '*.py')):
        if file.endswith('/__init__.py'):
            continue
        file = os.path.abspath(file)
        logger.debug(f' *   发现视图文件：{file}')
        module_name = os.path.basename(file)[:-3]
        module = importlib.import_module(
            f'nanotools.service.api.{module_name}')
        modules.append(module)
        logger.debug(f' *   搜索模块：{module.__name__}')

    # 验证并加载处理器
    services = list()
    for handle_class in BaseHandler.__subclasses__():
        if hasattr(handle_class, 'url'):
            logger.debug(f' *   发现合法的处理器：{handle_class.__name__}')
            services.append((handle_class.url, handle_class))
    _urls = services
    return services
