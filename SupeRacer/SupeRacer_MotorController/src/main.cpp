#include <Arduino.h>
#include "MotorController.h"
#include <SoftwareSerial.h>
#include <LinkedList.h>

MotorController motorControler;
SoftwareSerial nodeSerial(2, 3);     //RX -> PWM   |   TX -> DIGITAL 
String strategy= "";
bool canPrint= false;
unsigned long prevTime= 0;
int index= 0;
int speedLeft= 100;
int speedRight= 100;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  nodeSerial.begin(9600);
  motorControler= MotorController();
}

void loop() {
  // put your main code here, to run repeatedly:
  while (nodeSerial.available()) {
    if ((millis() - prevTime) > 1000) {
      char action= char(nodeSerial.read());
      Serial.println(action);
      if (action == '2') {
        speedLeft= 100;
        speedRight= 100;
      } else if (action == '0') {
        speedLeft= 100;
        speedRight= 0;
      } else if (action == '1') {
        speedLeft= 0;
        speedRight= 100;
      } 
      motorControler.manageMotors("FORWARD", speedLeft, speedRight);
      index++;
      prevTime= millis();
    }
  }

  
  
}

