import sys
import os
import os.path
import json


def load_app_config():
    """加载应用配置"""
    config_file = os.environ.get('NANOTOOLS_CONFIG_FILE')
    if not config_file or not os.path.exists(os.path.realpath(config_file)):
        error_message = '无法读取系统配置'
        print(error_message, file=sys.stderr)
        sys.exit(-1001)
    try:
        print(f'尝试从{config_file}中加载应用配置', flush=True)
        with open(config_file, 'rt') as fin:
            data = json.load(fin)
        return data
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(-1001)


app_config = load_app_config()
