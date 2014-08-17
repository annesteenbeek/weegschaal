/*
  ReadAnalogVoltage
 Reads an analog input on pin 0, converts it to voltage, and prints the result to the serial monitor.
 Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.
 
 This example code is in the public domain.
 */

float startVolt, voltweight, voltage, voltageAverage, x; //voltage at setup
float weight=0;
int i;

float mass, slope, start, timer;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);

  timer = micros();
  while( micros()-timer < 100 ) { // dit stukje 100microsec laten draaien om gemiddelde te krijgen
    i++;
    startVolt+=(analogRead(A0)* (5.0 / 1023.0))/i;
  }
  Serial.print("Start Voltage is: "); 
  Serial.println(startVolt);
  i=0;
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  int sensorValue = analogRead(A0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  voltage = sensorValue * (5.0 / 1023.0);
  //smooth out with average voltage
  voltageAverage = (0.90*voltageAverage + 0.10*voltage);
  x = 52.788*(voltageAverage - startVolt);

  Serial.print("Gewicht is: "); 
  Serial.print(x); 
  Serial.print("\t"); 
  Serial.print(voltageAverage); 
  Serial.print("\t"); 
  Serial.println(voltweight);

  // hier kun je data naar de serial port sturen
  // int j=0;
  // char buffer[100];
  // while (Serial.available() && j<99) {
  //   buffer[j++] = Serial.read();
  // }
  // buffer[i++]='\0';
  // if(j>0){
  //   Serial.println((char*)buffer);
  //   if(strcmp(buffer, "reset") == 0){
  //     Serial.println("Het wordt gereset!");
  //     timer = micros();
  //     while( micros()-timer < 100 ) { // dit stukje 100microsec laten draaien om gemiddelde te krijgen
  //       i++;
  //       startVolt+=(analogRead(A0)* (5.0 / 1023.0))/i;
  //     }
  //     i=0;
  //     Serial.print("Start Voltage is: "); 
  //     Serial.println(startVolt);
  //   }
  //   else{      
  //     weight = atof(buffer);
  //     voltweight=voltageAverage;
  //     Serial.print("het huidige gewicht is: "); 
  //     Serial.println(weight);
  //   }
  // }
}

//functies:

// float analogToLoad(float analogval){

//   // using a custom map-function, because the standard arduino map function only uses int
//   float load = mapfloat(analogval, startVolt, voltweight, 0, weight);
//   return load;
// }

// float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
// {
//   return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
// }


