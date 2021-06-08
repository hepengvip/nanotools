# 脚本示例
import sys


def entrance():
    ver = sys.version_info

    print(f'hello Py-{ver.major}.{ver.minor}.{ver.micro}')
    print('Args:', sys.argv)


if __name__ == '__main__':
    entrance()
