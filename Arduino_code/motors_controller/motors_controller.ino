void setup() {
 // initialize serial communication at 9600 bits per second:
  Serial.begin(57600);
  Serial.println("Hello from Arduino");
  int in1=3;
  int in2=5;
  int in3=6;
  int in4=9;
  int ena=10;
  int enb=11;
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(ena, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n');
    Serial.println(received);
    String command, value1, value2;
    int firstSpace = received.indexOf(' ');  // Find first space
    int secondSpace = received.indexOf(' ', firstSpace + 1);  // Find second space
    // Error handling for unexpected formats
    if (firstSpace == -1 || secondSpace == -1) {
      Serial.println("Error: Invalid command format");
      return;
    }
    command = received.substring(0,firstSpace);
    value1 = received.substring(firstSpace + 1, secondSpace);
    value2 = received.substring(secondSpace + 1);
    int value1Int = value1.toInt();
    int value2Int = value2.toInt();
    if(command=="m"){
    if(value1Int >= 0 and value2Int >= 0){
      Serial.println("CASE 1");
      analogWrite(10,value1Int);
      digitalWrite(3,HIGH);
      digitalWrite(5,LOW);
      analogWrite(11,value2Int);
      digitalWrite(6,HIGH);
      digitalWrite(9,LOW);
    }
    else if(value1Int >= 0 and value2Int < 0){
      Serial.println("CASE 2");
      analogWrite(10,value1Int);
      digitalWrite(3,HIGH);
      digitalWrite(5,LOW);
      analogWrite(11,-value2Int);
      digitalWrite(6,LOW);
      digitalWrite(9,HIGH);
    }
    else if(value1Int < 0 and value2Int >= 0){
      Serial.println("CASE 3");
      analogWrite(10,-value1Int);
      digitalWrite(3,LOW);
      digitalWrite(5,HIGH);
      analogWrite(11,value2Int);
      digitalWrite(6,HIGH);
      digitalWrite(9,LOW);
    }
    else{
      Serial.println("CASE 4");
      analogWrite(10,-value1Int);
      digitalWrite(3,LOW);
      digitalWrite(5,HIGH);
      analogWrite(11,-value2Int);
      digitalWrite(6,LOW);
      digitalWrite(9,HIGH);
    }
   }
  }
}
