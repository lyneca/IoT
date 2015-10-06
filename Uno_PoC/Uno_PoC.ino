#define SLIDER1  A0
#define SLIDER2  A1
#define SLIDER3  A2
#define LIGHT    A3
#define TEMP     A4
#define KNOCK    A5

#define DATA     4
#define LED1     5
#define LED2     6
#define LATCH    7
#define CLOCK    8
#define BUZZER   9
#define BUTTON1  10
#define BUTTON2  11
#define BUTTON3  12

const byte ledCharSet[10] = {
  B11000000,
  B11111001, 
  B10100100, 
  B10110000, 
  B10011001, 
  B10010010, 
  B10000010, 
  B11111000, 
  B10000000, 
  B10010000
};

int i = 0;
int averageLength = 128;
float temps[128];

void setup() {
  // put your setup code here, to run once:
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LIGHT, INPUT);
  pinMode(TEMP, INPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(SLIDER1, INPUT);
  pinMode(SLIDER2, INPUT);
  pinMode(SLIDER3, INPUT);
  pinMode(KNOCK, INPUT);
  pinMode(LATCH, OUTPUT);
  pinMode(CLOCK, OUTPUT);
  pinMode(DATA, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int slider = analogRead(SLIDER1);
  float temperature = analogRead(TEMP);
  long light = analogRead(LIGHT);
  if (light <= 200) {
    digitalWrite(LED2, HIGH);
  } else {
    digitalWrite(LED2, LOW);
  }
  temperature *= 5000;
  temperature /= 1023;
  temperature -= 500;
  temperature /= 10;
  temps[i] = temperature;
  i += 1;
  if (i == averageLength) {
    i = 0;
    float tempAverage = sumArray(temps, averageLength) / averageLength;
    Serial.println(analogRead(KNOCK));
    digitalWrite(LATCH, LOW);
    shiftOut(DATA, CLOCK, MSBFIRST, ~(ledCharSet[map(round(tempAverage), 15, 35, 0, 9) - map(slider, 0, 255, 0, 9)]));
    digitalWrite(LATCH, HIGH);
  }
}
float sumArray(float* array, int len) {
  long sum = 0L;
  for (int j = 0; j < len; j++) {
    sum += array[j];
  }
  return (float) sum;
}

