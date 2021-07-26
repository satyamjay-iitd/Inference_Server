from IPC.ipc import IPC


class LidarIPC(IPC):
    __lidar_img_lock = None
    __lidar_output_lock = None
    __lidar_output_ready_lock = None

    __lidar_img_mmf = None
    __lidar_output_mmf = None
    __lidar_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(LidarIPC.__lidar_img_lock)
        img = IPC._dll.readMMF(LidarIPC.__lidar_img_mmf)
        IPC._dll.post(LidarIPC.__lidar_img_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(LidarIPC.__lidar_output_lock)
        IPC._dll.writeMMF(output, LidarIPC.__lidar_output_mmf)
        IPC._dll.post(LidarIPC.__lidar_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(LidarIPC.__lidar_output_ready_lock)
        IPC._dll.WriteInt(1, LidarIPC.__lidar_output_ready_mmf)
        IPC._dll.post(LidarIPC.__lidar_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(LidarIPC.__lidar_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        LidarIPC.__lidar_image_lock = IPC.get_lock("lidar_image_lock")
        LidarIPC.__lidar_output_lock = IPC.get_lock("lidar_output_lock")
        LidarIPC.__lidar_output_ready_lock = IPC.get_lock("lidar_ready_lock")

        LidarIPC.__lidar_image_mmf = IPC.get_mmf("lidar_image_mmf", 1000000)
        LidarIPC.__lidar_output_mmf = IPC.get_mmf("lidar_output_mmf", 65536)
        LidarIPC.__lidar_output_ready_mmf = IPC.get_mmf("lidar_ready_mmf", 4)

        LidarIPC.write_output(bytes('[]', encoding='utf-8'))
        LidarIPC.set_output_ready()

