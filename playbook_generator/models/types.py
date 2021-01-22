import enum


class PlaybookServiceTypes(enum.Enum):
    NUTANIX = 'nutanix'
    VMWARE = 'vmware'

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)
