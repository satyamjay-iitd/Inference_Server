from ctypes import c_char_p, CDLL
from abc import abstractmethod


class IPC:
    _dll = None

    @staticmethod
    def _load_dll():
        dll_path = "IPC/mmf_wrapper/libsem.so"
        IPC._dll = CDLL(dll_path)
        IPC._dll.readMMF.restype = c_char_p

    @staticmethod
    def get_mmf(name: str, size: int):
        shm_fd = IPC._dll.shared_mem_open(bytes(name, encoding='utf-8'),
                                          IPC._dll.getO_CREAT_ORDWR())
        IPC._dll.ftrunc(shm_fd, size)
        mmf = IPC._dll.mmap_obj(size, shm_fd)
        return mmf
        # return IPC.__dll.shared_mem(bytes(name, encoding='utf-8'), size)

    @staticmethod
    def get_lock(name: str):
        return IPC._dll.semaphore_open(bytes(name, encoding='utf-8'), IPC._dll.getO_Creat(), 1)

    @staticmethod
    @abstractmethod
    def init_ipc():
        pass

    @staticmethod
    def reset():
        IPC._dll.reset()

    @staticmethod
    @abstractmethod
    def read_data() -> str:
        pass

    @staticmethod
    @abstractmethod
    def write_output(output):
        pass

    @staticmethod
    @abstractmethod
    def set_output_ready():
        pass

    @staticmethod
    @abstractmethod
    def is_output_ready() -> bool:
        pass

