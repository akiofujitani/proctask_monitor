from os.path import normpath, abspath
from datetime import time
import logging

logger = logging.getLogger('Config')

class ProcessInit:
    '''
    ProcessInit

    Args
        - process_path - str
        - process_name - str
        - cmdline_detail - str
    '''
    def __init__(self, process_path: str, process_name: str, cmdline_detail: str='') -> None:
        self.process_path = process_path
        self.process_name = process_name
        self.cmdline_detail = cmdline_detail

    def combine_cmd(self) -> str:
        if not self.cmdline_detail:
            return self.process_name
        else:
            return f'{self.process_name} {self.cmdline_detail}'

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True    

    @classmethod
    def init_dict(cls, dict_values: dict[str, str]) -> object:
        process_path = abspath(normpath(dict_values.get('process_path')))
        process_name = dict_values.get('process_name')
        cmdline_details = dict_values.get('cmdline_detail')
        return cls(process_path, process_name, cmdline_details)

class Configuration:
    def __init__(self, process_list: list[ProcessInit], sleep_time: int, sleep_interval: int, operation_start_time: time, operation_end_time: time, start_delay: int, start_min: bool, pause_time: int) -> None:
        self.process_list = process_list
        self.sleep_time = sleep_time
        self.sleep_interval = sleep_interval
        self.operation_start_time = operation_start_time
        self.operation_end_time = operation_end_time  
        self.start_delay = start_delay
        self.start_min = start_min
        self.pause_time = pause_time

    def add_process(self, process_dict: dict[str, str]) -> bool:
        try: 
            new_process = ProcessInit.init_dict(process_dict)
            for process in self.process_list:
                if new_process.__eq__(process):
                    raise Exception('Process already exists.')
            return True
        except Exception as error:
            logger.warning(f'Could not add process due {error}')
            return False

    def replace_process(self, old_process: ProcessInit, new_process: ProcessInit) -> bool:
        for i, process in enumerate(self.process_list):
            if process.__eq__(old_process):
                self.process_list[i] = new_process
                return True
        return False

    def remove_process(self, process_remove: ProcessInit) -> bool:
        for process in self.process_list:
            if process.__eq__(process_remove):
                self.process_list.remove(process_remove)
                return True
        return False

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True    
    
    @classmethod
    def init_dict(cls, dict_values: dict[str, str]) -> object:
        process_list = [ProcessInit.init_dict(process) for process in dict_values.get('process_list')]
        sleep_time = int(dict_values.get('sleep_time'))
        sleep_interval = int(dict_values.get('sleep_interval'))
        operation_start_time = time(*[int(num) for num in dict_values.get('operation_start_time').split(':')])
        operation_end_time = time(*[int(num) for num in dict_values.get('operation_end_time').split(':')])     
        start_delay = int(dict_values.get('start_delay'))
        start_min = eval(dict_values.get('start_min'))
        pause_time = int(dict_values.get('pause_time'))
        return cls(process_list, sleep_time, sleep_interval, operation_start_time, operation_end_time, start_delay, start_min, pause_time)