from django.conf import settings
import os
import xlrd
import itertools
import re
from playbook_generator.models import StaticVarsValue, PlaybookServiceTypes


GROUPED_HEADING = {
    'Hostname': 'host_data',
}


class VmWareParser():
    __wbook = None
    HOST_DATA = 'host_data'
    VCENTER_DATA = 'vcenter_address'
    ILO_DATA = 'user_data'
    VLAN_DATA = 'Network Label'
    SYSLOG_SERVER_DATA = 'Syslog Server'
    STATIC = 'static'
    NTP_SERVER = 'ntp_server'
    SNMP_DATA = 'snmp_data'

    GROUPED_HEADING = {
        'Hostname': HOST_DATA,
        'VCENTER': VCENTER_DATA,
        'IPMI Name': ILO_DATA,
        'Network Label': VLAN_DATA,
        'Syslog Server': SYSLOG_SERVER_DATA,
        'NTP Server 1': NTP_SERVER,
        'SNMP Server 1': SNMP_DATA,
    }

    GROUPED_KEYS = {
        HOST_DATA: {
            'Hostname': 'esxi_host_name',
            'VLAN': 'esxi_host_mgmt_vlan_id',
            'IP address': 'esxi_host_mgmt_ip',
            'Subnet Mask': 'esxi_host_mgmt_subnet',
            'Gateway': 'esxi_host_mgmt_gw',
            'Preferred DNS': 'dns_server_1',
            'Alternate DNS': 'dns_server_2',
        },
        VCENTER_DATA: {
            'VCENTER': 'vcenter_address',
            'DataCenter Folder': 'country',
            'City Folder': 'city_folder',
            'Datacenter': 'dc_name',
        },
        ILO_DATA: {
            # 'iLO Name': 'ilo_name',
            'IP address': 'esxi_host_ipmi_ip',
            'Username': 'esxi_host_ipmi_username',
            'Password': 'esxi_host_ipmi_pw',
        },
        SYSLOG_SERVER_DATA: {
            'Syslog Server': 'syslog_hostname',
            'Syslog IP': 'syslog_ip',
        },
        VLAN_DATA: {
            'Network Label': 'vlan_vm_name',
            'VLAN ID': 'vlan_vm_id',
        },
        NTP_SERVER: {
            'NTP Server 1': 'ntp_server_1',
            'NTP Server 2': 'ntp_server_2',
        },

        SNMP_DATA: {
            'SNMP Server 1': 'snmp_server_1',
            'SNMP Server 2': 'snmp_server_2',
            'SNMP Community': 'snmp_community',
            'SNMP Port': 'snmp_port',
        }
    }

    """
        parsed_data values with all possible values with additional configs 
    """
    PARSED_DATA = {
        # keys in order
        'esxi_host_name': {
            'name': 'esxi_host_name',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_host_name', ],
        },

        'esxi_host_mgmt_ip': {
            'name': 'esxi_host_mgmt_ip',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'esxi_host_mgmt_subnet': {
            'name': 'esxi_host_mgmt_subnet',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
        },

        'esxi_host_mgmt_gw': {
            'name': 'esxi_host_mgmt_gw',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
        },

        'esxi_host_mgmt_vlan_id': {
            'name': 'esxi_host_mgmt_vlan_id',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_vlan_id', 'format_filter_to_digits_only', 'format_integer'],
        },

        'esxi_host_ipmi_ip': {
            'name': 'esxi_host_ipmi_ip',
            'group': ILO_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'esxi_host_ipmi_username': {
            'name': 'esxi_host_ipmi_username',
            'group': ILO_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'esxi_host_ipmi_pw': {
            'name': 'esxi_host_ipmi_pw',
            'group': ILO_DATA,
            'is_to_playbook': True,
            'value': '',
        },

        # default values HOST_DATA
        'datastore_name': {
            'is_default': True,
            'name': 'datastore_name',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '{{ esxi_host_name }}-local',
        },

        'dns_server_1': {
            'name': 'dns_server_1',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'dns_server_2': {
            'name': 'dns_server_2',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': '',
        },

        'dns_server_array': {
            'name': 'dns_server_array',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': ["{{ dns_server_1 }}", "{{ dns_server_2 }}"],
        },

        # VCENTER_DATA
        'vcenter_address': {
            'name': 'vcenter_address',
            'group': VCENTER_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'country': {
            'name': 'country',
            'group': VCENTER_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'city_folder': {
            'name': 'city_folder',
            'group': VCENTER_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'dc_name': {
            'name': 'dc_name',
            'group': VCENTER_DATA,
            'is_to_playbook': True,
            'value': '',
        },

        # NTP Server
        'ntp_server_1': {
            'name': 'NTP Server 1',
            'group': NTP_SERVER,
            'is_to_playbook': True,
            'value': '',
        },
        'ntp_server_2': {
            'name': 'NTP Server 2',
            'group': NTP_SERVER,
            'is_to_playbook': True,
            'value': '',
        },

        'ntp_server_array': {
            'name': 'ntp_server_array',
            'group': HOST_DATA,
            'is_to_playbook': True,
            'value': ['{{ ntp_server_1 }}', '{{ ntp_server_2 }}'],
        },

        # SNMP_DATA

        'snmp_server_1': {
            'name': 'SNMP Server 1',
            'group': SNMP_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'snmp_server_2': {
            'name': 'SNMP Server 2',
            'group': SNMP_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'snmp_community': {
            'name': 'SNMP Community',
            'group': SNMP_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'snmp_port': {
            'name': 'SNMP Port',
            'group': SNMP_DATA,
            'is_to_playbook': True,
            'format_methods': ['format_filter_to_digits_only',],
        },

        # Syslog Server

        'syslog_hostname': {
            'name': 'syslog_hostname',
            'group': SYSLOG_SERVER_DATA,
            'is_to_playbook': False,
            'value': '',
        },
        'syslog_ip': {
            'name': 'syslog_ip',
            'group': SYSLOG_SERVER_DATA,
            'is_to_playbook': True,
            'value': '',
        },
        'vlan_vm_name': {
            'name': 'vlan_vm_name',
            'group': VLAN_DATA,
            'is_to_playbook': True,
            'is_default': False,
            'value': '',
            'format_methods': ['format_to_underscore', ],
        },
        'vlan_vm_id':  {
            'name': 'vlan_vm_id',
            'group': VLAN_DATA,
            'is_to_playbook': True,
            'value': '',
            'format_methods': ['format_vlan_id', 'format_filter_to_digits_only', 'format_integer'],
        },
    }

    def __init__(self, file_contents=None, file_path=None, index_sheet=0):
        self.parsed_data = {}
        for key in self.PARSED_DATA.keys():
            self.parsed_data[key] = self.PARSED_DATA[key].copy()
        if file_contents:
            self.__wbook = xlrd.open_workbook(file_contents=file_contents)
        else:
            self.__wbook = xlrd.open_workbook(filename=file_path)
        self.sheet = self.__wbook.sheet_by_index(index_sheet)
        st = StaticVarsValue.objects.filter(service_type=PlaybookServiceTypes.VMWARE.value)
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
        return list(filter(lambda item: bool(item),self.sheet.row_values(row_num)))

    def get_headers(self, row_num, to_group):
        return [self.GROUPED_KEYS[to_group].get(head, '') for head in self.current_row(row_num)]

    def parse_heading_table(self, row_num, to_group):
        """
        """
        headers = self.get_headers(row_num, to_group)
        row_num += 1

        while row_num < self.sheet.nrows and self.current_row(row_num):
            if not len(self.current_row(row_num)) or not self.current_row(row_num)[0]:
                return row_num
            for inx in range(0, len(self.current_row(row_num))):
                if inx > len(headers) - 1:
                    headers.append('')
                if not self.parsed_data.get(f"{headers[inx]}"):
                    continue
                value = self.set_formating_data(self.parsed_data.get(f"{headers[inx]}"),
                                                self.current_row(row_num)[inx])
                try:
                    if not self.parsed_data[f"{headers[inx]}"].get('is_default'):
                        self.parsed_data[f"{headers[inx]}"]['value'] = value
                except KeyError:
                    print('error!!!', headers[inx], value, row_num)
            row_num += 1
        return row_num

    def parse_with_type(self, row_num):
        """ parse_with_type
            select method for parse grouped block with diff type
        :param row_num:
        :return: row_num:
        """
        grouped_heading = self.get_grouped_heading(self.current_row(row_num)[0])
        if grouped_heading == self.HOST_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.VCENTER_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.ILO_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.VLAN_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.SYSLOG_SERVER_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.NTP_SERVER:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        if grouped_heading == self.SNMP_DATA:
            row_num = self.parse_heading_table(row_num, grouped_heading)
        return row_num

    def parse_file(self):
        row_num = 0
        while row_num < self.sheet.nrows:
            if len(self.current_row(row_num)) > 0 and self.get_grouped_heading(self.current_row(row_num)[0]) is not None:
                row_num = self.parse_with_type(row_num)
            else:
                row_num += 1

    def set_formating_data(self, item_obj, value):
        if item_obj and item_obj.get('format_methods'):
            for method_key in item_obj.get('format_methods'):
                format_method = self.__getattribute__(method_key)
                if format_method:
                    value = format_method(value)
        return value

    def get_yml_dict(self, json_path=None):
        """ get_yml_dict
        reformat self.parsed_data to dict which will be dumped to yaml
        :return:
        """
        yml_dict = {
            # 'foundation_json': json_path
        }

        def format_val(val):
            return val

        for key, data in self.parsed_data.items():
            value = data.get('value')
            if value is not None and data.get('is_to_playbook'):
                yml_dict.update({
                    key: format_val(value),
                })
        return yml_dict

    def get_json_dict(self):
        json_dict = {
            # 'foundation_json': json_path
        }
        def format_val(val):
            if type(val) == bool:
                return val
            return val
        for key, data in self.parsed_data.items():
            value = data.get('value')
            if value is not None and data.get('is_to_playbook'):
                json_dict.update({
                    key: format_val(value),
                })
        return json_dict



    @staticmethod
    def format_host_name(value) -> str:
        return f"{'.'.join(value.split('.')[:-2])}"

    @staticmethod
    def format_filter_to_digits_only(value) -> str:
        """ format_filter_to_digits_only
        """
        if str == type(value):
            return ''.join([ch for ch in value if ch.isdigit()])
        if float == type(value):
            return int(value)
        return value

    @staticmethod
    def format_vlan_id(value) -> str:
        if str == type(value):
            return value.split(' ')[-1].replace(')', '')
        if float == type(value):
            return int(value)
        return value

    @staticmethod
    def format_integer(value) -> str:
        return str(int(value))

    @staticmethod
    def format_to_underscore(value) -> str:
        return value.replace('- ', '').replace(' ', '_')


