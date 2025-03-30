import logging
from tkinter import Toplevel, Label, Button, Entry, Frame, Tk


logger = logging.getLogger('add_treeview')


class AddTreeview(Toplevel):
    '''
    AddTreeview
    -----------

    Treeview add window
    '''
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.master = master
        self.title('Add Process')
        self.minsize(500, 200)
        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1, minsize=40)

        row_num = 0
        Label(self, text='Please select the executable file', justify='center').grid(column=0, row=row_num, columnspan=3, sticky='nesw', padx=5, pady=5)

        row_num += 1
        Label(self, text='Process Name', justify='right').grid(column=0, row=row_num, sticky='nesw', padx=5, pady=5)
        self.entry_process_name = Entry(self, width=20, justify='center')
        self.entry_process_name.grid(column=1, row=row_num, columnspan=4, sticky='nesw', padx=5 ,pady=5)

        row_num += 1
        Label(self, text='CMD Line Detail', justify='right').grid(column=0, row=row_num, sticky='nesw', padx=5, pady=5)
        self.entry_cmd_line = Entry(self, width=20, justify='center')
        self.entry_cmd_line.grid(column=1, row=row_num, columnspan=4, sticky='nesw', padx=5, pady=5)

        row_num += 1
        Label(self, text='Process Path', justify='right').grid(column=0, row=row_num, sticky='nesw', padx=5, pady=5)
        self.entry_process_path = Entry(self, justify='left')
        self.entry_process_path.grid(column=1, row=row_num, columnspan=3, sticky='nesw', padx=(5, 0), pady=5)

        self.button_path = Button(self, text='...', width=5)
        self.button_path.grid(column=4, row=row_num, sticky='nesw', padx=(0, 5), pady=5)

        row_num += 1
        frame_button = Frame(self)
        frame_button.grid(column=0, row=row_num, columnspan=5, sticky='nse')
        frame_button.grid_columnconfigure((0, 1, 2), weight=1)
        frame_button.grid_rowconfigure(0, weight=1)
        self.button_ok = Button(frame_button, text='Ok', width=15)
        self.button_ok.grid(column=3, row=0, sticky='nesw', padx=5, pady=5)
        self.button_cancel = Button(frame_button, text='Cancel', width=15)
        self.button_cancel.grid(column=4, row=0, sticky='nesw', padx=5, pady=5)


if __name__ == '__main__':
    root = Tk()
    main_frame = Frame(root)
    main_frame.grid(column=0, row=0, sticky='nesw')
    settings = AddTreeview(main_frame)
    root.mainloop()
