
import logging
import numpy as np
from SensorReceiver import SensorReceiver

class LaneDetectionProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        # TODO
        pass

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        # TODO
        pass

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        # TODO
        pass

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
                inference_output.steering_angle = 0.3 * inference_output.steering_angle \
                                                  + 0.7 * old_inference.steering_angle

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
