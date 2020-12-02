worker = 1
threads = 16
keepalive = 5

loglevel = 'error'
errorlog = '/usr/local/var/log/gunicorn/gunicorn-error.log'
accesslog = '/usr/local/var/log/gunicorn/gunicorn-access.log'

bind = ['0.0.0.0:8000']
