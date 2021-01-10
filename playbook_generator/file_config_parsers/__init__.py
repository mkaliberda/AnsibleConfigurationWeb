from playbook_generator.models import PlaybookServiceTypes
from .nutanix_parser import NutanixParser
from .vmware_parser import VmWareParser


class ParserFactory:
    """
     This is factory class for Parser of different config files
    """
    PARSE_CLASSES = {
        PlaybookServiceTypes.NUTANIX.value: NutanixParser,
        PlaybookServiceTypes.VMWARE.value: VmWareParser,
    }

    def __init__(self, event_type):
        self.parser_class = self.get_parser_class(event_type=event_type)

    def get_parser_class(self, event_type):
        return self.PARSE_CLASSES.get(event_type, None)
