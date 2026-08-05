#include <Servo.h>
Servo myServo;
int servoPin = 13;
int triggerPin = 12;
int echoPin = 11;
int buttonPin = 2;
int manualYPin = A5;

void setup() {
  // put your setup code here, to run once:
  myServo.attach(servoPin);
  pinMode(triggerPin,OUTPUT);
  pinMode(echoPin,INPUT);
  pinMode(buttonPin,INPUT_PULLUP);
  pinMode(manualYPin,INPUT);
  Serial.begin(9600);
}

void initialTrigger() {
  digitalWrite(triggerPin,HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin,LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  myServo.write(0);
  int manualYVoltage = analogRead(manualYPin);
  Serial.println(manualYVoltage);
}
