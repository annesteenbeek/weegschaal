int sensorValue; //Value measured from sensor
int sensorAverage = 0; // average sensor data
int sensorStart; 
int sensorLoaded;
int sensorOutput=0; // average sensor output for #counts
int weight2;
int weight1;

float weight;

int k=0;
int count=0;
int countmax = 10;
int computerdata = 0;
int emptyweight = 0;
int nixieson = 0;
int ledson = 0;

//--- PINS ---//

int gndpin = 9;
int latchPin = 8;
int clockPin = 12;
int dataPin = 11;
byte data0, data1;
int byteArray[10];
int num0, num1, num2;
int number =0;
int byte0, byte1;