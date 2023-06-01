#include <Arduino.h>
#include <MPU6050_tockn.h>
#include <SoftwareSerial.h>
#include <LinkedList.h>
#include <Wire.h>




#define PIN_Motor_PWMA 5
#define PIN_Motor_PWMB 6
#define PIN_Motor_BIN_1 8
#define PIN_Motor_AIN_1 7
#define PIN_Motor_STBY 9
#define SPEED_MAX 255
#define REF_TIME_CM 50 //(en MS)
#define AGENT_VELOCITY 30 //(en PX pour Jumeau Numérique)
#define X_REDUCT_FACTOR 10 // /10 = *0.1
#define Y_REDUCT_FACTOR 5  // /5  = *0.2








void manageMotors(int percentSpeedL, int percentSpeedR);
bool process_action();
void fonction_test();




SoftwareSerial nodeSerial(2, 3);     //RX -> PWM   |   TX -> DIGITAL
MPU6050 mpu(Wire);

// Taille de l'environnement= Simulation-> 944px * 800px  | Réel-> 188CM(944*0.2) * 80CM(800*0.1)    >> 1px= 1MM

//>>      EXEMPLE MOUVEMENT POUR 30px --> 6CM     <<
    // Mouvement Double Numérique en ligne droite= (Axe Y || Axe X)-> 30px                          >> Y= 30 * cos(0° ou 180°)= +/- 30     X= 30 * sin(90° ou -90°)= +/- 30
    // Mouvement Réel Robot en ligne droite= Axe Y-> 6CM(30*0.2) & Axe X-> 3CM(30*0.1)              
    // Mouvement Double Numérique en diagonale= Axe Y-> 21.2px & Axe X-> 21.1px                    >> Y= 30 * cos(45° ou -45°)= 21.21  X= 21.1 * sin(45° ou -45°)= +/- 21.21
    // Mouvement Réel Robot en diagonale= Axe Y-> 4.24CM(21.21*0.2) & Axe X-> 2.12CM(21.21*0.1)
String strategy= "";
bool canPathFinding= false;
unsigned long prevTime= 0;
unsigned long prevWaitTime= 0;
unsigned long prevRotationTime= 0;
unsigned long rotationTimeInterval= 10000;
int index= 0;
int target_angle= 0;
int prev_angle= 0;
bool actionFinished= false;
float *gyroData[3];
bool pathfindingFinished= false;
int action_iterator= 0;
bool isSameAction= false;
float max_accel= 0;
unsigned long i= 0;
char current_action= '6';
unsigned long time= 0;
int sL= 0;
int sR= 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  nodeSerial.begin(9600);
  mpu.begin();
  mpu.calcGyroOffsets();
  pinMode(PIN_Motor_PWMA, OUTPUT);
  pinMode(PIN_Motor_PWMB, OUTPUT);
  pinMode(PIN_Motor_AIN_1, OUTPUT);
  pinMode(PIN_Motor_BIN_1, OUTPUT);
  pinMode(PIN_Motor_STBY, OUTPUT);
  digitalWrite(PIN_Motor_AIN_1, HIGH);
  digitalWrite(PIN_Motor_BIN_1, HIGH);
  digitalWrite(PIN_Motor_STBY, LOW);
  mpu.update();
  Serial.println("");
  Serial.println("Initial Angle Z= " + String(mpu.getGyroAngleZ()));
  manageMotors(0, 0);
}




void loop() {
  // put your main code here, to run repeatedly:
  //RECUPERATION DE LA STRATEGIE VENANT DU NODEMCU
  while (nodeSerial.available() > 0) {
    Serial.println("Receive Action");
    if (pathfindingFinished == true) {
      pathfindingFinished= false;
      index= 0;
      action_iterator= 0;
      strategy= "";
    }
    strategy+= char(nodeSerial.read());
    Serial.println("Strategie= " + strategy);


  }
  if (pathfindingFinished == false && strategy.length() > 0) {
    mpu.update();
    current_action= strategy[index];
    actionFinished= process_action();
    if (actionFinished == true) {
      index++;
      actionFinished= false;
      isSameAction= false;
      if (index == strategy.length()) {
        Serial.println("Pathfinding FINISHED");
        manageMotors(0, 0);
        pathfindingFinished= true;
       
      }
    }
  }
}






