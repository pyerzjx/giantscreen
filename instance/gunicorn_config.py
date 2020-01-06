## server mechanics
chdir = '/usr/local/giantscreen'
pidfile = '%s/gunicorn.pid'%chdir
pythonpath = '/usr/local/python3/bin'

## server socket
bind = '127.0.0.1:844'
backlog = 1024

## worker 进程
workers = 5
worker_class = 'utils.websocket_util.worker'

# worker_connections = 1000
max_requests = 5000
max_requests_jitter = 1000
keepalive = 60

## security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 5120

## debugging
reload = True

## process naming
# proc_name = 'websocket_server'

## server hooks

