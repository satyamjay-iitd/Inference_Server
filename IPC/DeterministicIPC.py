from IPC.ipc import IPC
from DeterministicLaneDetection.LaneDetection import DeterministicInference


class DeterministicIPC(IPC):
    __deterministic_img_lock = None
    __deterministic_output_lock = None
    __deterministic_output_ready_lock = None

    __deterministic_img_mmf = None
    __deterministic_output_mmf = None
    __deterministic_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(DeterministicIPC.__deterministic_img_lock)
        img = IPC._dll.readMMF(DeterministicIPC.__deterministic_img_mmf)
        IPC._dll.post(DeterministicIPC.__deterministic_img_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(DeterministicIPC.__deterministic_output_lock)
        IPC._dll.writeMMF(output, DeterministicIPC.__deterministic_output_mmf)
        IPC._dll.post(DeterministicIPC.__deterministic_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(DeterministicIPC.__deterministic_output_ready_lock)
        IPC._dll.WriteInt(1, DeterministicIPC.__deterministic_output_ready_mmf)
        IPC._dll.post(DeterministicIPC.__deterministic_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(DeterministicIPC.__deterministic_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        DeterministicIPC.__deterministic_image_lock = IPC.get_lock("deterministic_image_lock")
        DeterministicIPC.__deterministic_output_lock = IPC.get_lock("deterministic_output_lock")
        DeterministicIPC.__deterministic_output_ready_lock = IPC.get_lock("deterministic_ready_lock")

        DeterministicIPC.__deterministic_image_mmf = IPC.get_mmf("deterministic_image_mmf", 1000000)
        DeterministicIPC.__deterministic_output_mmf = IPC.get_mmf("deterministic_output_mmf", 32768)
        DeterministicIPC.__deterministic_output_ready_mmf = IPC.get_mmf("deterministic_ready_mmf", 4)

        DeterministicIPC.set_output_ready()
        DeterministicIPC.write_output(bytes(str(DeterministicInference()), encoding='utf-8'))