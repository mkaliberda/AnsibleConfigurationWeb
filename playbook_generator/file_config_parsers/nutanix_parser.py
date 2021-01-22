from django.conf import settings
import os
import xlrd
import itertools
import re
from playbook_generator.models import StaticVarsValue, PlaybookServiceTypes

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
    USER_VLAN = 'uesr_vlan'
    STORAGE = 'storage'
    SMTP = 'smtp'
    INFOBOX = 'infoblox'
    STATIC = 'static'

    GROUPED_HEADING = {
        'Cluster Configuration': CLUSTER_CONFIGURATION,
        'Cluster Networking': CLUSTER_NETWORKING,
        'Block Serial #': NODES,
        'IPMI': NODES,
        'Nutanix VLANs': VLAN,
        'Support and Storage': STORAGE,
        'SMTP & Prism Central': SMTP,
        'User VM VLAN(s)': USER_VLAN,
    }

    """
        keys with names as key and 
    """
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
        USER_VLAN: {
            'VLAN Name': 'vlan_vm_name',
            'VLAN ID': 'vlan_vm_id',
            'Gateway': 'vlan_vm_geteway',
            'VLAN Tagging?' : 'vlan_vm_tagging',
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
            'Email Address TO': ['smtp_address_to', 'pulse_email_contact'],
            'Email Address FROM': 'smtp_address_from',
            'PRISM Central Instance IP': 'prism_central_ip',
        }
    }

    parsed_data = {
        # Cluster Configuration
        'location': {
            'name': 'Location',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': False,
            'value': '',
        },
        'cluster_name': {
            'name': 'Cluster Name',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': True,
            'is_to_playbook': True,
            'value': '',
        },
        'cluster_license': {
            'name': 'Cluster License',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': False,
            'value': '',
        },
        'cluster_external_ip': {
            'name': 'Cluster External IP (VIP)',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': True,
            'is_to_playbook': True,
            'value': '',
        },
        'redundancy_factor': {
            'name': 'Cluster Redundancy Factor',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': True,
            'is_to_playbook': True,
            'value': None,
            'format_methods': ['format_filter_to_digits_only'],
        },
        'aos': {
            'name': 'Acropolis Operating System (AOS) version',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': False,
            'value': '',
        },
        'hypervisor_iso': {
            'name': 'Hervisor ISO',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': True,
            'value': {},
        },
        'hypervisor_version': {
            'name': 'Hypervisor Version & Build',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': False,
            'value': '',
        },
        'witness_appliance_version': {
            'name': 'Nutanix Witness Appliance Version',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': False,
            'value': '',
        },
        'witness_address': {
            'name': 'Nutanix Witness Appliance IP Address',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': False,
            'is_to_playbook': True,
            'value': '',
        },
        'cluster_init_successful': {
            'name': 'cluster_init_successful',
            'group': CLUSTER_CONFIGURATION,
            'is_cluster_json': True,
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
            'is_cluster_json': True,
            'is_to_playbook': True,
            'value': [],
        },
        'ntp_server': {
            'name': 'NTP Servers',
            'group': CLUSTER_NETWORKING,
            'is_cluster_json': True,
            'is_to_playbook': True,
            'value': [],
        },
        'nodes': {
            'group': NODES,
        },

        'hypervisor_ip': {
            'group': NODES,
            'is_to_playbook': True,
            'is_cluster_json': False,
            'value': [],
        },

        'cvm_ip': {
            'group': NODES,
            'is_cluster_json': True,
            'is_body_json': True,
            'is_to_playbook': True,
            'value': [],
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
        'vlan_ipmi_name': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_ipmi_id': {
            'group': VLAN,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_filter_to_digits_only'],
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
        # vlan user
        'vlan_vm_name': {
            'group': USER_VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_vm_id': {
            'group': USER_VLAN,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_filter_to_digits_only'],
        },
        'vlan_vm_geteway': {
            'group': USER_VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_vm_tagging': {
            'group': USER_VLAN,
            'is_to_playbook': True,
            'value': '',
        },
        # storage
        'pulse_enabled': {
            'group': STORAGE,
            'is_to_playbook': True,
            'value': '',
        },
        'pulse_email_contact': {
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
        ### These variables need to be added from website
        'infoblox_dev_service_account': {
            'name': 'infoblox_dev_service_account',
            'group': INFOBOX,
            'is_to_playbook': True,
            'value': 'SVC_ibx_d_RW',
        },
        'infoblox_prod_service_account': {
            'name': 'infoblox_prod_service_account',
            'group': INFOBOX,
            'is_to_playbook': True,
            'value': 'SVC_ibx_p_RW',
        },
        'infoblox_dev_server': {
            'name': 'infoblox_dev_server',
            'group': INFOBOX,
            'is_to_playbook': True,
            'value': '10.150.121.139',
        },
        'infoblox_prod_server': {
            'name': 'infoblox_prod_server',
            'group': INFOBOX,
            'is_to_playbook': True,
            'value': '10.130.121.9',
        },
    }
    """
        hypervisor_iso - This sounds weird but it should be empty. Essentially, we need the JSON to read "hypervisor_iso": {}
        skip_hypervisor - Please default to false and don't pull anything from excel
        nos_package - please default to the value and don't pull anything from excel
        is_imaging - default to true and don't pull anything from excel
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

    def __init__(self, file_contents=None, file_path=None, index_sheet=0):
        if file_contents:
            self.__wbook = xlrd.open_workbook(file_contents=file_contents)
        else:
            self.__wbook = xlrd.open_workbook(filename=file_path)
        self.sheet = self.__wbook.sheet_by_index(index_sheet)
        # add static vars
        st = StaticVarsValue.objects.filter(service_type=PlaybookServiceTypes.NUTANIX.value)
        for conf in st:
            self.parsed_data.update({
                conf.key : {
                    'name': conf.key,
                    'group': self.STATIC,
                    'is_cluster_json': True,
                    'is_to_playbook': True,
                    'value': conf.value,
               }
            })


    def get_grouped_heading(self, row_value):
        return self.GROUPED_HEADING.get(row_value)

    def current_row(self, row_num):
        return self.sheet.row_values(row_num)

    def get_headers(self, row_num, to_group):
        return [self.GROUPED_KEYS[to_group].get(head, '') for head in self.current_row(row_num)]

    def set_value_to_parsed_data(self, col_num, row_num, item_key):
        if self.current_row(row_num)[col_num] and item_key and self.parsed_data.get(item_key):
            if type(self.parsed_data.get(item_key)['value']) == list:

                if self.current_row(row_num)[col_num] not in self.parsed_data.get(item_key)['value']:
                    # array should contains uniqe values
                    self.parsed_data.get(item_key)['value'].append(
                        self.set_formating_data(self.parsed_data.get(item_key), self.current_row(row_num)[col_num])
                    )
            else:
                self.parsed_data.get(item_key)['value'] = self.set_formating_data(
                    self.parsed_data.get(item_key), self.current_row(row_num)[col_num]
                )

    def parse_item_config(self, row_num, to_group, value_range=5):
        row_num += 2 # pass heading
        while row_num < self.sheet.nrows:
            item_cell = self.current_row(row_num)[0] if len(self.current_row(row_num)) else None

            if item_cell is None:
                return row_num

            item_cell = re.split(', | & ', item_cell) # some items parsed by , or &

            item_keys = []
            for new_item_key, n in itertools.zip_longest(item_cell, range(2, value_range)):
                if new_item_key is not None:
                    if type(self.GROUPED_KEYS[to_group].get(new_item_key)) == list:
                        item_keys = self.GROUPED_KEYS[to_group].get(new_item_key, [])
                    else:
                        if self.GROUPED_KEYS[to_group].get(new_item_key):
                            item_keys = [self.GROUPED_KEYS[to_group].get(new_item_key)]
                if not item_keys:
                    return row_num
                for item_key in item_keys:
                    self.set_value_to_parsed_data(n, row_num, item_key)
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
        # default values
        DEFAULT_VALUES = {
            'image_now': True,
            'hypervisor': 'kvm',
            'ipmi_configure_now': False,
            'is_bare_metal': True,
        }

        NODE_VALUES = {
            'hypervisor_hostname': {
                'format_methods': ['format_host_name',],
            },
        }


        NODE_KEY = 'ipmi_ip'
        headers = self.get_headers(row_num, to_group)
        row_num += 1
        while row_num < self.sheet.nrows and self.current_row(row_num):
            if not len(self.current_row(row_num)) or not self.current_row(row_num)[0]:
                return row_num

            node_dict = {}
            for inx, value in enumerate(self.current_row(row_num)):
                if headers[inx]:
                    node_dict.update({
                        headers[inx]: self.set_formating_data(NODE_VALUES.get(headers[inx]), value)
                    })
                    if self.parsed_data.get(headers[inx]):
                        "set values to base dict"
                        self.set_value_to_parsed_data(col_num=inx, row_num=row_num, item_key=headers[inx])
            if node_dict:
                node_dict.update(DEFAULT_VALUES)
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
                    value = self.set_formating_data(self.parsed_data.get(f"{prefix}_{headers[inx]}"),
                                                    self.current_row(row_num)[inx])
                    self.parsed_data[f"{prefix}_{headers[inx]}"]['value'] = value
            row_num += 1
        return row_num

    def parse_heading_table_one_row(self, row_num, to_group):

        headers = self.get_headers(row_num, to_group)
        row_num += 1
        for inx in range(1, len(self.current_row(row_num))):
            if headers[inx] and self.parsed_data.get(headers[inx]):
                value = self.set_formating_data(self.parsed_data.get(headers[inx]),
                                                self.current_row(row_num)[inx])
                self.parsed_data[headers[inx]]['value'] = value
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
        if grouped_heading == self.USER_VLAN:
            row_num = self.parse_heading_table_one_row(row_num, grouped_heading)
        if grouped_heading == self.STORAGE:
            row_num = self.parse_item_config(row_num, grouped_heading, 4)
        if grouped_heading == self.SMTP:
            row_num = self.parse_item_config(row_num, grouped_heading, 5)
        return row_num

    def set_formating_data(self, item_obj, value):
        if item_obj and item_obj.get('format_methods'):
            for method_key in item_obj.get('format_methods'):
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

    def get_yml_dict(self, json_path=None):
        """ get_yml_dict
        reformat self.parsed_data to dict which will be dumped to yaml
        :return:
        """
        yml_dict = {
            'foundation_json': json_path
        }

        def format_val(val):
            if type(val) == bool:
                return val
            else:
                return str(val)

        for key, data in self.parsed_data.items():
            value = data.get('value')
            if value is not None and data.get('is_to_playbook'):
                if type(value) == list:
                    yml_dict.update({
                        f"{key}_array": format_val(value),
                    })
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

    def get_json_dict(self):
        default_values = {
            'hypervisor_password': 'nutanix',
            'tests': {
                'run_syscheck': True,
                'run_ncc': True,
            },
        }

        json_dict = {
            'clusters': [],
            'blocks': [],
            **default_values,
        }

        values_to_copy = {
            # copy from key: copy to key
            'hypervisor_nameserver': 'dns_server',
            'current_cvm_vlan_tag': 'vlan_mgmt_and_cvm_id',
        }

        values_to_copy_cluster = {
            'hypervisor_ntp_servers': 'ntp_server',
        }

        clusters_default_values = {
            'enable_ns': False,
            'cluster_init_now': True,
        }

        def copy_values(value_to_copy):
            copied_values = {}
            for target_key, dist_key in value_to_copy.items():
                if self.parsed_data.get(dist_key):
                    copied_values[target_key] = format_val(self.parsed_data.get(dist_key).get('value'), dist_key)
            return copied_values

        def format_val(val, key):
            save_format = ['cluster_members', 'hypervisor_iso']
            cast_to_int = ['redundancy_factor',]
            if key in save_format:
                return val
            if key in cast_to_int:
                return int(val)
            if type(val) == bool:
                return val
            if type(val) == list:
                return ', '.join(val)
            else:
                return str(val)

        def change_cluster_key(key):
            changed_keys = {
                'dns_server': 'cvm_dns_servers',
                'ntp_server': 'cvm_ntp_servers',
                'cvm_ip': 'cluster_members'
            }
            return changed_keys.get(key, key)

        def change_key(key, is_node=False):
            changed_keys = {
                'cvm_ip': 'cvm_ip_array',
                'hypervisor_ip': 'hypervisor_ip_array',
            }
            if is_node:
                return key
            return changed_keys.get(key, key)

        cluster_config = {}

        for key, data in self.parsed_data.items():
            value = data.get('value')
            if value is not None and data.get('is_to_playbook'):
                if data.get('is_cluster_json'):
                    cluster_config.update({ change_cluster_key(key): format_val(value, change_cluster_key(key)) })
                    if data.get('is_body_json'):
                        json_dict.update({change_key(key): format_val(value, key)})
                else:
                    json_dict.update({ change_key(key): format_val(value, key) })
            if key == 'nodes':
                for inx, (node_key, node_obj) in enumerate(data.items()):
                    node_dict = {}
                    if node_key == 'group':
                        continue
                    for k, node_val in node_obj.items():
                        node_dict.update({ change_key(k, True): format_val(node_val, key) })

                    json_dict['blocks'].append({
                        'block_id': node_dict.pop('block_id'),
                        'nodes': [node_dict],
                    })
        copied_val = copy_values(values_to_copy)

        json_dict.update({ **copied_val })

        clusters_copied_val = copy_values(values_to_copy_cluster)
        json_dict['clusters'].append({
            **clusters_default_values,
            **cluster_config,
            **clusters_copied_val,
        })
        return json_dict

    @staticmethod
    def format_host_name(value) -> str:
        return f"{'.'.join(value.split('.')[:-2])}"

    @staticmethod
    def format_filter_to_digits_only(value) -> str:
        """ format_filter_to_digits_only
        """
        return ''.join([ch for ch in value if ch.isdigit()])

    @staticmethod
    def format_vlan_id(value) -> str:
        return value.split(' ')[-1].replace(')', '')

    @staticmethod
    def format_integer(value) -> str:
        return str(int(value))


