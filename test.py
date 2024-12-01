import tomllib, tomli_w

from enigma_requests import Box

with open('./example_configs/boxes/examplebox.toml', 'rb') as f:
    Box.add(Box(
        name='examplebox',
        identifier=1,
        config=tomli_w.dumps(tomllib.load(f))
    ))

with open('./example_configs/boxes/examplebox2.toml', 'rb') as f:
    Box.add(Box(
        name='examplebox2',
        identifier=2,
        config=tomli_w.dumps(tomllib.load(f))
    ))