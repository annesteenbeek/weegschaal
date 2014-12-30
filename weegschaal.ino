#include <EEPROM.h> // for writing to the arduino memory;

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


int latchPin = 8;
int clockPin = 12;
int dataPin = 11;
byte data0, data1;
int byteArray[10];
int num0, num1, num2;
int number =0;
int byte0, byte1;


// the setup routine runs once when you press reset:
void setup() {

  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  Serial.begin(9600);

  byteArray[0] = 0; //0000
  byteArray[1] = 1; //0001
  byteArray[2] = 2; //0010
  byteArray[3] = 3; //0011
  byteArray[4] = 4; //0100
  byteArray[5] = 5; //0101
  byteArray[6] = 6; //0110
  byteArray[7] = 7; //0111
  byteArray[8] = 8; //1000
  byteArray[9] = 9; //1001
  emptyweight = EEPROM.read(1);
  


}

void loop() {
 // read the input on analog pin 0:
  sensorValue = analogRead(A0);
  // analog voltage goes from 0 to 1023

  if (count != countmax){
    count++;
    sensorAverage=sensorAverage+sensorValue;
  }
  else{
    count = 0;
    if ( sensorAverage/countmax - (0.5*1023) > sensorOutput > sensorAverage/countmax + (0.5*1023) ){ // minimum difference to prevent constant small value changes
    sensorOutput=sensorAverage/countmax;
    }
    sensorAverage = 0;
  }
 
  weight = map(sensorOutput, sensorStart, sensorLoaded, weight1, weight2); // het gewicht*10

  // MANUAL INPUT OF WEIGHT DATA OVER SERIAL
  // //The first input defines weight 1
  // if (Serial.available() > 0 && k == 0) {
  //   weight1 = (float) Serial.parseInt();
  //   sensorStart=sensorAverage;
  //   Serial.print("weight 1 is: "); Serial.println(weight1);
  //   k = 1;
  // }
  
  // //The second input defines weight 2
  // if (Serial.available() > 0 && k == 1) {
  //   weight2 = (float) Serial.parseInt();
  //   sensorLoaded=sensorAverage;
  //   Serial.print("weight 2 is: "); Serial.println(weight2);
  //   k = 0;
  // }




// toDo:
// calibratie data opslaan in geheugen
// relais fixen zodat je power supply echt uit kunt zetten.
// Timer zodat nixies niet hele dag aan staan.
// Script voor op woonkamer computer



Serial.print(weight); Serial.print("\n");

if (Serial.available() != 0){
  computerdata = Serial.parseInt();
  emptyweight = computerdata / 10;
  nixieson = computerdata - emptyweight*10;
  
  EEPROM.write(1, emptyweight);
  
}

if (nixieson == 1){
  int number = weight - emptyweight;
    num0 = number/100; // vind het eerste getal
    num1 = number/10 - num0*10; // vind het 2e getal
    num2 = number - num0*100 - num1*10; // vind het 3e getal

    data0 = (byte) (byteArray[num2] | (byteArray[num1]<<4)); // 1e en 2e 4 bits
    data1 = (byte) (byteArray[num0] | (byteArray[0]<<4)); // second shift register data
    digitalWrite(latchPin, 0); 
    shiftOut(dataPin, clockPin, data1); // stuur naar 2e shift register
    shiftOut(dataPin, clockPin, data0); // stuur naar 1e shift register
    digitalWrite(latchPin,1);
  }
  
   delay(1000);
}


 // Functie voor het sturen van data naar de shift registers
 void shiftOut(int myDataPin, int myClockPin, byte myDataOut) {
  // This shifts 8 bits out MSB first, 
  //on the rising edge of the clock,
  //clock idles low

  //internal function setup
  int i=0;
  int pinState;
  pinMode(myClockPin, OUTPUT);
  pinMode(myDataPin, OUTPUT);

  //clear everything out just in case to
  //prepare shift register for bit shifting
  digitalWrite(myDataPin, 0);
  digitalWrite(myClockPin, 0);

  //for each bit in the byte myDataOut�
  //NOTICE THAT WE ARE COUNTING DOWN in our for loop
  //This means that %00000001 or "1" will go through such
  //that it will be pin Q0 that lights. 
  for (i=7; i>=0; i--)  {
    digitalWrite(myClockPin, 0);

    //if the value passed to myDataOut and a bitmask result 
    // true then... so if we are at i=6 and our value is
    // %11010100 it would the code compares it to %01000000 
    // and proceeds to set pinState to 1.
    if ( myDataOut & (1<<i) ) {
      pinState= 1;
    }
    else {  
      pinState= 0;
    }

    //Sets the pin to HIGH or LOW depending on pinState
    digitalWrite(myDataPin, pinState);
    //register shifts bits on upstroke of clock pin  
    digitalWrite(myClockPin, 1);
    //zero the data pin after shift to prevent bleed through
    digitalWrite(myDataPin, 0);
  }

  //stop shifting
  digitalWrite(myClockPin, 0);
}


