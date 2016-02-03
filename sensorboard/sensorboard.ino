#define TEMP   A0
#define LIGHT  A1
#define SOUND  A2
#define HUMIDITY A3
#define GLED 8
#define OLED 9
#define RLED 10
#define BLED 11
#include <SoftwareSerial.h>
#include <Wire.h>
#include "SparkFunMPL3115A2.h"

SoftwareSerial ESPserial(2, 3); // RX | TX
MPL3115A2 pressure;
int soundSamples = 5000;
int lastSoundMax;
int i = 0;
String sendString = "";
void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  pressure.begin();
  pinMode(TEMP, INPUT);
  pinMode(LIGHT, INPUT);
  pinMode(SOUND, INPUT);
  pinMode(GLED, OUTPUT);
  pinMode(OLED, OUTPUT);
  pinMode(RLED, OUTPUT);
  pinMode(BLED, OUTPUT);
  Serial.begin(9600);
  while (!Serial)   {
    ;
  }
  pressure.setModeBarometer(); // Measure pressure in Pascals from 20 to 110 kP
  pressure.setOversampleRate(7); // Set Oversample to the recommended 128
  pressure.enableEventFlags();
  digitalWrite(BLED, HIGH);
  ESPserial.begin(115200);
  ESPserial.println("AT+CIOBAUD=38400");
  delay(100);
  Serial.begin(38400);
  while (!Serial)   {
    ;
  }
  ESPserial.begin(38400);
  ESPserial.println("AT+CWMODE=1");
  waitFor("OK");
//  Serial.println("Connecting...");
//  ESPserial.println("AT+CWJAP=\"LorandKath\",\"bosezu81\"");
  ESPserial.println("AT+CWJAP=\"GHSSECURE\",\"04E1C14429E91670C3BAD755E8\"");
//  ESPserial.println("AT+CWJAP=\"NetGenie\",\"FTSU27MC\"");

  waitFor("OK");
//  Serial.println("Connected!");
  ESPserial.println("AT+CIPMUX=1");
  waitFor("OK");
//  Serial.println("Starting server...");
  ESPserial.println("AT+CIPSERVER=1,8080");
//  waitFor("OK");
//  Serial.println("Server up!");
  digitalWrite(GLED, HIGH);
  digitalWrite(BLED, LOW);
  sendString = getMeasurements();
}

void loop() {
  String str = "AT+CIPSEND=0," + String(sendString.length());
  digitalWrite(RLED, HIGH);
  ESPserial.println(str);
  while (1) {
    if (!ESPserial.find(">")) {
//      Serial.println("Connection failed, retrying...");
      ESPserial.println(str);
    } else {
//      Serial.println("Connection success!");
      digitalWrite(RLED, LOW);
      break;
    }
  }
  sendString = getMeasurements();
  digitalWrite(BLED, HIGH);
  ESPserial.println(sendString);
  waitFor("SEND OK");
  str = "Sent " + String(sendString.length()) + " characters.";
  ESPserial.println("AT+CIPCLOSE=0");
  waitFor("OK");
  digitalWrite(BLED, LOW);
}

void waitFor(char x[]) {
  digitalWrite(RLED, HIGH);
  while (1) {
    if (ESPserial.find(x)) {
      break;
    }
  }
  digitalWrite(RLED, LOW);
}

String getMeasurements() {
  digitalWrite(OLED, HIGH);
  lastSoundMax = 0;
  for (int x = 0; x < soundSamples; x++) {
    int sound = analogRead(SOUND);
    if (sound > lastSoundMax) {
      lastSoundMax = sound;
    }
  }
  String ss = String(pressure.readTemp()) + " " + String(analogRead(LIGHT)) + " " + String(lastSoundMax) + " " + String(pressure.readPressure() / 1000) + " " + String(analogRead(HUMIDITY));
  digitalWrite(OLED, LOW);
  return ss;
}

