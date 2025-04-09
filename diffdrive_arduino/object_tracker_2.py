#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np
import cv2
from scipy.spatial.distance import cosine
from deepface import DeepFace
import time


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        self.publisher_twist = self.create_publisher(Twist, '/diff_cont/cmd_vel_unstamped', 10)

        self.cvNet = cv2.dnn.readNetFromTensorflow('/content/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb', '/content/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        
        self.classNames = { 0: 'background',
        1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane',
        6: 'bus', 7: 'train', 8: 'truck', 9: 'boat',
        10: 'traffic light', 11: 'fire hydrant', 13: 'stop sign',
        14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat', 18: 'dog',
        19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
        24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella',
        31: 'handbag', 32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis',
        36: 'snowboard', 37: 'sports ball', 38: 'kite', 39: 'baseball bat',
        40: 'baseball glove', 41: 'skateboard', 42: 'surfboard',
        43: 'tennis racket', 44: 'bottle', 46: 'wine glass', 47: 'cup',
        48: 'fork', 49: 'knife', 50: 'spoon', 51: 'bowl', 52: 'banana',
        53: 'apple', 54: 'sandwich', 55: 'orange', 56: 'broccoli',
        57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut', 61: 'cake',
        62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
        67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
        75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave',
        79: 'oven', 80: 'toaster', 81: 'sink', 82: 'refrigerator',
        84: 'book', 85: 'clock', 86: 'vase', 87: 'scissors',
        88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush' }

        self.timer = self.create_timer(0.1, self.process_frame)
        self.cap = cv2.VideoCapture(0)
        self.w, self.h = (int(self.cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT))

        with open('/home/pfe/work/src/diffdrive_arduino/face_features/my_features.npy', 'rb') as f:
            self.reference_embeddings = np.load(f)

    def is_me(self, new_image, threshold=0.6):
        new_embedding = np.array(DeepFace.represent(img_path=new_image, model_name="Facenet", enforce_detection=False)[0]["embedding"])

        # Compute cosine similarity with all reference embeddings
        similarities = [1 - cosine(new_embedding, ref_emb) for ref_emb in self.reference_embeddings]

        # Take the highest similarity score
        max_similarity = max(similarities)

        return max_similarity > threshold, max_similarity  # Return decision & similarity score

    def process_frame(self):
        success, frame = self.cap.read()
        if not success:
            self.get_logger().warn("Failed to capture frame.")
            return
        
        rows = frame.shape[0]
        cols = frame.shape[1]
        self.cvNet.setInput(cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False))
        cvOut = self.cvNet.forward()

        # Initialize max confidence tracking
        max_score = 0
        best_detection = None

        # Find detection with highest confidence
        for detection in cvOut[0, 0, :, :]:
            score = float(detection[2])
            if score > max_score and score > 0.5:
                max_score = score
                best_detection = detection
                class_id = int(detection[1])
                class_name = self.classNames.get(class_id, 'Unknown')
                self.get_logger().info(f"Object detected : {class_name}")

        if best_detection is not None and max_score > 0.5:
            class_id = int(best_detection[1])
            class_name = self.classNames.get(class_id, 'Unknown')
            if class_name == 'person':
                result, sim_score = self.is_me(frame)
                print("Is it me?", result, "Similarity Score:", sim_score)
            # Get bounding box coordinates
            xmin = int(best_detection[3] * cols)
            ymin = int(best_detection[4] * rows)
            xmax = int(best_detection[5] * cols)
            ymax = int(best_detection[6] * rows)
            self.get_logger().info(f"Object detected : {class_name}")

            x=(xmax+xmin)/2
            y=(ymax+ymin)/2

        twist_msg = Twist()
        
        tw = False
        if x < self.w // 2 - 100:
            twist_msg.angular.z = 0.5  # Turn left
            tw = False
        elif x > self.w // 2 + 100:
            twist_msg.angular.z = -0.5  # Turn right
            tw = False
        else:
            twist_msg.angular.z = 0.0
            tw = True
        
        if tw:
            if y < self.h // 2 - 100:
                twist_msg.linear.x = 0.5  # Move forward
            elif y > self.h // 2 + 100:
                twist_msg.linear.x = -0.5  # Move backward
            else:
                twist_msg.linear.x = 0.0  # Stop
        
        self.publisher_twist.publish(twist_msg)

        time.sleep(0.5)

        twist_msg.angular.z = 0.0
        twist_msg.linear.x = 0.0

        self.publisher_twist.publish(twist_msg)

        time.sleep(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
