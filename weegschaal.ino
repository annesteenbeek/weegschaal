/*
  ReadAnalogVoltage
  Reads an analog input on pin 0, converts it to voltage, and prints the result to the serial monitor.
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.
 
 This example code is in the public domain.
 */

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

float voltageAverage = 2.5;

float calibrateMassA = 0.0;
float calibrateVoltageA = 2.7;

float calibrateMassB = 65.0;
float calibrateVoltageB = 4.16;


Serial.print("Calibrate voltage A is: "); Serial.print(calibrateVoltageA); Serial.print("\t");
Serial.print("Calibrate mass A is: "); Serial.println(calibrateMassA);
Serial.print("Calibrate voltage B is: "); Serial.print(calibrateVoltageB); Serial.print("\t");
Serial.print("Calibrate mass B is: "); Serial.println(calibrateMassB);

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  int sensorValue = analogRead(A0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float voltage = sensorValue * (5.0 / 1023.0);
  //smooth out with average voltage
  voltageAverage = (0.90*voltageAverage + 0.10*voltage);
  
  // print out the value you read:
  Serial.print("Voltage is: "); Serial.print(voltage); Serial.print("\t");
  Serial.print("sensorValue is: "); Serial.print(sensorValue); Serial.print("\t");
  Serial.print("voltageAverage is: "); Serial.println(voltageAverage);
}

