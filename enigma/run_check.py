import sys

from enigma import possible_services
from enigma.broker import RabbitMQ

# run_check.py SERVICE ADDR [OPTIONS]
# -p, --port    Assigns a custom port
# -a, --auth    Auth methods
# -k, --keyfile Keyfile
# -c, --creds   Creds to use
# -P, --path    Path to check
if __name__ == '__main__':
    full_service_name = sys.argv[1]

    team = int(sys.argv[2].split('.')[2])
    addr = sys.argv[2]
    args = {}
    for i in [opt for opt in range(3, len(sys.argv)) if opt % 2 == 1]:
        arg = sys.argv[i]
        opt = sys.argv[i + 1]

        while arg.startswith('-'):
            arg = arg[1:]

        match arg:
            case 'p' | 'port':
                args['port'] = opt
            case 'a' | 'auth':
                args['auth'] = opt
            case 'k' | 'keyfile':
                args['keyfile'] = opt
            case 'c' | 'creds':
                args['creds'] = opt
            case 'P' | 'path':
                args['path'] = opt
            case _:
                pass

    service = possible_services[sys.argv[1].split('.')[1]].new(args)
    result = service.conduct_service_check(addr=addr)

    with RabbitMQ() as rabbit:
        message = f'{team}|{full_service_name}|{result[1]}'
        if result[0]:
            rabbit.channel.basic_publish(
                exchange='enigma',
                routing_key='enigma.engine.results',
                body=message
            )