#ifndef MOTORCONTROLLER_H_
#define MOTORCONTROLLER_H_
#include <Arduino.h>

#define PIN_Motor_PWMA 5
#define PIN_Motor_PWMB 6
#define PIN_Motor_BIN_1 8
#define PIN_Motor_AIN_1 7
#define PIN_Motor_STBY 9
#define speed_Max 255

class MotorController
{
private:
    /* data */
public:
    MotorController(/* args */);
    void manageMotors(String direction, uint8_t percentSpeedL, uint8_t percentSpeedR);
    ~MotorController();
};

#endif