bool process_action() {
  bool isFinished= false;
  float angle= mpu.getGyroAngleZ();
  if (current_action == '0') {
    //Update de l'angle cible et correction de la valeur d'angle réel
    if (isSameAction == false) {
      target_angle-= 45;
      isSameAction= true;
    }
    //Processing de la rotation
    if (round(angle) <= target_angle) {
      Serial.println("Target Angle= " + String(target_angle) + " | Real Angle= " + String(angle));
      manageMotors(0, 0);
      isSameAction= false;
      current_action= '2';
    } else if (abs(abs(round(angle)) - abs(target_angle)) > 15) {
      if (sL != 55 || sR != -55) {
        sL= 55;
        sR= -55;
        manageMotors(sL, sR);
      }
    } else {
      if (sL != 40 || sR != -40) {
        sL= 40;
        sR= -40;
        manageMotors(sL, sR);
      }
    }
  
  } else if (current_action == '1') {
    if (isSameAction == false) {
      target_angle+= 45;
      isSameAction= true;
    }
    //Processing de la rotation
    if (round(angle) >= target_angle) {
      Serial.println("Target Angle= " + String(target_angle) + " | Real Angle= " + String(angle));
      if (sL != 0 || sR != 0) {
        sL= 0;
        sR= 0;
        manageMotors(sL, sR);
      }
      isSameAction= false;
      current_action= '2';
    } else if (abs(abs(round(angle)) - abs(target_angle)) > 15) {
      if (sL != -55 || sR != 55) {
        sL= -55;
        sR= 55;
        manageMotors(sL, sR);
      }
    } else {
      if (sL != -40 || sR != 40) {
        sL= -40;
        sR= 40;
        manageMotors(sL, sR);
      }
    }
  } if (current_action == '2') {
    if (isSameAction == false) {
      prevTime= millis();
      max_accel= abs(mpu.getAccX() + mpu.getAccY());
      isSameAction= true;
    }
    float x_dist= (AGENT_VELOCITY * sin(mpu.getGyroZ()* DEG_TO_RAD)) / X_REDUCT_FACTOR;
    float y_dist= (AGENT_VELOCITY * cos(mpu.getGyroZ()* DEG_TO_RAD)) / Y_REDUCT_FACTOR;
    float final_dist= sqrt(pow(x_dist, 2) + pow(y_dist, 2));
    time= millis();
    while ((time - prevTime) < REF_TIME_CM * final_dist/ max_accel) {
      mpu.update();
      if (abs(mpu.getAccX() + mpu.getAccY()) > max_accel){
        max_accel= abs(mpu.getAccX() + mpu.getAccY());
      }
      if (angle < target_angle) {
        if (sL != 40 || sR != 55) {
          sL= 40;
          sR= 55;
          manageMotors(sL, sR);
        }
      } else if (angle > target_angle) {
        if (sL != 55 || sR != 40) {
          sL= 55;
          sR= 40;
          manageMotors(sL, sR);
        }
      } else {
        if (sL != 55 || sR != 55) {
          sL= 55;
          sR= 55;
          manageMotors(sL, sR);
        }
      }
      time= millis();
    } if (current_action == '.'){
      manageMotors(0, 0);
    }
    Serial.println("Target time= " + String(REF_TIME_CM * final_dist/ max_accel) + "ms -> Real Time elapsed= " + String(time - prevTime) + "ms | Max Accel= " + String(max_accel));
    manageMotors(0, 0);
    isFinished= true;
    isSameAction= false;
    
  }
  return isFinished;
}




void manageMotors(int percentSpeedL, int percentSpeedR){
  digitalWrite(PIN_Motor_STBY, HIGH);
  int speedL= round(percentSpeedL*2.55);
  int speedR= round(percentSpeedR*2.55);
  if((percentSpeedL > 100)){
    speedL= SPEED_MAX;
  } if ((percentSpeedL < -100)){
    speedL= -SPEED_MAX;
  }
  if((percentSpeedR > 100)){
    speedR= SPEED_MAX;
  } if ((percentSpeedR < -100)){
    speedR= -SPEED_MAX;
  }
  if (speedL == 0 && speedR == 0){
    digitalWrite(PIN_Motor_STBY, LOW);
    analogWrite(PIN_Motor_PWMA, 0);
    analogWrite(PIN_Motor_PWMB, 0);
  }


  else {
    if (speedL > 0) {
      digitalWrite(PIN_Motor_BIN_1, HIGH);
      analogWrite(PIN_Motor_PWMB, speedL);
    } else if ( speedL == 0){
      analogWrite(PIN_Motor_PWMB, 0);
      digitalWrite(PIN_Motor_BIN_1, HIGH);
    } else {
      digitalWrite(PIN_Motor_BIN_1, LOW);
      analogWrite(PIN_Motor_PWMB, abs(speedL));
    }




    if (speedR > 0) {
      digitalWrite(PIN_Motor_AIN_1, HIGH);
      analogWrite(PIN_Motor_PWMA, speedR);
    } else if ( speedR == 0){
      analogWrite(PIN_Motor_PWMA, 0);
      digitalWrite(PIN_Motor_AIN_1, HIGH);
    } else {
      digitalWrite(PIN_Motor_AIN_1, LOW);
      analogWrite(PIN_Motor_PWMA, abs(speedR));
    }
  }
}


