#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"

class ControlBridgeNode : public rclcpp::Node {
public:
    ControlBridgeNode()
        : Node("control_bridge_node") {  // Consistent naming convention
        publisher_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/forward_velocity_controller/commands", 10);
        
        subscriber_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/diff_cont/cmd_vel_unstamped", 10,
            std::bind(&ControlBridgeNode::control_callback, this, std::placeholders::_1));
    }

private:
    void control_callback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        auto command_msg = std_msgs::msg::Float64MultiArray();
        command_msg.data = {msg->angular.z, msg->linear.x};  // Example mapping
        publisher_->publish(command_msg);
    }

    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr publisher_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscriber_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ControlBridgeNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
