import logging
from tkinter.filedialog import askopenfilename
from tkinter import Entry
from os.path import normpath, exists, basename, dirname
from model.scripts.file_handler import resource_path
from model.gui_config import GuiConfiguration
from view.add_treeview import AddTreeview


logger = logging.getLogger('add_treeview_controller')


class AddTreeviewController:
    '''
    AddTreeviewController
    ---------------------

    Controller of AddTreeview GUI
    '''
    def __init__(self, add_treeview: AddTreeview, gui_configuration: GuiConfiguration) -> None:
        self.gui_configuration = gui_configuration
        self.frame = add_treeview
        self.last_grab = self.frame.grab_current()
        self.frame.grab_set()   
        win_pos = self.gui_configuration.check_update_win_pos(self.frame.geometry(), 'add_treeview')
        if win_pos:
            self.frame.geometry(win_pos)
        self.frame.protocol('WM_DELETE_WINDOW', self.destroy)  

        self.entry_process_name = self.frame.entry_process_name
        self.entry_process_path = self.frame.entry_process_path
        self.entry_cmd_line = self.frame.entry_cmd_line

        self.button_path = self.frame.button_path
        self.button_ok = self.frame.button_ok
        self.button_cancel = self.frame.button_cancel
        
        self.button_path.config(command=lambda path=self.entry_process_path, file=self.entry_process_name: self.file_path_command(path, file))
        self.button_ok.config(command=self.ok_command)
        self.button_cancel.config(command=self.cancel_command)

        self.process = None

    def ok_command(self, event=None) -> None:
        self.process = (self.entry_process_name.get(), self.entry_process_path.get(), self.entry_cmd_line.get())
        self.destroy()

    def cancel_command(self, event=None) -> None:
        self.destroy()

    def file_path_command(self, entry_path: Entry, entry_file: Entry, event=None) -> None:
        file_path = askopenfilename(initialdir='/', title='Select file')
        old_path = entry_path.get()
        old_file = entry_file.get()
        if file_path:
            try:
                file_path = normpath(file_path)
                directory = dirname(file_path)
                file_name = basename(file_path)
                entry_path.delete(0, 'end')
                entry_path.insert('end', str(directory))
                entry_path.lift()
                entry_file.delete(0, 'end')
                entry_file.insert('end', str(file_name))
                logger.debug(f'File path {file_path}')
            except Exception as error:
                logger.warning(f'Could not get file path due {error}')
                if old_path:
                    entry_path.delete(0, 'end')
                    entry_path.insert('end', str(old_path))
                    entry_file.delete(0, 'end')                    
                    entry_file.insert('end', str(old_file))

    def get_process(self) -> str:
        return self.process

    def fill_process(self, process_name: str, process_path: str, cmd_line: str) -> None:
        self.entry_process_name.insert(0, process_name)
        self.entry_process_path.insert(0, normpath(process_path))
        self.entry_cmd_line.insert(0, cmd_line)

    def destroy(self) -> None:
        if self.last_grab:
            self.last_grab.grab_set()
        self.gui_configuration.check_update_win_pos(self.frame.geometry(), 'add_treeview')
        self.frame.destroy()