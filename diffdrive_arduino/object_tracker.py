#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np
import supervision as sv
from ultralytics import YOLO
import cv2


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        self.publisher_twist = self.create_publisher(Twist, '/diff_cont/cmd_vel_unstamped', 10)

        self.model = YOLO('/home/pfe/work/src/diffdrive_arduino/models/yolov9e_int8.tflite')
        
        self.timer = self.create_timer(0.1, self.process_frame)
        self.cap = cv2.VideoCapture(0)
        self.w, self.h = (int(self.cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT))
    
    def process_frame(self):
        success, frame = self.cap.read()
        if not success:
            self.get_logger().warn("Failed to capture frame.")
            return
        
        results = self.model(frame, imgsz=640)[0]
        detections = sv.Detections.from_yolov8(results)
        
        if len(detections.xyxy) == 0:
            self.get_logger().info("No detections")
            return
        
        max_conf_index = np.argmax(detections.confidence)
        
        classes = self.model.names
        for x in detections.class_id:
            self.get_logger().info("Object Detected : "+classes[x])
            

        x = (detections.xyxy[max_conf_index][0] + detections.xyxy[max_conf_index][2]) / 2
        y = (detections.xyxy[max_conf_index][1] + detections.xyxy[max_conf_index][3]) / 2
        
        self.get_logger().info(f"Object tracked : {classes[detections.class_id[max_conf_index]]}, X = {x}, Y = {y}, Confidence = {detections.confidence[max_conf_index]}")
        
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
