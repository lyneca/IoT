// Basic serial communication with ESP8266
// Uses serial monitor for communication with ESP8266
//
//  Pins
//  Arduino pin 2 (RX) to ESP8266 TX
//  Arduino pin 3 to voltage divider then to ESP8266 RX
//  Connect GND from the Arduiono to GND on the ESP8266
//  Pull ESP8266 CH_PD HIGH
//
// When a command is entered in to the serial monitor on the computer
// the Arduino will relay it to the ESP8266
//

#include <SoftwareSerial.h>
SoftwareSerial ESPserial(2, 3); // RX | TX

void setup() {
    Serial.begin(115200);     // communication with the host computer
    while (!Serial)   { ; }
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
    while (!Serial)   { ; }
    ESPserial.begin(38400);
    if ( ESPserial.available() )   {  Serial.write( ESPserial.read() );  }
    Serial.println("ESP8266 baud rate set to 38400.");

    Serial.println("");
    Serial.println("Remember to to set Both NL & CR in the serial monitor.");
    Serial.println("Ready");
    cmd("AT+CWMODE=1");
    waitFor("OK");
    cmd("AT+CWDHCP=1,1");
    waitFor("OK");
    Serial.println("Connecting...");
    cmd("AT+CWJAP=\"Lynx\",\"11111111\"");
    waitFor("OK");
    Serial.println("Connected!");
    cmd("AT+CIPMUX=1");
    waitFor("OK");
    Serial.println("Starting server...");
    cmd("AT+CIPSERVER=1,80");
    waitFor("OK");
    Serial.println("Server up!");
    Serial.println("Sending data...");
    while (1) {
      cmd("AT+CIPSEND=0,8");
      if (ESPserial.find(">")) {
        Serial.println("Connection failed, retrying...");
        break;
      }
    }
    cmd("00000000");
    waitFor("SEND OK");
    cmd("AT+CIPCLOSE=0");
    waitFor("OK");
}

void loop() {
    // listen for communication from the ESP8266 and then write it to the serial monitor
    if (ESPserial.available()) {
      Serial.write(ESPserial.read());
    }
    // listen for user input and send it to the ESP8266
    if (Serial.available()) {
      ESPserial.write(Serial.read());
    }
}

void cmd(char x[]) {
  String temp = (String) x + "\r\n";
  for (int i = 0; i < temp.length() + 1; i++) {
//    Serial.write(temp[i]);
    ESPserial.write(temp[i]);
  }
}

void waitFor(char x[]) {
  while (1) {
    if (ESPserial.find(x)) {
      break;
    }
  }
}

