#include "MqttManager.h"

const char* ssid = "xxxxxxxxxxx";                                         // Nom du Point d'Acces WiFi
const char* password = "xxxxxxxxxxx";  
const char* broker = "test.mosquitto.org";                // URL du Broker Distant
unsigned long brokerPort = 1883; 
const char* strategyTopic= "xxxxxxxxxxxxxxxxxxx";
const char* feedBackTopic= "xxxxxxxxxxxxxxxxxxxxxxxxxx";
WiFiClient wifiClient;
WiFiManager wifiManager;
PubSubClient nodeClient(wifiClient);
SoftwareSerial motorSerial(D3, D4);    //RX -> PWM   |   TX -> DIGITAL 

void setupMqttConection(){
    motorSerial.begin(9600);
    setupGateway();
    String ssid = WiFi.SSID();
    String psswd = WiFi.psk();
    setupNodeClient(ssid, psswd);
    subTopic();
}

void setupNodeClient(String ssid, String password){
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while(WiFi.status() != WL_CONNECTED){     // Boucle gestion des problèmes de connexions
        delay(100);
        Serial.print(".");
    }   
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    nodeClient.setServer(broker, brokerPort);
    nodeClient.setCallback(getFinalStrategy);
    tryReconnection();
}

void tryReconnection() {
    while (!nodeClient.connected()) {
        Serial.println("Try connection to Broker...");
        if (nodeClient.connect("AI_Robot")) {
            Serial.println("Broker connection sucessfull");
        } else {
            Serial.println("Broker connection failed");
            Serial.println(nodeClient.state());
            delay(250);
        }
    }
}


void getFinalStrategy(char* topic, byte* payload, unsigned int len){
    String message((char*) payload);
    Serial.println(message);
    Serial.println("-----------------------");
    for (int i= 0; i < message.length(); i++){
        if (isdigit(message[i]))
        {
            Serial.println(message[i]);
            motorSerial.print(message[i]);
        }
        else{
            break;
        }
        
    }
    
    nodeClient.publish(feedBackTopic, "Start PathFinding");
    /*for (auto val: strategy) {
        Serial.println(val);
    }*/
}

void setupGateway() {
    wifiManager.setAPCallback(gatewayCallback);
    if (!wifiManager.autoConnect("AI_Robot")){
        Serial.println("failed to connect and hit timeout");
        ESP.reset();
        Serial.println("ERREUR DE MISE EN PLACE DE LA PLATEFORME WIFI");
        delay(1000);
    }
}

void gatewayCallback(WiFiManager *myWifiManager) {
    Serial.println("Entered config mode");
    Serial.println(WiFi.softAPIP());
    Serial.println(myWifiManager->getConfigPortalSSID());
}

void subTopic() {
    nodeClient.subscribe(strategyTopic);
}

void updateNodeClient() {
    nodeClient.loop();
}