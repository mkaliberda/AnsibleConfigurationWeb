import yaml

class quoted(str):
    pass


class YamlLoader:

    def __init__(self, *args, **kwargs):
        self.yaml = yaml
        yaml.add_representer(quoted, self.quoted_presenter)

    def get_yaml_parsed_dict(self, yml_dict):
        yaml_parsed_dict = {}
        for key, val in yml_dict.items():
            if type(val) == str or type(val) == list:
                yaml_parsed_dict[key] = quoted(val)
            else:
                yaml_parsed_dict[key] = val
        return yaml_parsed_dict

    def yaml_dump(self, yml_dict):
        return yaml.dump(
            self.get_yaml_parsed_dict(yml_dict),
            default_flow_style=False, sort_keys=False, encoding='utf-8'
        )

    @staticmethod
    def quoted_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

