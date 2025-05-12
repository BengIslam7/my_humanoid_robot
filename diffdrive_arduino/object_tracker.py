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
import tensorflow as tf


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')

        self.interpreter = tf.lite.Interpreter(model_path='/home/pfe/work/src/diffdrive_arduino/models/MobileNet-SSD-V3.tflite')
        self.interpreter.allocate_tensors()
        
        self.publisher_twist = self.create_publisher(Twist, '/diff_cont/cmd_vel_unstamped', 10)

	    # Get input and output tensors
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.classNames = {
        0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
        4: "airplane", 5: "bus", 6: "train", 7: "truck",
        8: "boat", 9: "traffic light", 10: "fire hydrant", 11: "stop sign",
        12: "parking meter", 13: "bench", 14: "bird", 15: "cat",
        16: "dog", 17: "horse", 18: "sheep", 19: "cow",
        20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe",
        24: "backpack", 25: "umbrella", 26: "handbag", 27: "tie",
        28: "suitcase", 29: "frisbee", 30: "skis", 31: "snowboard",
        32: "sports ball", 33: "kite", 34: "baseball bat", 35: "baseball glove",
        36: "skateboard", 37: "surfboard", 38: "tennis racket", 39: "bottle",
        40: "wine glass", 41: "cup", 42: "fork", 43: "knife",
        44: "spoon", 45: "bowl", 46: "banana", 47: "apple",
        48: "sandwich", 49: "orange", 50: "broccoli", 51: "carrot",
        52: "hot dog", 53: "pizza", 54: "donut", 55: "cake",
        56: "chair", 57: "couch", 58: "potted plant", 59: "bed",
        60: "dining table", 61: "toilet", 62: "tv", 63: "laptop",
        64: "mouse", 65: "remote", 66: "keyboard", 67: "cell phone",
        68: "microwave", 69: "oven", 70: "toaster", 71: "sink",
        72: "refrigerator", 73: "book", 74: "clock", 75: "vase",
        76: "scissors", 77: "teddy bear", 78: "hair drier", 79: "toothbrush"
        }


        self.timer = self.create_timer(0.1, self.process_frame)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
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
        
        input_shape = self.input_details[0]['shape']
        
        img_resized=cv2.resize(frame,(input_shape[2],input_shape[1]))

        self.interpreter.set_tensor(self.input_details[0]['index'], img_resized.reshape(1, input_shape[1], input_shape[2], input_shape[3]))  # Set the resized image as input
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]        
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]     
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]   
        num_detections = int(self.interpreter.get_tensor(self.output_details[3]['index'])[0])

        width = frame.shape[1]
        height = frame.shape[0]

        max_score=0
        max_score_index= None

        for i in range(num_detections):
            if scores[i] >= 0.5:
                if scores[i] > max_score:
                    max_score = scores[i]
                    max_score_index = i
                ymin, xmin, ymax, xmax = boxes[i]
                left = int(xmin * width)
                top = int(ymin * height)
                right = int(xmax * width)
                bottom = int(ymax * height)
                class_id = int(classes[i])
                self.get_logger().info(f"Object Detected: {self.classNames[class_id]}, Confidence: {scores[i]}")
                if class_id == 0:
                    result, score = self.is_me(frame)
                    self.get_logger().info(f"Is it me? {result}, Similarity Score: {score}")

        if max_score_index is not None:
            ymin, xmin, ymax, xmax = boxes[max_score_index]
            left = int(xmin * width)
            top = int(ymin * height)
            right = int(xmax * width)
            bottom = int(ymax * height)
            class_id = int(classes[max_score_index])
            x=(left + right) / 2
            y=(top + bottom) / 2

            twist_msg = Twist()
        
            tw = False
            if x < self.w // 2 - 30:
                twist_msg.angular.z = 0.5  # Turn left
                tw = False
            elif x > self.w // 2 + 30:
                twist_msg.angular.z = -0.5  # Turn right
                tw = False
            else:
                twist_msg.angular.z = 0.0
                tw = True
        
            if tw:
                if y < self.h // 2 - 30:
                    twist_msg.linear.x = 0.5  # Move forward
                elif y > self.h // 2 + 30:
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
