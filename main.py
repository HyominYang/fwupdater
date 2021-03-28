import serial
import serial.tools.list_ports
import sys
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from fork_py_ymodem.YModem import YModem


def send_fw_file(port, fpath):
    # connec to a serial-port
    with serial.serial_for_url(port.device, 115200, timeout=1) as handle:
        print("send reboot")
        handle.write(b'20210322rbtfw\r')
        # handle.close()

        # time.sleep(0.5)

        # with serial.serial_for_url(port.device, 115200, timeout=3) as handle:
        ch = handle.read(17)
        if ch == b'20210322updatefw\r':
            handle.write(b'20210322hasfw\r')
        else:
            print("read error")
            print(ch)
            sys.exit(0)

    with serial.serial_for_url(port.device, 115200, timeout=3) as handle:
        def sender_getc(size):
            return handle.read(size) or None

        def sender_putc(data, timeout=15):
            return handle.write(data)

        sender = YModem(sender_getc, sender_putc)
        sender.send_file(fpath)
        handle.close()
        #
        # while True:
        #     byte = handle.read()
        #     print("code: ", byte, ", ascii: ", byte.decode("ascii"))
        #     if byte == b'C':
        #         print("read 'C'")


def get_port_list():
    return serial.tools.list_ports.comports()


class UserInterface:
    def __init__(self):
        super().__init__()
        self.gui = tkinter.Tk(className="Firmware Updater")
        self.gui.geometry("345x90")
        self.string_firmware_fpath = tkinter.StringVar()
        self.label_firmware_fpath = tkinter.Label(self.gui, text="firmware :")
        self.label_firmware_fpath.grid(column=0, row=0, ipadx=5, ipady=10)
        self.textbox_firmware_fpath = tkinter.Entry(self.gui, textvariable=self.string_firmware_fpath, width=25, state="readonly")
        self.textbox_firmware_fpath.grid(column=1, row=0, padx=5)

        self.combobox_port_list = tkinter.ttk.Combobox(self.gui, height=15, state="readonly", postcommand=self.port_changed)
        self.combobox_port_list.grid(column=0, columnspan=2, row=1, sticky=tkinter.W + tkinter.E, padx=5)

        self.port_list = get_port_list()
        self.port_name_list = []
        for port_info in self.port_list:
            self.port_name_list.append(port_info.name)
        self.combobox_port_list['values'] = self.port_name_list;
        if len(self.port_name_list) > 0:
            self.combobox_port_list.current(0)

        self.button_open_filedialog = tkinter.Button(self.gui, text="Open", width=10, command=self.open_file)
        self.button_open_filedialog.grid(column=2, row=0)
        self.button_write_firmware = tkinter.Button(self.gui, text="Write", width=10, command=self.write_firmware)
        self.button_write_firmware.grid(column=2, row=1)

        self.firmware_fpath = ""

    def __new__(cls):
        return super().__new__(cls)

    def port_changed(self):
        index = self.combobox_port_list.current()
        print("selected port: ", self.port_list[index])

    def open_file(self):
        self.firmware_fpath = tkinter.filedialog.askopenfilename(initialdir="c:", title="select a firmware-file")
        self.string_firmware_fpath.set(self.firmware_fpath)

    def write_firmware(self):
        print("fpath: ", self.firmware_fpath)
        if len(self.firmware_fpath) == 0:
            tkinter.messagebox.showerror("write error", "파일이 없거나 잘못 되었습니다.")
        else:
            send_fw_file(self.port_list[self.combobox_port_list.current()], self.firmware_fpath)
            tkinter.messagebox.showinfo("End", "전송 완료.")

    def run(self):
        self.gui.mainloop()


ui = UserInterface()
ui.run()

sys.exit(0)


