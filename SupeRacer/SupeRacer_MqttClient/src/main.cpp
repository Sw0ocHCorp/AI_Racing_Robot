#include <Arduino.h>
#include "MqttManager.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  setupMqttConection();
}

void loop() {
  // put your main code here, to run repeatedly:
  updateNodeClient();
  
}