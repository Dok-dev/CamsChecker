sqlUser = 'reader'
sqlPass = 'XXXXXXXX'

winCredentials = [
    {
        'user': 'DOMAIN1\admin',
        'password': 'XXXXXXXX',
    },
    {
        'user': 'DOMAIN2\installer ',
        'password': 'XXXXXXXX',
    }
]

servers = [
    {
        'name': 'police3',
        'url': 'police3.domain1',
        'path': r'\\police3.domain1\e$\storage'
    },
    {
        'name': 'police2',
        'url': '172.19.2.2',
        'path': r'\\172.19.2.2\e$\storage'
    },
    {
        'name': 'police4',
        'url': '172.19.4.4',
        'path': r'\\172.19.4.4\d$\storage'
    },
    {
        'name': 'police6',
        'url': '172.19.6.6',
        'path': r'\\172.19.6.6\e$\storage'
    },
    {
        'name': 'police5',
        'url': '172.19.5.5',
        'path': r'\\172.19.5.5\e$\storage'
    },
    {
        'name': 'police1',
        'url': 'police1.domain1',
        'path': r'\\police1.domain1\d$\storage'
    }
]

to_addr = 'admin@domain.ru'
from_addr = 'mail_allert@domain.ru'
SMTPrelay = 'relay.domain1.ru'
port = 25
