from IPC.ipc import IPC


class YoloIPC(IPC):
    __yolo_img_lock = None
    __yolo_output_lock = None
    __yolo_output_ready_lock = None

    __yolo_img_mmf = None
    __yolo_output_mmf = None
    __yolo_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(YoloIPC.__yolo_img_lock)
        img = IPC._dll.readMMF(YoloIPC.__yolo_img_mmf)
        IPC._dll.post(YoloIPC.__yolo_img_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(YoloIPC.__yolo_output_lock)
        IPC._dll.writeMMF(output, YoloIPC.__yolo_output_mmf)
        IPC._dll.post(YoloIPC.__yolo_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(YoloIPC.__yolo_output_ready_lock)
        IPC._dll.WriteInt(1, YoloIPC.__yolo_output_ready_mmf)
        IPC._dll.post(YoloIPC.__yolo_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(YoloIPC.__yolo_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        YoloIPC.__yolo_image_lock = IPC.get_lock("yolo_image_lock")
        YoloIPC.__yolo_output_lock = IPC.get_lock("yolo_output_lock")
        YoloIPC.__yolo_output_ready_lock = IPC.get_lock("yolo_ready_lock")

        YoloIPC.__yolo_image_mmf = IPC.get_mmf("yolo_image_mmf", 1000000)
        YoloIPC.__yolo_output_mmf = IPC.get_mmf("yolo_output_mmf", 256)
        YoloIPC.__yolo_output_ready_mmf = IPC.get_mmf("yolo_ready_mmf", 4)

        YoloIPC.write_output(bytes('{"signal": "g"}', encoding='utf-8'))
        YoloIPC.set_output_ready()

