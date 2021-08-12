import base64
from io import BytesIO
import logging

from PIL import Image
import numpy as np
from SensorReceiver import SensorReceiver
from DeterministicLaneDetection import detect_lane, DeterministicInference
from IPC import DeterministicIPC


class DeterministicLaneDetectionProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        DeterministicIPC.init_ipc()
        self.__inference: DeterministicInference = DeterministicInference()

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        self.__inference = detect_lane(img)

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        # If output has been consumed by Unity
        img = None
        if not DeterministicIPC.is_output_ready():
            img_str = DeterministicIPC.read_data()
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img = np.array(img)
        return img

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        DeterministicIPC.write_output(bytes(str(self.__inference), encoding='utf-8'))
        DeterministicIPC.set_output_ready()

    def start_message(self):
        msg = "Deterministic Lane Detection Main loop started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('Deterministic_LD')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/Deterministic_LD.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    ld = DeterministicLaneDetectionProcess(logger=logger)
    ld.run()
