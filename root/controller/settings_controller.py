import logging
from copy import deepcopy
from os.path import normpath, exists, isfile, dirname
from os import mkdir
from datetime import time
from tkinter import IntVar
from tkinter.messagebox import askquestion, showerror
from model.database import Database
from model.classes.config import Configuration, ProcessInit
from model.scripts.file_handler import resource_path
from model.gui_config import GuiConfiguration
from view.settings import Settings
from view.add_treeview import AddTreeview
from controller.add_treeview_controller import AddTreeviewController
from controller.validation_controller import int_validate, time_validate

logger = logging.getLogger('settings_controller')


class SettingsController:
    '''
    SettingsController
    ------------------

    attributes
        - settings_view (Settings)
        - database (Database)
        - gui_configuration (GuiConfiguration)
    '''
    def __init__(self, settings_view: Settings, database: Database, gui_configuration: GuiConfiguration) -> None:
        self.frame = settings_view
        self.database = database
        self.gui_configuration = gui_configuration
        self.configuration = deepcopy(self.database.get('config'))
        self.last_grab = self.frame.grab_current()
        self.frame.grab_set()   
        win_pos = self.gui_configuration.check_update_win_pos(self.frame.geometry(), 'settings')
        if win_pos:
            self.frame.geometry(win_pos)
        self.frame.protocol('WM_DELETE_WINDOW', self.__on_window_close)  

        # Widgets Entries
        self.entry_sleep_interval = self.frame.entry_sleep_interval
        self.entry_sleep_time = self.frame.entry_sleep_time
        self.entry_start_delay = self.frame.entry_start_delay
        self.entry_pause_time = self.frame.entry_pause_time
        self.entry_operation_start_time = self.frame.entry_operation_start_time
        self.entry_operation_end_time = self.frame.entry_operation_end_time

        self.treeview = self.frame.treeview
        self.button_add = self.frame.button_add
        self.button_edit = self.frame.button_edit
        self.button_remove = self.frame.button_remove

        self.bool_check = IntVar(self.frame.master)
        self.check_start_min = self.frame.check_start_min
        self.check_start_min.config(variable=self.bool_check)

        # Widgets Buttons
        self.button_cancel = self.frame.button_cancel
        self.button_ok = self.frame.button_ok

        # Commands
        self.button_add.config(command=self.treeview_add_command)
        self.button_edit.config(command=self.treeview_edit_command)
        self.button_remove.config(command=self.treeview_remove_command)
        self.button_cancel.config(command=self.cancel_command)
        self.button_ok.config(command=self.ok_command)
        self.entry_int_list = [self.entry_sleep_interval, self.entry_sleep_time, self.entry_start_delay, self.entry_pause_time]
        self.entry_time_list = [self.entry_operation_start_time, self.entry_operation_end_time]
        self.fill_entries()

        # Validation
        self.int_vcmd = (self.frame.register(int_validate), 
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.time_vcmd = (self.frame.register(time_validate), 
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W', 8)
        for entry in self.entry_int_list:
            entry.config(validate='key', validatecommand=self.int_vcmd)
        for entry in self.entry_time_list:
            entry.config(validate='key', validatecommand=self.time_vcmd)

        for entry in self.entry_time_list:
            entry.bind('<FocusOut>', lambda event: self.time_format(event))

        for column in self.frame.columns:
            self.treeview.heading(column, command=lambda column_value=column: self.__sort_tree_view(column_value, False))

    def __sort_tree_view(self, colum_value, descending):
        '''
        __sort_tree_view
        ----------------

        Sort treeview by selected column

        https://www.w3resource.com/python-exercises/tkinter/python-tkinter-widgets-exercise-18.php
        '''
        tree_view_data = [(self.tree_view.set(item, colum_value), item) for item in self.tree_view.get_children('')]
        tree_view_data.sort(reverse=descending)
        even_odd = {0 : 'evenrow', 1 : 'oddrow'}
        for index, (_, item) in enumerate(tree_view_data):
            self.treeview.move(item, '', index)
            self.treeview.item(item, tags=(even_odd.get(index % 2)))
        self.tree_view.heading(colum_value, command=lambda: self.__sort_tree_view(colum_value, not descending))

    def set_treeview(self, values_list: list[ProcessInit]) -> None:
        '''
        Set values on treeview GUI
        '''
        even_odd = {0: 'evenrow', 1: 'oddrow'}
        self.treeview.delete(*self.treeview.get_children())
        if len(values_list) > 0:
            for i, value in enumerate(values_list):
                self.treeview.insert('', 'end', values=(value.process_name, value.process_path, value.cmdline_detail), tags=(even_odd.get(i % 2)))

    def time_format(self, event) -> None:
        entry_widget = event.widget
        time_str = entry_widget.get().replace(':', '').ljust(6, '0')
        try:
            hour = int(time_str[0:2])
            minutes = int(time_str[2:4])
            seconds = int(time_str[4:6])
            time_value = time(hour, minutes, seconds)
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, f'{time_value.hour}:{time_value.minute}:{time_value.second}')            
        except Exception as error:
            logger.warning(f'Wrong time format {error}')
            showerror('Time format error.', 'Wrong time or time format, try again.')
            self.fill_entries()


    def treeview_add_command(self, event=None) -> None:
        '''
        Treeview Add Command
        --------------------

        add process to treeview
        '''
        self.treeview_add = AddTreeview(self.frame.master)
        self.treeview_add_controller = AddTreeviewController(self.treeview_add, self.gui_configuration)
        self.frame.wait_window(self.treeview_add)
        process_values = self.treeview_add_controller.get_process()
        if process_values:
            self.configuration.add_process(self.process_dict(process_values))
            self.clear()
            self.fill_entries()

    def treeview_edit_command(self, event=None) -> None:
        '''
        Treeview Edit Command
        ---------------------
        
        Edit currente selected process
        '''
        process = self.treeview.item(self.treeview.selection()[0]).get('values')
        self.treeview_add = AddTreeview(self.frame.master)
        self.treeview_add_controller = AddTreeviewController(self.treeview_add, self.gui_configuration)
        self.treeview_add_controller.fill_process(*process)   
        self.frame.wait_window(self.treeview_add)
        process_values = self.treeview_add_controller.get_process()
        if process_values:
            if not process_values[0] == process[0] or not process_values[1] == process[1] or not process_values[2] == process[2]:
                answer = askquestion('Process edit', 'Changes were made in Process. \nDo you want replace it?')
                if answer == 'yes':
                    process_edited = ProcessInit.init_dict(self.process_dict(process_values))                    
                    self.configuration.replace_process(ProcessInit.init_dict(self.process_dict(process)), process_edited)
                    self.fill_entries()

    def treeview_remove_command(self, event=None) -> None:
        '''
        Treeview Remove Command
        -----------------------
        '''
        process = self.treeview.item(self.treeview.selection()[0]).get('values')
        self.configuration.remove_process(ProcessInit.init_dict(self.process_dict(process)))
        self.fill_entries()      

    def cancel_command(self, event=None) -> None:
        self.save_close()

    def ok_command(self, event=None) -> None:
        self.save_close(True)

    def save_close(self, ok: bool=False) -> None:
        '''
        Save Close
        ----------

        Compare values in the settings GUI with the saved values and confirms save
        '''
        try:
            old_config = self.database.get('config')
            new_confg = self.get_entries()
        except Exception as error:
            if not ok:
                self.destroy()
                return
            else:
                showerror('Save Error', f'Could not get values for saving check due\n{error}')
                return
        if not old_config.__eq__(new_confg):
            answer = askquestion('Configuration save', 'Changes were made in configuration. \nDo you want to save it?')
            if answer == 'yes':
                self.save(new_confg)
        self.destroy()

    def save(self, new_config: Configuration) -> None:
        try:
            self.database.save_update('config', new_config)
        except Exception as error:
            logger.error(f'Could not save due {error}')
            showerror('Save error', f'Could not save configuration due {error}')
        finally:
            return

    def fill_entries(self) -> None:
        '''
        Fill all values from configuration in GUI 
        '''
        self.clear()
        self.entry_sleep_interval.insert(0, self.configuration.sleep_interval)
        self.entry_sleep_time.insert(0, self.configuration.sleep_time)
        self.entry_start_delay.insert(0, self.configuration.start_delay)
        self.entry_pause_time.insert(0, self.configuration.pause_time)
        self.entry_operation_start_time.insert(0, self.configuration.operation_start_time)
        self.entry_operation_end_time.insert(0, self.configuration.operation_end_time)
        self.bool_check.set(self.configuration.start_min)
        self.set_treeview(self.configuration.process_list) 

    def check_format_path(self, path: str) -> str:
        '''
        Check path
        '''
        path = normpath(resource_path(path))
        if isfile(path):
            path_dir = dirname(path)
        else:
            path_dir = path
        if not exists(path_dir):
            mkdir(path_dir)
        return path

    def process_dict(self, process_treeview: tuple[str, str, str]) -> dict[str, str]:
        process = {}
        process['process_path'] = process_treeview[1]
        process['process_name'] = process_treeview[0]
        process['cmdline_detail'] = process_treeview[2]
        return process

    def get_entries(self) -> Configuration:
        '''
        Get Entries
        -----------

        Create a new configuration object with the GUI values
        '''
        try:
            new_sleep_interval = int(self.entry_sleep_interval.get())
            new_sleep_time = int(self.entry_sleep_time.get())
            new_start_delay = int(self.entry_start_delay.get())
            new_pause_time = int(self.entry_pause_time.get())
            new_start_min = self.bool_check.get()
            new_operation_start_time = time(*[int(value) for value in self.entry_operation_start_time.get().split(':')])
            new_operation_end_time = time(*[int(value) for value in self.entry_operation_end_time.get().split(':')])
            new_process_list = [ProcessInit.init_dict(self.process_dict(self.treeview.item(id).get('values'))) for id in self.treeview.get_children()]
            return Configuration(new_process_list, new_sleep_time, new_sleep_interval, new_operation_start_time, new_operation_end_time, new_start_delay, new_start_min, new_pause_time)
        except Exception as error:
            self.fill_entries()
            raise error

    def clear(self) -> None:
        '''
        Clear
        -----

        Remove all values from the GUI
        '''
        for entry in self.entry_int_list + self.entry_time_list:
            entry.delete(0, 'end')
        self.treeview.delete(*self.treeview.get_children())

    def __on_window_close(self):
        self.destroy()

    def destroy(self) -> None:
        if self.last_grab:
            self.last_grab.grab_set()
        self.gui_configuration.check_update_win_pos(self.frame.geometry(), 'settings')
        self.frame.destroy()