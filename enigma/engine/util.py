from enigma.models.box import Box

# Performs get_service_names() for every box in the list
def full_service_list(cls, boxes: list):
    services = list()
    for box in boxes:
        for service in box.services:
            services.append(f'{box.name}.{service.name}')
    return services