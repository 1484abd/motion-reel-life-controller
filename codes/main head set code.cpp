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
int s =0;
float gyroX_offset = 0;
float gyroY_offset = 0;
float gyroZ_offset = 0;
MPU9250 mpu;
float yaw;
float pitch;
float roll;

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




  if(!mpu.setup(0x68)){
    Serial.println("MPU9250 not found");
    while(1);
  }


  delay(3000);
    mpu.calibrateAccelGyro();
  mpu.calibrateMag();
}

void checkmpu(){

  if(mpu.update()){


    yaw = mpu.getYaw();

    pitch = mpu.getPitch();

    roll = mpu.getRoll();



    Serial.print("Yaw: ");
    Serial.print(yaw);
    Serial.println(" deg");


    Serial.print("Pitch: ");
    Serial.print(pitch);
    Serial.println(" deg");


    Serial.print("Roll: ");
    Serial.print(roll);
    Serial.println(" deg");



    SerialBT.print("YAW,");
    SerialBT.println(yaw);


    SerialBT.print("PITCH,");
    SerialBT.println(pitch);


    SerialBT.print("ROLL,");
    SerialBT.println(roll);



    float ax = mpu.getAccX();
    float ay = mpu.getAccY();
    float az = mpu.getAccZ();



    float totalAcceleration =
      sqrt(
        ax*ax+
        ay*ay+
        az*az
      );


    if(totalAcceleration > 18){

      Serial.println("JUMP");
      SerialBT.println("JUMP");

    }


    if(
      abs(ax)>3 ||
      abs(ay)>3 ||
      abs(az-1)>0.3
    ){

      SerialBT.println("MOVING");

    }
    else{

      SerialBT.println("STILL");

    }

  }


  delay(20);

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
