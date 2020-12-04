from django.conf import settings
import pandas
import os
import xlrd
import itertools
import re


GROUPED_HEADING = {
    'Cluster Configuration': 'cluster_configuration',
    'Cluster Networking': 'cluster_networking',
    'Block Serial #': 'nodes',
    'Passwords': '',
}


class NutanixParser():
    __wbook = None
    CLUSTER_CONFIGURATION = 'cluster_configuration'
    CLUSTER_NETWORKING = 'cluster_networking'
    NODES = 'nodes'
    VLAN = 'vlan'
    STORAGE = 'storage'
    SMTP = 'smtp'

    GROUPED_HEADING = {
        'Cluster Configuration': CLUSTER_CONFIGURATION,
        'Cluster Networking': CLUSTER_NETWORKING,
        'Block Serial #': NODES,
        'IPMI': NODES,
        'Nutanix VLANs': VLAN,
        'Support and Storage': STORAGE,
        'SMTP & Prism Central': SMTP,
    }

    GROUPED_KEYS = {
        CLUSTER_CONFIGURATION: {
            'Location': 'location',
            'Cluster Name': 'cluster_name',
            'Cluster License': 'cluster_license',
            'Cluster External IP (VIP)': 'cluster_external_ip',
            'Cluster Redundancy Factor': 'redundancy_factor',
            'Acropolis Operating System (AOS) version': 'aos',
            'Hypervisor Version': 'hypervisor_version',
            'Build': 'build',
            'Nutanix Witness Appliance Version': 'witness_appliance_version',
            'Nutanix Witness Appliance IP Address': 'witness_address',
        },
        CLUSTER_NETWORKING: {
            'Controller (CVM) – Subnet Mask': 'cvm_netmask',
            'Controller (CVM) – Default Gateway': 'cvm_gateway',
            'Hypervisor - Subnet Mask': 'hypervisor_netmask',
            'Hypervisor – Default Gateway': 'hypervisor_gateway',
            'IPMI/iDRAC – Subnet Mask': 'ipmi_netmask',
            'IPMI/iDRAC – Default Gateway': 'ipmi_gateway',
            'DNS Servers': 'dns_server',
            'NTP Servers': 'ntp_server',
        },
        NODES: {
            'Block Serial #': 'block_id',
            'Node ID': 'node_position',
            'Hypervisor Host Name (FQDN)': 'hypervisor_hostname',
            'Hypervisor Mgmt IP': 'hypervisor_ip',
            'CVM IP': 'cvm_ip',
            'IPMI IP': 'ipmi_ip',
            'Asset Tag': 'asset_tag',
            'IPMI Username': 'ipmi_user',
            'IPMI Password': 'ipmi_password',
            'IPMI': 'ipmi', #old version
            'Username': 'ipmi_user', #old version
            'Password': 'ipmi_password', #old version
            'IPMI address': 'ipmi_ip', #old version
        },
        VLAN: {
            'CVM/Hypervisor VLAN (Both will reside on same VLAN)': 'vlan_mgmt_and_cvm', #prefix
            'IPMI VLAN': 'vlan_ipmi', #prefix
            'VLAN Name': 'name',
            'VLAN ID': 'id',
            'Gateway': 'gateway',
            'VLAN Tagging?': 'tagging',
        },
        STORAGE: {
            'Pulse Enabled (phone home)': 'pulse_enabled',
            'Storage Pool Name': 'storage_pool_name',
            'Compression': 'storage_compression_enabled',
            'Compression Delay': 'storage_compression_delay',
            'Deduplication': 'storage_deduplication',
            'Container Name(s)': 'storage_container_name',
        },
        SMTP: {
            'SMTP Address': 'smtp_address',
            'Protocol': 'smtp_protocol',
            'Port': 'smtp_port',
            'SMTP Security Mode': 'smtp_security_mode',
            'SMTP Username': 'smtp_username',
            'Password': 'smtp_password',
            'Email Address TO': 'smtp_address_to',
            'Email Address FROM': 'smtp_address_from',
            'PRISM Central Instance IP': 'prism_central_ip',
        }
    }
    """
        hypervisor_iso - This sounds weird but it should be empty. Essentially, we need the JSON to read "hypervisor_iso": {}
        skip_hypervisor - Please default to false and don't pull anything from excel
        nos_package - please default to the value and don't pull anything from excel
        is_imaging - default to true and don't pull anything from excel
        timezone - This can be removed entirely as it's no longer needed
        cluster_init_successful - default to true and don't pull anything from excel
        node1_image_now - default to true and don't pull anything from excel
        node1_hypervisor - please default to kvm and don't pull anything from excel
        node1_ipmi_configure_now - Please default to false and don't pull anything from excel
        node1_is_bare_metal - default to true and don't pull anything from excel
        node2_image_now - default to true and don't pull anything from excel
        node2_hypervisor - please default to kvm and don't pull anything from excel
        node2_ipmi_configure_now - Please default to false and don't pull anything from excel
        node2_is_bare_metal - default to true and don't pull anything from excel
    """
    parsed_data = {
        # Cluster Configuration
        'location': {
            'name': 'Location',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': False,
            'value': '',
        },
        'cluster_name': {
            'name': 'Cluster Name',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': '',
        },
        'cluster_license': {
            'name': 'Cluster License',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': False,
            'value': '',
        },
        'cluster_external_ip': {
            'name': 'Cluster External IP (VIP)',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': '',
        },
        'redundancy_factor': {
            'name': 'Cluster Redundancy Factor',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': '',
        },
        'aos': {
            'name': 'Acropolis Operating System (AOS) version',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': False,
            'value': '',
        },
        'hypervisor_iso': {
            'name': 'Hervisor ISO',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': {},
        },
        'skip_hypervisor': {
            'name': 'Skip Hypervisor',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': False,
        },
        'hypervisor_version': {
            'name': 'Hypervisor Version & Build',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': False,
            'value': '',
        },
        'nos_package': {
            'name': 'Nos Package',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': '/home/nutanix/foundation/nos/nutanix_installer_package-release-euphrates-5.15.3-stable-x86_64.tar.gz',
        },
        'is_imaging': {
            'name': '',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': True,
        },
        'witness_appliance_version': {
            'name': 'Nutanix Witness Appliance Version',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': False,
            'value': '',
        },
        'witness_address': {
            'name': 'Nutanix Witness Appliance IP Address',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': '',
        },
        'cluster_init_successful': {
            'name': 'cluster_init_successful',
            'group': CLUSTER_CONFIGURATION,
            'is_to_playbook': True,
            'value': True,
        },

        # Cluster Networking
        'cvm_netmask': {
            'name': 'Controller (CVM) – Subnet Mask',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'cvm_gateway': {
            'name': 'Controller (CVM) – Default Gateway',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'hypervisor_netmask': {
            'name': 'Hypervisor - Subnet Mask',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'hypervisor_gateway': {
            'name': 'Hypervisor – Default Gateway',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'ipmi_netmask': {
            'name': 'IPMI/iDRAC – Subnet Mask',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'ipmi_gateway': {
            'name': 'IPMI/iDRAC – Default Gateway',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': '',
        },
        'dns_server': {
            'name': 'DNS Servers',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': [],
        },
        'ntp_server': {
            'name': 'NTP Servers',
            'group': CLUSTER_NETWORKING,
            'is_to_playbook': True,
            'value': [],
        },
        'nodes': {
            'group': NODES,
        },
        'vlan_mgmt_and_cvm_name': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_mgmt_and_cvm_id': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_vlan_id'],
        },
        'vlan_mgmt_and_cvm_gateway': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_mgmt_and_cvm_tagging': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_ipmi_id': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_vlan_id'],
        },
        'vlan_ipmi_gateway': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_ipmi_tagging': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'pulse_enabled': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'storage_pool_name': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'storage_compression_enabled': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'storage_compression_delay': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_integer'],
        },
        'storage_deduplication': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'storage_container_name': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'smtp_address': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
        'smtp_protocol': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
        'smtp_port': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_integer'],
        },
        'smtp_username': {
            'group': SMTP,
            'is_to_playbook': False,
            'value': '',
        },
        'smtp_password': {
            'group': SMTP,
            'is_to_playbook': False,
            'value': '',
        },
        'smtp_security_mode': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
        'smtp_address_to': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
        'smtp_address_from': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
        'prism_central_ip': {
            'group': SMTP,
            'is_to_playbook': True,
            'value': '',
        },
    }

    def __init__(self, file_contents=None, file_path=None, index_sheet=0):
        if file_contents:
            self.__wbook = xlrd.open_workbook(file_contents=file_contents)
        else:
            self.__wbook = xlrd.open_workbook(filename=file_path)
        self.sheet = self.__wbook.sheet_by_index(index_sheet)

    def get_grouped_heading(self, row_value):
        return self.GROUPED_HEADING.get(row_value)

    def current_row(self, row_num):
        return self.sheet.row_values(row_num)

    def get_headers(self, row_num, to_group):
        return [self.GROUPED_KEYS[to_group].get(head, '') for head in self.current_row(row_num)]

    def parse_item_config(self, row_num, to_group, value_range=5):
        row_num += 2 # pass heading
        while row_num < self.sheet.nrows:
            item_cell = self.current_row(row_num)[0] if len(self.current_row(row_num)) else None

            if item_cell is None:
                return row_num

            item_cell = re.split(', | & ', item_cell) # some items parsed by , or &

            item_key = None
            for new_item_key, n in itertools.zip_longest(item_cell, range(2, value_range)):
                if new_item_key is not None:
                    item_key = self.GROUPED_KEYS[to_group].get(new_item_key)
                if item_key is None:
                    return row_num
                if self.current_row(row_num)[n] and item_key and self.parsed_data.get(item_key):

                    if type(self.parsed_data.get(item_key)['value']) == list:
                        if self.current_row(row_num)[n] not in self.parsed_data.get(item_key)['value']:
                            self.parsed_data.get(item_key)['value'].append(
                                self.set_formating_data(item_key, self.current_row(row_num)[n])
                            )
                    else:
                        self.parsed_data.get(item_key)['value'] = self.set_formating_data(
                            item_key, self.current_row(row_num)[n]
                        )
            row_num += 1
        return row_num

    def parse_nodes_heading_table(self, row_num, to_group):
        """
            node1_image_now - default to true and don't pull anything from excel
            node1_hypervisor - please default to kvm and don't pull anything from excel
            node1_ipmi_configure_now - Please default to false and don't pull anything from excel
            node1_is_bare_metal - default to true and don't pull anything from excel
        :param row_num:
        :param to_group:
        :return:
        """
        DEFAULT_VALUES = {
            'image_now': True,
            'hypervisor': 'kvm',
            'ipmi_configure_now': False,
            'is_bare_metal': True,
        }
        NODE_KEY = 'ipmi_ip'
        headers = self.get_headers(row_num, to_group)
        row_num += 1
        while row_num < self.sheet.nrows and self.current_row(row_num):
            if not len(self.current_row(row_num)) or not self.current_row(row_num)[0]:
                return row_num
            node_dict = {}
            node_dict.update(DEFAULT_VALUES)
            for inx, value in enumerate(self.current_row(row_num)):
                if headers[inx]:
                    node_dict.update({ headers[inx]: value })
            if node_dict.get(NODE_KEY) not in self.parsed_data[self.NODES]:
                self.parsed_data[self.NODES][node_dict.get(NODE_KEY)] = node_dict
            else:
                self.parsed_data[self.NODES][node_dict.get(NODE_KEY)].update(node_dict)
            row_num += 1
        return row_num

    def parse_prefix_heading_table(self, row_num, to_group):
        headers = self.get_headers(row_num, to_group)
        row_num += 1

        while row_num < self.sheet.nrows and self.current_row(row_num):
            prefix = self.GROUPED_KEYS[to_group].get(
                self.current_row(row_num)[0]
            ) if len(self.current_row(row_num)) else None

            if prefix is None:
                return row_num

            for inx in range(1, len(self.current_row(row_num))):
                if headers[inx] and self.parsed_data.get(f"{prefix}_{headers[inx]}"):
                    value = self.set_formating_data(f"{prefix}_{headers[inx]}", self.current_row(row_num)[inx])
                    self.parsed_data[f"{prefix}_{headers[inx]}"]['value'] = value
            row_num += 1
        return row_num

    def parse_with_type(self, row_num):
        """ parse_with_type
        select method for parse grouped block
        :param row_num:
        :return: row_num:
        """
        grouped_heading = self.get_grouped_heading(self.current_row(row_num)[0])
        if grouped_heading == self.CLUSTER_CONFIGURATION:
            row_num = self.parse_item_config(row_num, grouped_heading)
        if grouped_heading == self.CLUSTER_NETWORKING:
            row_num = self.parse_item_config(row_num, grouped_heading)
        if grouped_heading == self.NODES:
            row_num = self.parse_nodes_heading_table(row_num, grouped_heading)
        if grouped_heading == self.VLAN:
            row_num = self.parse_prefix_heading_table(row_num, grouped_heading)
        if grouped_heading == self.STORAGE:
            row_num = self.parse_item_config(row_num, grouped_heading, 4)
        if grouped_heading == self.SMTP:
            row_num = self.parse_item_config(row_num, grouped_heading, 5)
        return row_num

    def set_formating_data(self, item_key, value):
        data = self.parsed_data.get(item_key)
        if data and data.get('format_methods'):
            for method_key in data.get('format_methods'):
                format_method = self.__getattribute__(method_key)
                if format_method:
                    value = format_method(value)
        return value

    def parse_file(self):
        row_num = 0
        while row_num < self.sheet.nrows:
            if len(self.current_row(row_num)) > 0 and self.get_grouped_heading(self.current_row(row_num)[0]) is not None:
                row_num = self.parse_with_type(row_num)
            else:
                row_num += 1
        # method = self.__getattribute__('format_vlan_id')
        # print(method('CJ (VLAN 102)'))

    def get_yml_dict(self):
        yml_dict = {}

        def format_val(val):
            if type(val) == bool:
                return val
            else:
                return str(val)

        for key, data in self.parsed_data.items():
            value = data.get('value')
            if value and data.get('is_to_playbook'):
                if type(value) == list:
                    for inx, item in enumerate(value):
                        yml_dict.update({
                            f"{key}_{inx + 1}": format_val(item),
                        })
                else:
                    yml_dict.update({
                        key: format_val(value),
                    })
            if key == 'nodes':
                for inx, (node_key, node_obj) in enumerate(data.items()):
                    if node_key == 'group':
                        continue
                    for k, node_val in node_obj.items():
                        yml_dict.update({
                            f"node{inx}_{k}": format_val(node_val),
                        })

        return yml_dict

    @staticmethod
    def format_vlan_id(value):
        return value.split(' ')[-1].replace(')', '')

    @staticmethod
    def format_integer(value):
        return str(int(value))


