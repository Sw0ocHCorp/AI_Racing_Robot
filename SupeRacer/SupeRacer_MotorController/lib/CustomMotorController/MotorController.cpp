#include "MotorController.h"

MotorController::MotorController(void) {
    pinMode(PIN_Motor_PWMA, OUTPUT);
    pinMode(PIN_Motor_PWMB, OUTPUT);
    pinMode(PIN_Motor_AIN_1, OUTPUT);
    pinMode(PIN_Motor_BIN_1, OUTPUT);
    pinMode(PIN_Motor_STBY, OUTPUT);
}

void MotorController::manageMotors(String direction, uint8_t percentSpeedL, uint8_t percentSpeedR) {
    digitalWrite(PIN_Motor_STBY, HIGH);
    uint8_t speedL= percentSpeedL*2.55;
    uint8_t speedR= percentSpeedR*2.55;
    if (percentSpeedL > 100){
            speedL= speed_Max;
    }
    if (percentSpeedR > 100) {
        speedR= speed_Max;
    }
    if (direction == "FORWARD"){
        digitalWrite(PIN_Motor_AIN_1, HIGH);
        analogWrite(PIN_Motor_PWMA, speedR);
        digitalWrite(PIN_Motor_BIN_1, HIGH);

        analogWrite(PIN_Motor_PWMB, speedL);
    } else if (direction == "BACKWARD"){
        digitalWrite(PIN_Motor_AIN_1, LOW);
        analogWrite(PIN_Motor_PWMA, speedR);
        digitalWrite(PIN_Motor_BIN_1, LOW);
        analogWrite(PIN_Motor_PWMB, speedL);
    } else if (direction == "STAND_BY"){
        analogWrite(PIN_Motor_PWMA, 0);
        analogWrite(PIN_Motor_PWMB, 0);
        digitalWrite(PIN_Motor_STBY, LOW);
    } else
    {
        analogWrite(PIN_Motor_PWMA, 0);
        analogWrite(PIN_Motor_PWMB, 0);
        digitalWrite(PIN_Motor_STBY, LOW);
        Serial.println("Moteurs Stoppés car la direction spécifiée n'est pas valide");
    }
}

MotorController::~MotorController(){

}