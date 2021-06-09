import json
import time
import asyncio
from collections import defaultdict


rps_per_worker = {}
last_reqnumber_per_worker = defaultdict(int)
time_table = dict()


def human_size(n):
    # G
    if n >= (1024*1024*1024):
        return "%.1fG" % (n/(1024*1024*1024))
    # M
    if n >= (1024*1024):
        return "%.1fM" % (n/(1024*1024))
    # K
    if n >= 1024:
        return "%.1fK" % (n/1024)
    return "%d" % n


def reqcount(item):
    return item['requests']


def calc_percent(tot, req):
    if tot == 0:
        return 0.0
    return (100 * float(req)) / float(tot)


async def get_nodes(*cmd, app_name):
    '''get nodes in the cluster'''
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        pods = dict()
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            if not stdout:
                return pods
            try:
                ret = json.loads(stdout)
            except Exception:
                ret = {}
            if ret.get('kind').lower() != 'list':
                return pods
            for item in ret['items']:
                app = item['metadata']['labels'].get('app')
                if app != app_name:
                    continue
                podname = item['metadata']['name']
                ip = item['status']['podIP']
                pods[podname] = ip
        return pods
    except Exception:
        return {}


async def read_stats(ip, name=None, port=5004):
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        js = ''
        while True:
            data = await reader.read(4096)
            if len(data) < 1:
                break
            js += data.decode('utf8', 'ignore')
        writer.close()
        return name, json.loads(js), time.time()
    except Exception:
        return None, {}, time.time()


def handle_data(name, data, ts):
    if not data:
        return {}

    global rps_per_worker, last_reqnumber_per_worker, time_table

    dd = data
    node_tag = node_name(name)
    ret_data = dict(items=list())

    ret_data['header'] = dict(
        pod_name=name,
        cwd=dd['cwd'],
        uid=dd['uid'],
        gid=dd['gid'],
        master_pid=dd['pid'],
    )

    tot = sum([worker['requests'] for worker in dd['workers']])

    last_tot_time = time_table.get(node_tag, time.time())
    dt = ts - last_tot_time
    total_rps = 0
    for worker in dd['workers']:
        wid = worker['id']
        worker_tag = f'{node_tag}:{wid}'
        curr_reqnumber = worker['requests']
        last_reqnumber = last_reqnumber_per_worker[worker_tag]
        rps_per_worker[worker_tag] = (curr_reqnumber - last_reqnumber) / dt
        total_rps += rps_per_worker[worker_tag]
        last_reqnumber_per_worker[worker_tag] = curr_reqnumber

    time_table[node_tag] = ts

    tx = sum([worker['tx'] for worker in dd['workers']])
    ret_data['summary'] = dict(
        uwsgi_version=dd['version'],
        total_requests=tot,
        rps=int(round(total_rps)),
        lq=dd.get('listen_queue', 0),
        tx=tx,
    )

    dd['workers'].sort(key=reqcount, reverse=True)
    for worker in dd['workers']:
        sigs = 0
        wlastspawn = "--:--:--"

        wrunt = worker['running_time']/1000
        if wrunt > 9999999:
            wrunt = f'{wrunt/60000:.4f}min'
        else:
            wrunt = f'{wrunt/1000:.4f}sec'

        if worker['last_spawn']:
            wlastspawn = time.strftime(
                "%H:%M:%S", time.localtime(worker['last_spawn']))

        if 'signals' in worker:
            sigs = worker['signals']

        wid = worker['id']
        worker_tag = f'{node_tag}:{wid}'

        rps = int(round(rps_per_worker[worker_tag]))

        try:
            ret_data['items'].append(dict(
                wid=wid,
                percentage=calc_percent(tot, worker['requests']),
                pid=worker['pid'],
                req=worker['requests'],
                rps=max(rps, 0),
                exc=worker['exceptions'],
                sig=sigs,
                status=worker['status'],
                avg=worker['avg_rt']/1000,
                rss=(worker['rss']),
                vsz=(worker['vsz']),
                tx=(worker['tx']),
                respwn=worker['respawn_count'],
                hc=worker['harakiri_count'],
                runt=wrunt,
                lastspwn=wlastspawn,
            ))
        except Exception:
            pass
    return ret_data


def cluster_name(pod_name):
    parts = pod_name.split('-')
    return '-'.join(parts[:-1])


def node_name(pod_name):
    parts = pod_name.split('-')
    return (parts[-1])


async def query(app_name):
    cmd = [
        '/home/op/.install/bin/kubectl',
        'get', 'pods',
        '--namespace', 'poros', '-o', 'json']
    pods = await get_nodes(*cmd, app_name=app_name)
    aws = [asyncio.create_task(
        read_stats(ip=ip, name=pod)) for pod, ip in pods.items()]
    items = [handle_data(*(await coro)) for coro in asyncio.as_completed(aws)]
    items = list(filter(lambda x: x, items))
    if not items:
        return None

    ret_data = dict()
    reqs = sum([item['summary']['total_requests'] for item in items])
    rps = sum([item['summary']['rps'] for item in items])
    lq = sum([item['summary']['lq'] for item in items])
    tx = human_size(sum([item['summary']['tx'] for item in items]))
    ret_data['uwsgi_version'] = items[0]['summary']['uwsgi_version']
    ret_data['ts'] = int(time.time())
    ret_data['reqs'] = reqs
    ret_data['rps'] = rps
    ret_data['lq'] = lq
    ret_data['tx'] = tx

    cluster = cluster_name(items[0]['header']['pod_name'])
    cwd = items[0]['header']['cwd']
    ret_data['cluster'] = cluster
    ret_data['cwd'] = cwd
    ret_data['nodes'] = len(pods)

    pos = 3
    ret_data['items'] = list()
    for node in items:
        pod_name = node['header']['pod_name']
        node_tag = node_name(pod_name)
        lq = node['summary']['lq']
        for item in node['items']:
            status = item["status"]
            ret_data['items'].append([
                f'{node_tag}:{item["wid"]}',
                lq,
                item["pid"],
                item["req"],
                item["rps"],
                item["exc"],
                item["sig"],
                status,
                f'{item["avg"]/1000:.6f}ms',
                human_size(item["rss"]),
                human_size(item["vsz"]),
                human_size(item["tx"]),
                item["respwn"],
                item["hc"],
                item["runt"],
                item["lastspwn"],
            ])
            pos += 1
    return ret_data


def get_columns():
    return [
        {"text": "wid", "type": "string"},
        {"text": "lq", "type": "number"},
        {"text": "pid", "type": "number"},
        {"text": "rep", "type": "number"},
        {"text": "wrps", "type": "number"},
        {"text": "exc", "type": "number"},
        {"text": "sig", "type": "number"},
        {"text": "status", "type": "string"},
        {"text": "avg", "type": "string"},
        {"text": "rss", "type": "string"},
        {"text": "vsz", "type": "string"},
        {"text": "wtx", "type": "string"},
        {"text": "respwn", "type": "number"},
        {"text": "hc", "type": "number"},
        {"text": "runt", "type": "string"},
        {"text": "lastspwn", "type": "string"},
    ]
