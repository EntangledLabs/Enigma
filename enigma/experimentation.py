from engine.util import Box
from engine.checks import Service, SSHService, HTTPService, HTTPSService

import tomli_w, tomllib

with open('./boxes/examplebox.toml', 'rb') as f:
    box = Box.new('examplebox', tomli_w.dumps(tomllib.load(f)))

another_box = Box('examplebox', 1, [
    SSHService(['examplecreds'], 22, ['plaintext', 'pubkey'], ''),
    HTTPService(80, ''),
    HTTPSService(443, '')
])

print(box == another_box)