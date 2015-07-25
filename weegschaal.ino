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
  weight = map(sensorValue, sensorStart, sensorLoaded, weight1, weight2); // het gewicht*10


Serial.print(abs(weight)); Serial.print("\n");
// Serial.println(sensorValue);
if (Serial.available() != 0){
  computerdata = Serial.readString();
  emptyweight = computerdata / 10;
  nixieson = computerdata - emptyweight*10;
  
  EEPROM.write(1, emptyweight);
  
}

  if (nixieson == 1){
    int number = abs(weight) - emptyweight;
    num0 = number/100; // vind het eerste getal
    setNumber(nixieOne, num0);
    num1 = number/10 - num0*10; // vind het 2e getal
    setNumber(nixieTwo, num1);
    num2 = number - num0*100 - num1*10; // vind het 3e getal
    setNumber(nixieThree, num2);
  }else{
    digitalWrite(nixieOne, LOW);
    digitalWrite(nixieTwo, LOW);
    digitalWrite(nixieThree, LOW);
  }
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
  delayMicroseconds(100);
  digitalWrite(nixie, HIGH);
  delayMicroseconds(1000);
}

unsigned int hexToDec(String hexString) {
  unsigned int decValue = 0;
  int nextInt;
  for (int i = 0; i < hexString.length(); i++) {
    nextInt = int(hexString.charAt(i));
    if (nextInt >= 48 && nextInt <= 57) nextInt = map(nextInt, 48, 57, 0, 9);
    if (nextInt >= 65 && nextInt <= 70) nextInt = map(nextInt, 65, 70, 10, 15);
    if (nextInt >= 97 && nextInt <= 102) nextInt = map(nextInt, 97, 102, 10, 15);
    nextInt = constrain(nextInt, 0, 15);
    decValue = (decValue * 16) + nextInt;
  }
  return decValue;
}

void setRGB(String colValHex){
  int redVal = hexToDec(colValHex.substring(0,1));
  int greenVal = hexToDec(colValHex.substring(2,3));
  int blueVal = hexToDec(colValHex.substring(4,6));
  analogWrite(redPin, redVal);
  analogWrite(greenPin, greenVal);
  analogWrite(bluePin, blueVal);
}