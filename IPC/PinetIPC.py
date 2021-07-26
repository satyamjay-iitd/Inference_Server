from IPC.ipc import IPC

from PINET import PinetInference


class PinetIPC(IPC):
    __pinet_img_lock = None
    __pinet_output_lock = None
    __pinet_output_ready_lock = None

    __pinet_img_mmf = None
    __pinet_output_mmf = None
    __pinet_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(PinetIPC.__pinet_img_lock)
        img = IPC._dll.readMMF(PinetIPC.__pinet_img_mmf)
        IPC._dll.post(PinetIPC.__pinet_img_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(PinetIPC.__pinet_output_lock)
        IPC._dll.writeMMF(output, PinetIPC.__pinet_output_mmf)
        IPC._dll.post(PinetIPC.__pinet_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(PinetIPC.__pinet_output_ready_lock)
        IPC._dll.WriteInt(1, PinetIPC.__pinet_output_ready_mmf)
        IPC._dll.post(PinetIPC.__pinet_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(PinetIPC.__pinet_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        PinetIPC.__pinet_image_lock = IPC.get_lock("pinet_image_lock")
        PinetIPC.__pinet_output_lock = IPC.get_lock("pinet_output_lock")
        PinetIPC.__pinet_output_ready_lock = IPC.get_lock("pinet_ready_lock")

        PinetIPC.__pinet_image_mmf = IPC.get_mmf("pinet_image_mmf", 1000000)
        PinetIPC.__pinet_output_mmf = IPC.get_mmf("pinet_output_mmf", 32768)
        PinetIPC.__pinet_output_ready_mmf = IPC.get_mmf("pinet_ready_mmf", 4)

        PinetIPC.set_output_ready()
        PinetIPC.write_output(bytes(str(PinetInference()), encoding='utf-8'))

