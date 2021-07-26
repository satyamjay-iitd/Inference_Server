import base64
from io import BytesIO
import logging
import json

from PIL import Image
import numpy as np

from IPC import YoloIPC
from SensorReceiver import SensorReceiver
from YOLO.traffic_light_detection import get_traffic_light_status


class YoloTrafficDetection(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        YoloIPC.init_ipc()
        self.__detected_color = "g"

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        self.__detected_color = get_traffic_light_status(img)

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        # If output has been consumed by Unity
        img = None
        if not YoloIPC.is_output_ready():
            img_str = YoloIPC.read_data()
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img = np.array(img)
        return img

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        output_json = {"signal": self.__detected_color}
        YoloIPC.write_output(bytes(json.dumps(output_json), encoding='utf-8'))
        YoloIPC.set_output_ready()

    def start_message(self):
        msg = "Signal Detection Main loop started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('YOLO_TD')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/YOLO_TD.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    td = YoloTrafficDetection(logger=logger)
    td.run()

