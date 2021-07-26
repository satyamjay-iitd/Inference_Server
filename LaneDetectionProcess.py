import base64
from io import BytesIO
import logging

from PIL import Image
import numpy as np

from IPC import PinetIPC
from PINET import inference, get_homography_matrix, get_lane_agent, PinetInference
from SensorReceiver import SensorReceiver


class LaneDetectionProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        PinetIPC.init_ipc()
        self.__lane_detection_agent = get_lane_agent()
        _, self.__homography_matrix = get_homography_matrix()
        self.__inference: PinetInference = PinetInference()

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        raw_inference = inference(self.__lane_detection_agent, img, self.__homography_matrix)
        self.__inference = self.__post_process_lane_inference(raw_inference, self.__inference)

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        # If output has been consumed by Unity
        img = None
        if not PinetIPC.is_output_ready():
            img_str = PinetIPC.read_data()
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img = np.array(img)
        return img

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        PinetIPC.write_output(bytes(str(self.__inference), encoding='utf-8'))
        PinetIPC.set_output_ready()

    @staticmethod
    def __post_process_lane_inference(inference_output, old_inference):
        """
        Performs weighted average of previous steering angle and current steering angle
        :param inference_output: Current Inference output
        :param old_inference:    Output of previous Inference
        :return: None
        """
        if inference_output.steering_angle != -100:
            if inference_output.steering_angle in (10, -10):
                pass
            elif abs(old_inference.steering_angle) <= 1:
                inference_output.steering_angle = 0
            else:
                # Weighted average of steering angle to remove noise
                inference_output.steering_angle = 0.3*inference_output.steering_angle\
                                                  + 0.7*old_inference.steering_angle

        return inference_output

    def start_message(self):
        msg = "Lane Detection Main loop started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('PINET_LD')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/PINET_LD.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    ld = LaneDetectionProcess(logger=logger)
    ld.run()

