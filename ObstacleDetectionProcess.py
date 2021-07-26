import base64
from io import BytesIO
import logging
import json

import cv2
from PIL import Image
import numpy as np
from skimage import morphology

from IPC import LidarIPC
from SensorReceiver import SensorReceiver


# obstacle class storing information for each object
class Obstacle:
    sx = (293 - 217) / 2
    sy = (252 - 176) / 2
    mat_car = np.array([[255.71868789, 356.86626215], ]*4)

    def __init__(self, bb):
        bb = bb*self.sx + self.mat_car
        self.center = (np.sum(bb[:, 0]).item() / 4, np.sum(bb[:, 1]).item() / 4)  # calculating centroid for object
        self.bb = bb  # bounding box for the object 4 coordinates of vertices
        self.y_max = np.max(bb[:, 1]).item()  # y-value nearest to the self-driving car

    def __dict__(self):
        d = {
            'Center': self.center,
            'Bbox':   self.bb.tolist(),
            'YMax':   self.y_max,
        }
        return d


class ObstacleDetectionProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        LidarIPC.init_ipc()
        logger.info(LidarIPC.is_output_ready())
        self.obstacles = []

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        selem = np.ones((3, 3), dtype='bool')
        res = 0.5
        count = 2
        img = img == 255    # image binarification
        img = img[:, :, 0]  # image binarification
        img[img.shape[0] // 2, img.shape[1] // 2] = 0  # image binarification
        img = morphology.binary_closing(img, selem)    # image closing
        img2 = np.zeros(img.shape, dtype='int32')
        img2[img] = 1
        yn, xn = np.nonzero(img2)  # getting non-zero pixels
        min_arr_x = []
        min_arr_y = []
        max_arr_x = []
        max_arr_y = []
        # BFS on image to find connected components
        for i in range(xn.shape[0]):
            if img2[yn[i], xn[i]] == 1:
                qu = [(xn[i], yn[i])]
                img2[yn[i], xn[i]] = count
                min_arr_x.append(xn[i])
                min_arr_y.append(yn[i])
                max_arr_x.append(xn[i])
                max_arr_y.append(yn[i])
                ind = count - 2
                while len(qu) > 0:
                    curr = qu.pop(0)
                    p = curr[0] + 1
                    q = curr[1] + 1
                    if p < img2.shape[1] and q < img2.shape[0] and img2[q, p] == 1:
                        img2[q, p] = count
                        qu.append((p, q))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                    p = curr[0] - 1
                    q = curr[1] - 1
                    if p >= 0 and q >= 0 and img2[q, p] == 1:
                        img2[q, p] = count
                        qu.append((p, q))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                    q = curr[1] - 1
                    if q >= 0 and img2[q, curr[0]] == 1:
                        img2[q, curr[0]] = count
                        qu.append((curr[0], q))
                        max_arr_x[ind] = max(curr[0], max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(curr[0], min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                    p = curr[0] - 1
                    if p >= 0 and img2[curr[1], p] == 1:
                        img2[curr[1], p] = count
                        qu.append((p, curr[1]))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(curr[1], max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(curr[1], min_arr_y[ind])
                    p = curr[0] + 1
                    q = curr[1] - 1
                    if p < img.shape[1] and q >= 0 and img2[q, p] == 1:
                        img2[q, p] = count
                        qu.append((p, q))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                    p = curr[0] - 1
                    q = curr[1] + 1
                    if p >= 0 and q < img.shape[0] and img2[q, p] == 1:
                        img2[q, p] = count
                        qu.append((p, q))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                    p = curr[0] + 1
                    if p < img.shape[1] and img2[curr[1], p] == 1:
                        img2[curr[1], p] = count
                        qu.append((p, curr[1]))
                        max_arr_x[ind] = max(p, max_arr_x[ind])
                        max_arr_y[ind] = max(curr[1], max_arr_y[ind])
                        min_arr_x[ind] = min(p, min_arr_x[ind])
                        min_arr_y[ind] = min(curr[1], min_arr_y[ind])
                    q = curr[1] + 1
                    if q < img.shape[0] and img2[q, curr[0]] == 1:
                        img2[q, curr[0]] = count
                        qu.append((curr[0], q))
                        max_arr_x[ind] = max(curr[0], max_arr_x[ind])
                        max_arr_y[ind] = max(q, max_arr_y[ind])
                        min_arr_x[ind] = min(curr[0], min_arr_x[ind])
                        min_arr_y[ind] = min(q, min_arr_y[ind])
                count += 1
        i = count - 3
        bboxes = []
        # finding the tightest bounding box for each connected component
        while i >= 0:
            yp, xp = np.nonzero(img2[min_arr_y[i]:max_arr_y[i] + 1, min_arr_x[i]:max_arr_x[i] + 1])
            yp = yp + min_arr_y[i]
            xp = xp + min_arr_x[i]
            cnt = np.concatenate((xp[:, np.newaxis], yp[:, np.newaxis]), axis=1)
            rect = cv2.minAreaRect(cnt)  # finds convex hull and minimum area bounding box
            box = cv2.boxPoints(rect)    # obtains vertices from output of cv2.minAreaRect
            bboxes.append(box)
            i -= 1

        # convert from bird's eye view back to 3D LIDAR  coordinates
        bboxes = (np.array(bboxes) - img2.shape[0] / 2) * res
        bboxes = list(map(Obstacle, bboxes))
        self.obstacles = bboxes

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        img = None
        if not LidarIPC.is_output_ready():
            img_str = LidarIPC.read_data()
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img = np.array(img)
        return img

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        LidarIPC.write_output(bytes(json.dumps([ob.__dict__() for ob in self.obstacles]), encoding='utf-8'))
        LidarIPC.set_output_ready()

    def start_message(self):
        msg = "Object Detection Main loop started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('LIDAR_OD')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/LIDAR_OD.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    od = ObstacleDetectionProcess(logger=logger)
    od.run()
