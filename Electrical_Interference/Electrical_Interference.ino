#include <Servo.h>
Servo myServo;
int servoPin = 13;
int triggerPin = 12;
int echoPin = 11;
int buttonPin = 2;
int manualYPin = A5;
int servoAngle = 0;
float distance;
int toggle = 0;
int currentButtonState;
int previousButtonState = 1;
int automaticSweepTime = 10800.0; //60 * 180Minimum time required for one distance calculation per angle (sync). 
int sweepDirection = 1;
unsigned long currentTime;
unsigned long previousTimeTrigger = 0;
unsigned long previousTimeAutoRadar = 0;
int powerRailVoltage = A0;

void setup() {
  // put your setup code here, to run once:
  myServo.attach(servoPin);
  pinMode(triggerPin,OUTPUT);
  pinMode(echoPin,INPUT);
  pinMode(buttonPin,INPUT_PULLUP);
  pinMode(manualYPin,INPUT);
  pinMode(powerRailVoltage,INPUT);
  Serial.begin(115200);
}

// This sends the initial voltage spike so the ultrasonic sensor sends its 8 bursts. 
void initialTrigger() {
  digitalWrite(triggerPin,HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin,LOW);
}

// Measures time taken for waves to return, then calculates distance in cm. 
float captureDistance() {
  initialTrigger();
  float timeTaken = pulseIn(echoPin,HIGH,23500);
  float someDistance = (0.0343 * timeTaken) / 2.0;
  return someDistance;
}

void serialPrinter() {
  Serial.print(distance);
  Serial.print(",");
  Serial.println(analogRead(powerRailVoltage));
}

// If toggle on, then servo manually controlled with joystick, if toggle off then automatically sweeps the range. 
void toggleButton() {
  currentButtonState = digitalRead(buttonPin);
  if (currentButtonState == 1 && previousButtonState == 0) {
    toggle = !toggle;
  }
  previousButtonState = currentButtonState;
}

void loop() {
  // put your main code here, to run repeatedly:
  currentTime = millis();
  toggleButton();
  if ((currentTime - previousTimeTrigger) > 60) {
    distance = captureDistance();
    previousTimeTrigger = currentTime;
    serialPrinter();
  }
  myServo.write(servoAngle);
  if (!toggle) {
    int manualYVoltage = analogRead(manualYPin);
    servoAngle = map(manualYVoltage,0,1023,0,180);
  }
  else {
    if ((currentTime - previousTimeAutoRadar) > (automaticSweepTime / 181.0)) {
      servoAngle += sweepDirection;
      if (servoAngle == 180 || servoAngle == 0) {
        sweepDirection = -sweepDirection;
      }
      previousTimeAutoRadar = currentTime;
    }
  }  
}