#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#define OLED128X64_PIN_RST	8
#define OLED128X64_PIN_DC	7
#define OLED128X64_PIN_CS	6
#define BUTTON1 9
#define BUTTON2 10
#define BUTTON3 11
#define BUTTON4 12
#define startBUTTON 13  
#define TRIG_FRONT 2
#define ECHO_FRONT 0

#define TRIG_RIGHT 5
#define ECHO_RIGHT 4
BluetoothSerial SerialBT;
Adafruit_MPU6050 mpu;
int s =0;
float yaw = 0;
float pitch = 0;
float roll = 0;

unsigned long lastTime;


void setup() {
  Serial.begin(115200);
    Wire.begin(21, 22);
  SerialBT.begin("Headset");
    pinMode(TRIG_FRONT, OUTPUT);
    pinMode(ECHO_FRONT, INPUT);

    pinMode(TRIG_RIGHT, OUTPUT);
    pinMode(ECHO_RIGHT, INPUT);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  pinMode(BUTTON3, INPUT_PULLUP);
  pinMode(BUTTON4, INPUT_PULLUP);
  pinMode(startBUTTON, INPUT_PULLUP);




  if (!mpu.begin()) {
    Serial.println("MPU6050 NOT FOUND!");
    while (1) {
      delay(10);
    }
  }


  Serial.println("MPU6050 READY");


  // Settings
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);


  lastTime = millis();
}

void checkmpu(){
    sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;


  mpu.getEvent(&accel, &gyro, &temp);



  // Time difference
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  lastTime = now;



  // Convert gyro from rad/s to degrees/s

  float gyroX = gyro.gyro.x * 57.2958;
  float gyroY = gyro.gyro.y * 57.2958;
  float gyroZ = gyro.gyro.z * 57.2958;



  // Calculate angles

  roll  += gyroX * dt;
  pitch += gyroY * dt;
  yaw   += gyroZ * dt;



  // Keep yaw between 0 and 360

  if (yaw >= 360)
    yaw -= 360;

  if (yaw < 0)
    yaw += 360;



  // Print acceleration


  Serial.print("Acceleration X: ");
  Serial.println(accel.acceleration.x);

  Serial.print("Acceleration Y: ");
  Serial.println(accel.acceleration.y);

  Serial.print("Acceleration Z: ");
  Serial.println(accel.acceleration.z);



  // Print rotation

  Serial.print("Yaw: ");
  Serial.print(yaw);
  Serial.println(" deg");


  Serial.print("Pitch: ");
  Serial.print(pitch);
  Serial.println(" deg");


  Serial.print("Roll: ");
  Serial.print(roll);
  Serial.println(" deg");


  SerialBT.print("Acceleration X, ");
  SerialBT.println(accel.acceleration.x);

  SerialBT.print("Acceleration Y, ");
  SerialBT.println(accel.acceleration.y);

  SerialBT.print("Acceleration Z, ");
  SerialBT.println(accel.acceleration.z);





  SerialBT.print("Yaw, ");
  SerialBT.print(yaw);
  SerialBT.println(", deg");


  SerialBT.print("Pitch, ");
  SerialBT.print(pitch);
  SerialBT.println(", deg");


  SerialBT.print("Roll, ");
  SerialBT.print(roll);
  SerialBT.println(", deg");


  // Jump detection

  float totalAcceleration =
    sqrt(
      accel.acceleration.x * accel.acceleration.x +
      accel.acceleration.y * accel.acceleration.y +
      accel.acceleration.z * accel.acceleration.z
    );


  if (totalAcceleration > 18) {
    Serial.println("JUMP DETECTED!");
  }



  // Movement detection

  if (
    abs(accel.acceleration.x) > 3 ||
    abs(accel.acceleration.y) > 3 ||
    abs(accel.acceleration.z - 9.8) > 3
  ) {
    Serial.println("MOVING");
  }
  else {
    Serial.println("STILL");
  }



  delay(100);
}
void checkstart(){
    if(digitalRead(startBUTTON) == LOW){
    if (s==0){
        s = 1;
        SerialBT.println("start");
    }
    else{
        s = 0;
        SerialBT.println("stop");
    }
    delay(200);

  }

}

void checkButtons(){

  if(digitalRead(BUTTON1) == LOW){
    SerialBT.println("BUTTON,1");
    delay(200);
  }


  if(digitalRead(BUTTON2) == LOW){
    SerialBT.println("BUTTON,2");
    delay(200);
  }


  if(digitalRead(BUTTON3) == LOW){
    SerialBT.println("BUTTON,3");
    delay(200);
  }


  if(digitalRead(BUTTON4) == LOW){
    SerialBT.println("BUTTON,4");
    delay(200);
  }

}
float getDistance(int trigPin, int echoPin){

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);


  long duration = pulseIn(echoPin, HIGH, 30000);


  float distance = duration * 0.0343 / 2;


  return distance;
}
void readUltrasonic(){

  float front = getDistance(TRIG_FRONT, ECHO_FRONT);

  float right = getDistance(TRIG_RIGHT, ECHO_RIGHT);


  Serial.print("Front: ");
  Serial.print(front);
  Serial.println(" cm");


  Serial.print("Right: ");
  Serial.print(right);
  Serial.println(" cm");
  SerialBT.print("Front, ");
  SerialBT.print(front);
  SerialBT.println(", cm");


  SerialBT.print("Right, ");
  SerialBT.print(right);
  SerialBT.println(", cm");

}
void loop() {
checkstart();
if(s==1){
    checkmpu();
    checkButtons();
    readUltrasonic();
}
}
