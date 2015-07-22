#include <EEPROM.h> // for writing to the arduino memory;
#include <config.h> 


// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(9600);

  pinmode(scalePin, OUTPUT);
  pinmode(redPin, OUTPUT);
  pinmode(greenPin, OUTPUT);
  pinmode(bluePin, OUTPUT);
  pinmode(nixieOne, OUTPUT);
  pinmode(nixieTwo, OUTPUT);
  pinmode(nixieThree, OUTPUT);
  pinmode(ledPin, OUTPUT);
  
  pinmode(Dpin, OUTPUT);
  pinmode(Cpin, OUTPUT);
  pinmode(Bpin, OUTPUT);
  pinmode(Apin, OUTPUT);

  emptyweight = EEPROM.read(1);
}

void loop() {
 // read the input on analog pin 0:
  sensorValue = analogRead(scalePin);
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
  int sensorStart = 555;
  int weight1 = 0;
  int sensorLoaded = 755;
  int weight2 = 650;
  weight = map(sensorValue, sensorStart, sensorLoaded, weight1, weight2); // het gewicht*10


Serial.print(abs(weight)); Serial.print("\n");
// Serial.println(sensorValue);
if (Serial.available() != 0){
  computerdata = Serial.parseFloat();
  emptyweight = computerdata / 10;
  nixieson = computerdata - emptyweight*10;
  
  EEPROM.write(1, emptyweight);
  
}

int emptyweight= 0;
if (nixieson == 1){
  int number = abs(weight) - emptyweight;
    num0 = number/100; // vind het eerste getal
    num1 = number/10 - num0*10; // vind het 2e getal
    num2 = number - num0*100 - num1*10; // vind het 3e getal

    data0 = (byte) (byteArray[num1] | (byteArray[num2]<<4)); // 1e en 2e 4 bits
    data1 = (byte) (byteArray[num0] | (byteArray[8]<<4)); // second shift register data
    digitalWrite(latchPin, 0); 
    shiftOut(dataPin, clockPin, data1); // stuur naar 2e shift register
    shiftOut(dataPin, clockPin, data0); // stuur naar 1e shift register
    digitalWrite(latchPin,1);

  }
  
   delay(1000);
}

void setNumber(int nixie, int num) {
  
  digitalWrite(nixieOne, LOW);
  digitalWrite(nixieTwo, LOW);
  digitalWrite(nixieThree, LOW);

  for (int i=0; i<=3; i++){ // loop trough the 4 bytes of the number to set
      switch (i) {  // select the appropriate pin for every case
        case 0:
          logicPin=Apin;
          break;
        case 1:
          logicPin=Bpin;
          break;
        case 2:
          logicPin=Cpin;
          break;
        case 3:
          logicPin=Dpin;
          break;
    }
    if (((number >> i) & 1)==1) {  // select the i'th bit from the number byte
      digitalWrite(logicPin, HIGH);
    }else{
      digitalWrite(logicPin, LOW);
    } 
  }
  digitalWrite(nixie, HIGH);
}