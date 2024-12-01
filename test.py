from enigma_requests import *

import tomli_w, tomllib

#settings = Settings()
#print(Settings.get().comp_name)
#Settings.update({'check_time': 20})
#print(Settings.get().check_time)

#print(Box.add({'name': 'examplebox', 'identifier': 1, 'config': dump_toml('./example_configs/boxes/examplebox.toml')}))
#print(Box.list())
#print(Box.get('examplebox'))
#print(Box.update('examplebox', {'identifier': 29}))
#print(Box.delete('examplebox'))

#print(enigma_path('inject-report', specific1=2, specific2=1))

print(EnigmaCMD.get_state())