#define TEMP   A0
#define LIGHT  A1
#define SOUND  A2
#define PRESSURE A3
#include <SoftwareSerial.h>
SoftwareSerial ESPserial(2, 3); // RX | TX
int soundSamples = 5000;
float lastSoundAverage;
int i = 0;
String sendString = "";
void setup() {
  // put your setup code here, to run once:
  pinMode(TEMP, INPUT);
  pinMode(LIGHT, INPUT);
  pinMode(SOUND, INPUT);
  Serial.begin(9600);
  while (!Serial)   {
    ;
  }
  // Start the software serial for communication with the ESP8266
  ESPserial.begin(115200);
  ESPserial.println("AT+CIOBAUD=38400");
  //do
  //{
  //  ESPserial.println("AT+CIOBAUD=38400");
  //  while(!ESPserial.available());
  //} while (!ESPserial.find("OK"));
  delay(100);
  Serial.begin(38400);
  while (!Serial)   {
    ;
  }
  ESPserial.begin(38400);
  ESPserial.println("AT+CWMODE=1");
  waitFor("OK");
  //    ESPserial.println("AT+CWDHCP=1,1");
  //    waitFor("OK");
  Serial.println("Connecting...");
  ESPserial.println("AT+CWJAP=\"NetGenie\",\"FTSU27MC\"");
  //    ESPserial.println("AT+CWJAP=\"GHSSECURE\",\"04E1C14429E91670C3BAD755E8\"");
  waitFor("OK");
  Serial.println("Connected!");
  ESPserial.println("AT+CIPMUX=1");
  waitFor("OK");
  Serial.println("Starting server...");
  ESPserial.println("AT+CIPSERVER=1,8080");
  waitFor("OK");
  Serial.println("Server up!");
}

void loop() {
  // put your main code here, to run repeatedly:
  float temp = (((analogRead(TEMP) * 5000.0) / 1024.0) - 600.0) / 10.0;
  temp /= 2;

  lastSoundAverage = 0;
  for (int x = 0; x < soundSamples; x++) {
    //    float tempSound = analogRead(SOUND) - 247;
    //    lastSoundAverage += abs(tempSound);
    //    lastSoundAverage += tempSound;
    float sound = analogRead(SOUND) - 247 ;
    if (sound > lastSoundAverage) {
      lastSoundAverage = sound;
    }
  }
  //  lastSoundAverage /= (float)soundSamples;

  sendString = String(millis()) + " " + String(analogRead(LIGHT)) + " " + String(temp) + " " + String(lastSoundAverage) + " " + "0" + " " + String(analogRead(PRESSURE));

  String str = "AT+CIPSEND=0," + String(sendString.length());
  while (1) {
    ESPserial.println(str);
    if (!ESPserial.find(">")) {
      Serial.println("Connection failed, retrying...");
    } else {
      Serial.println("Connection success!");
      break;
    }
  }
  ESPserial.println(sendString);
  waitFor("SEND OK");
  str = "Sent " + String(sendString.length()) + " characters.";
  Serial.println(str);
  ESPserial.println("AT+CIPCLOSE=0");
  waitFor("OK");
  Serial.println("Connection closed.");
}

void waitFor(char x[]) {
  while (1) {
    if (ESPserial.find(x)) {
      break;
    }
  }
}
