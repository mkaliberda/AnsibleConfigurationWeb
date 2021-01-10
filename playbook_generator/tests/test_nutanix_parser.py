from django.conf import settings
from playbook_generator.file_config_parsers import NutanixParser, VmWareParser
from pathlib import Path
from django.test import TestCase



class NutanixParserTestCases(TestCase):
    CLUSTER_CONFIGURATION = 'cluster_configuration'
    CLUSTER_NETWORKING = 'cluster_networking'
    GROUPED_HEADING = {
        'Cluster Configuration': CLUSTER_CONFIGURATION,
        'Cluster Networking': CLUSTER_NETWORKING,
    }

    parsed_data = {
        'location': {'name': 'Location', 'group': 'cluster_configuration', 'is_to_playbook': False,
                     'value': 'Madrid, Spain'},
        'cluster_name': {'name': 'Cluster Name', 'group': 'cluster_configuration', 'is_to_playbook': True,
                         'value': 'es-rom-ahv-crp-c01'},
        'cluster_license': {'name': 'Cluster License', 'group': 'cluster_configuration', 'is_to_playbook': False,
                            'value': ''},
        'cluster_external_ip': {'name': 'Cluster External IP (VIP)', 'group': 'cluster_configuration', 'is_to_playbook': True,
                                'value': '10.215.33.110'},
        'redundancy_factor': {'name': 'Cluster Redundancy Factor', 'group': 'cluster_configuration', 'is_to_playbook': True,
                              'value': 'RF2'},
        'aos': {'name': 'Acropolis Operating System (AOS) version', 'group': 'cluster_configuration', 'is_to_playbook': False,
                'value': '5.15.3 (LTS)'},
        'hypervisor_version': {'name': 'Hypervisor Version & Build', 'group': 'cluster_configuration', 'is_to_playbook': False,
                               'value': 'AHV'},
        'witness_appliance_version': {'name': 'Nutanix Witness Appliance Version', 'group': 'cluster_configuration', 'is_to_playbook': False,
                                      'value': '5.15.3'},
        'witness_address': {'name': 'Nutanix Witness Appliance IP Address', 'group': 'cluster_configuration', 'is_to_playbook': True,
                            'value': '10.195.54.79'},
        'cvm_netmask': {'name': 'Controller (CVM) – Subnet Mask', 'group': 'cluster_networking', 'is_to_playbook': True,
                        'value': '255.255.255.224'},
        'cvm_gateway': {'name': 'Controller (CVM) – Default Gateway', 'group': 'cluster_networking', 'is_to_playbook': True,
                        'value': '10.215.33.97'},
        'hypervisor_netmask': {'name': 'Hypervisor - Subnet Mask', 'group': 'cluster_networking', 'is_to_playbook': True,
                               'value': '255.255.255.224'},
        'hypervisor_gateway': {'name': 'Hypervisor – Default Gateway', 'group': 'cluster_networking', 'is_to_playbook': True,
                               'value': '10.215.33.97'},
        'ipmi_netmask': {'name': 'IPMI/iDRAC – Subnet Mask', 'group': 'cluster_networking', 'is_to_playbook': True,
                         'value': '255.255.255.224'},
        'ipmi_gateway': {'name': 'IPMI/iDRAC – Default Gateway', 'group': 'cluster_networking', 'is_to_playbook': True,
                         'value': '10.215.33.33'},
        'dns_server': {'name': 'DNS Servers', 'group': 'cluster_networking', 'is_to_playbook': True,
                       'value': ['10.195.121.44', '10.198.121.44', '10.150.121.44']},
        'ntp_server': {'name': 'NTP Servers', 'group': 'cluster_networking', 'is_to_playbook': True,
                       'value': ['10.195.121.44', '10.198.121.44', '10.150.121.44']}}


    def test_nutanix_parser(self):
        fin_path = settings.BASE_DIR.joinpath('playbook_generator/tests/files/nutanix1.xlsx')
        parser = NutanixParser(file_path=fin_path)
        parser.parse_file()
        # parser.get_parsed_data()
        # parser.get_yml_dict()
        # print(parser.get_yml_dict())
        # self.assertDictEqual(self.parsed_data, parser.parsed_data)

    def test_vm_ware_parser(self):
        fin_path = settings.BASE_DIR.joinpath('playbook_generator/tests/files/vm_ware.xlsx')
        parser = VmWareParser(file_path=fin_path)
        parser.parse_file()
        # parser.get_parsed_data()
        print(parser.get_yml_dict())
        # parser.get_json_dict()
