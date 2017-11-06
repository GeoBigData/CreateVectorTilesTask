import os
import re
import string
import json

from base_types import *


class InputPortBase(object):

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

    def __init__(self, value, data_type, port_descriptor):

        self.name = port_descriptor['name']

        self.data_type = data_type
        self.default = port_descriptor.get('defaultValue', None)

        self.value = value
        self.description = port_descriptor.get('description', None)


class IntegerInputPort(InputPortBase, Int):
    data_type = 'integer'

    @classmethod
    def parse(cls, value, port_descriptor):
        default = port_descriptor['defaultValue'] if 'defaultValue' in port_descriptor else None
        value = value if value is not None else default

        return cls(value, cls.data_type, port_descriptor)


class MappingInputPort(InputPortBase, Mapping):
    data_type = 'mapping'

    @classmethod
    def parse(cls, value, port_descriptor):
        default = port_descriptor['defaultValue'] if 'defaultValue' in port_descriptor else None
        value = value if value is not None else default

        if type(value) is dict:
            return value

        if string.strip(value) == '':
            return {}

        pairs = map(string.strip, value.split(','))
        pairs = [pair.split('=') for pair in pairs]
        value = {item[0]: item[1] for item in pairs}

        return cls(value, cls.data_type, port_descriptor)


class BooleanInputPort(InputPortBase, Bool):
    data_type = 'boolean'

    @classmethod
    def parse(cls, value, port_descriptor):
        default = port_descriptor['defaultValue']
        value = value if value is not None else default

        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False

        return cls(value, cls.data_type, port_descriptor)


class ListInputPort(InputPortBase, List):
    data_type = 'list'

    @classmethod
    def parse(cls, value, port_descriptor):
        default = port_descriptor['defaultValue'] if 'defaultValue' in port_descriptor else None
        value = value if value is not None else default

        value = [string.strip(item) for item in value.split(',')]

        return cls(value, cls.data_type, port_descriptor)


class StringInputPort(InputPortBase, String):
    data_type = 'string'

    @classmethod
    def parse(cls, value, port_descriptor):
        default = port_descriptor['defaultValue'] if 'defaultValue' in port_descriptor else None
        value = value if value is not None else default

        return cls(value, cls.data_type, port_descriptor)


class DirectoryInputPort(InputPortBase, String):
    data_type = 'directory'

    @classmethod
    def parse(cls, value, port_descriptor, work_path):
        value = os.path.join(work_path, 'input', value)

        return cls(value, cls.data_type, port_descriptor)


class InputPort(InputPortBase):
    DATA_TYPES = ['string', 'mapping', 'boolean', 'directory', 'list', 'integer']

    @classmethod
    def parse(cls, value, port_descriptor, work_path='/mnt/work'):
        data_type = cls.get_data_type(port_descriptor)

        if data_type == 'boolean':
            return BooleanInputPort.parse(value, port_descriptor)
        elif data_type == 'mapping':
            return MappingInputPort.parse(value, port_descriptor)
        elif data_type == 'list':
            return ListInputPort.parse(value, port_descriptor)
        elif data_type == 'integer':
            return IntegerInputPort.parse(value, port_descriptor)
        elif data_type == 'string':
            return StringInputPort.parse(value, port_descriptor)
        elif data_type == 'directory':
            return DirectoryInputPort.parse(value, port_descriptor, work_path)

    @classmethod
    def get_data_type(cls, port_descriptor):
        data_type = port_descriptor.get(
            'dataType',
            'directory' if port_descriptor['type'] == 'directory' else 'string'
        )
        if data_type not in cls.DATA_TYPES:
            raise ValueError('Data type {data_type} for port {name} is invalid.'.format(
                data_type=data_type,
                name=port_descriptor.get('name', None)
            ))
        return data_type


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
            input_port = InputPort.parse(value, descriptor)

            setattr(self, input_port.sanitized_name, input_port)

    @property
    def base_path(self):
        return self._work_path

    @property
    def input_path(self):
        return os.path.join(self.base_path, 'input')

