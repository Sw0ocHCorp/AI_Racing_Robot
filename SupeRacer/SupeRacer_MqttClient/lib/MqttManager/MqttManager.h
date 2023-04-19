#ifndef MqttManager_H_
#define MqttManager_H_

#include <Arduino.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>
#include <ESP8266mDNS.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <list>
#include <string>
#include <SoftwareSerial.h>

void setupMqttConection();
void setupNodeClient(String ssid, String password);
void getFinalStrategy(char* topic, byte* payload, unsigned int len);
void setupGateway();
void gatewayCallback(WiFiManager *myWifiManager);
void updateNodeClient();
void subTopic();
void sendFeedBack(const char *fdbck);
void tryReconnection();

#endif