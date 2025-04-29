#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = rclcpp::Node::make_shared("nav_cmd_vel_publisher");
    auto publisher = node->create_publisher<geometry_msgs::msg::Twist>("/diff_cont/cmd_vel_unstamped", 10);

    // Give publisher time to establish connection (optional)
    rclcpp::sleep_for(std::chrono::milliseconds(100));

    float vel[6] = {0.25, 0.0, 0.25, 0.5, 0.9, 0.5};
    
    int len = sizeof(vel) / sizeof(vel[0]);
    
    geometry_msgs::msg::Twist msg;
    
    msg.linear.y = 0.0;
    msg.linear.z = 0.0;
    msg.angular.x = 0.0;
    msg.angular.y = 0.0;
    
    for(int i = 0; i < len; i += 2){

    	msg.linear.x = vel[i];
    	msg.angular.z = vel[i+1];

   	RCLCPP_INFO(node->get_logger(), "Publishing commands to /diff_cont/cmd_vel_unstamped : [%f, %f]", msg.linear.x, msg.angular.z);


    	publisher->publish(msg);
    	
    	rclcpp::sleep_for(std::chrono::milliseconds(500));
    
    }

    rclcpp::shutdown();
    return 0;
}

