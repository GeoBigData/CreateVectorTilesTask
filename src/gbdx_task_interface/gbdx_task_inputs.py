import os
import re
import string
import json


class InputPort(object):

    DATA_TYPES = ['string', 'mapping', 'boolean', 'directory', 'list']

    @property
    def base_path(self):
        return self._work_path

    @property
    def input_path(self):
        return os.path.join(self.base_path, 'input')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        name = str(name)
        self.__name = name

    @property
    def sanitized_name(self):
        return re.sub(r'\W', '_', self.name).lower()

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        value = value if value is not None else self.default
        value = self.parse_value(value)
        self.__value = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        description = str(description)
        self.__description = description

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, default):
        default = self.parse_value(default)
        self.__default = default

    @property
    def data_type(self):
        return self.__data_type

    @data_type.setter
    def data_type(self, data_type):
        if data_type not in self.DATA_TYPES:
            raise ValueError('Data type {data_type} is not one of valid data types {data_types}'.format(
                data_type=data_type,
                data_types=self.DATA_TYPES
            ))
        self.__data_type = data_type

    def __init__(self, port_descriptor, value=None, work_path='/mnt/work'):
        self._work_path = work_path

        self.name = port_descriptor['name']

        self.data_type = port_descriptor.get(
            'dataType',
            'directory' if port_descriptor['type'] == 'directory' else 'string'
        )
        self.default = port_descriptor.get('defaultValue', None)

        self.value = value
        self.description = port_descriptor.get('description', None)

    def parse_value(self, value):
        if value is None:
            return value
        else:
            value = str(value)

            if self.data_type == 'mapping':
                return self._parse_mapping_value(value)
            elif self.data_type == 'boolean':
                return self._parse_boolean_value(value)
            elif self.data_type == 'list':
                return self._parse_list_value(value)
            elif self.data_type == 'directory':
                return self._parse_directory_value(value)
            else:
                return str(value)

    def _parse_mapping_value(self, value):
        if type(value) is dict:
            return value

        if type(value) is not str:
            raise TypeError('Invalid value type {val_type} for {name} input port'.format(
                val_type=type(value),
                name=self.name
            ))

        if string.strip(value) == '':
            return {}

        pairs = map(string.strip, value.split(','))
        pairs = [pair.split('=') for pair in pairs]
        return {item[0]: item[1] for item in pairs}

    def _parse_boolean_value(self, value):
        if type(value) is bool:
            return value

        if type(value) is not str or value.lower() not in ['true', 'false']:
            raise ValueError('Invalid value {value} for type \'boolean\' for input port {name}'.format(
                value=value,
                name=self.name
            ))

        return True if value.lower() == 'true' else False

    def _parse_list_value(self, value):
        if type(value) is list:
            return value

        if type(value) is not str:
            raise ValueError('Invalid value type {val_type} for input port {name}'.format(
                val_type=type(value),
                name=self.name
            ))

        return [string.strip(item) for item in value.split(',')]

    def _parse_directory_value(self, value):
        full_path = os.path.abspath(os.path.join(self.input_path, value))

        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise ValueError('Directory {value} does not exist or is not a directory for input port {name}'.format(
                value=full_path,
                name=self.name
            ))

        return full_path


class InputPorts(object):
    def __init__(self, work_path="/mnt/work", task_def_path='./task-definition.json'):
        self._work_path = work_path

        # Try getting the task description JSON
        try:
            with open(task_def_path, 'r') as f:
                task_def = json.load(f)
        except IOError:
            raise IOError('Cannot find task definition file {task_definition}'.format(task_definition=task_def_path))

        # If there are any string ports, load them from ports.json
        input_port_descriptors = task_def['inputPortDescriptors']
        if any(port['type'] == 'string' for port in input_port_descriptors):
            input_ports_file = os.path.join(self.input_path, "ports.json")
            if os.path.exists(input_ports_file):
                with open(input_ports_file, 'r') as f:
                    string_input_ports = json.load(f)
            else:
                raise IOError('String ports found in task definition, but no input ports.json file is present.')
        else:
            string_input_ports = {}

        # Attach each input port instance to this object
        for descriptor in task_def['inputPortDescriptors']:

            if descriptor['type'] == 'directory':
                # If the input is a directory type, we want to use the name as the value
                value = descriptor['name']
            elif descriptor['name'] not in string_input_ports:
                # If there is no value provided in ports.json, fallback to the default value
                # TODO: Should have a "required" field in the task definition so we can raise an exception here
                value = None
            else:
                # Otherwise, get the value from ports.json
                value = string_input_ports[descriptor['name']]
            input_port = InputPort(descriptor, value)

            setattr(self, input_port.sanitized_name, input_port)

    @property
    def base_path(self):
        return self._work_path

    @property
    def input_path(self):
        return os.path.join(self.base_path, 'input')

