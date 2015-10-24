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
String inData = "";
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
    ESPserial.println("AT+CWMODE=1");
    waitFor("OK");
    ESPserial.println("AT+CWDHCP=1,1");
    waitFor("OK");
    Serial.println("Connecting...");
    ESPserial.println("AT+CWJAP=\"NetGenie\",\"FTSU27MC\"");
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
    // listen for user input and send it to the ESP8266
    while (Serial.available() > 0) {
      char received = Serial.read();
      inData += received;
      if (received == '\n') {
        
        Serial.println("Sending data...");
        String str = "AT+CIPSEND=0," + String(inData.length());
        while (1) {
          ESPserial.println(str);
          if (!ESPserial.find(">")) {
            Serial.println("Connection failed, retrying...");
          } else {
            Serial.println("Connection success!");
            break;
          }
        }
        ESPserial.println(inData);
        waitFor("SEND OK");
        str = "Sent " + String(inData.length()) + " characters.";
        Serial.println(str);
        ESPserial.println("AT+CIPCLOSE=0");
        waitFor("OK");
        Serial.println("Connection closed.");
        inData = "";
      }
    }
}

//void cmd(char x[]) {
//  Serial.println(x);
//  String temp = (String) x + "\r\n";
//  for (int i = 0; i < temp.length() + 1; i++) {
////    Serial.write(temp[i]);
//    ESPserial.write(temp[i]);
//  }
//}

void waitFor(char x[]) {
  while (1) {
    if (ESPserial.find(x)) {
      break;
    }
  }
}

