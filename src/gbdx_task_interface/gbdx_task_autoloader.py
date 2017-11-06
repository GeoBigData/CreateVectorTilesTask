from gbdx_task_interface import GbdxTaskInterface
from gbdx_task_inputs import InputPorts


class GbdxTaskAutoloader(GbdxTaskInterface):
    def __init__(self, task_def='./task-definition.json', *args, **kwargs):
        super(GbdxTaskAutoloader, self).__init__(*args, **kwargs)

        self.inputs = InputPorts(self.base_path, task_def)
