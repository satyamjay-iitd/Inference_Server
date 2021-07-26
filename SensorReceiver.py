from abc import ABC, abstractmethod
from logging import Logger, INFO


class SensorReceiver(ABC):
    """
    This abstract class defines interface to receive sensor data from client, process it and send it to "DataStore".
    To add new sensor receiver, one simply needs to implement its abstract methods.
    Note than SensorReceiver inherits multiprocessing.Processing.
    Each SensorReceiver is a process."
    Both these objects are shared by all the SensorReceiverProcesses.
    """
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger: Logger = logger

    @abstractmethod
    def read_data(self) -> any:
        """
        Read data using IPC interface.

        :return: Data read, can be of any type.
        """
        pass

    @abstractmethod
    def process_data(self, data) -> None:
        """
        Process the data received. This will vary widely with type of sensor we are dealing with.

        :param data: Data that is returned by :meth:`read_data`
        :return: Analysis of the data received.
        """
        pass

    @abstractmethod
    def send_data(self) -> None:
        """
        Send the data after processing to DataStore
        """
        pass

    @abstractmethod
    def start_message(self) -> str:
        """
        Message to show before starting main loop
        """
        pass

    def run(self) -> None:
        """
        Main function of the process, runs indefinitely.
        Call routines in following order: -
        read_data -> process_data -> send_to_store
        """
        self.logger.log(msg=self.start_message(), level=INFO)
        self.logger.log(msg="Establishing connection with IPC layer", level=INFO)
        while True:
            data = self.read_data()
            if data is not None:
                self.process_data(data)
                self.send_data()
