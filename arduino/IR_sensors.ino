// Reads 4 IR sensors and send out data through Serial

// #include <Wire.h>

// IR value holders
int ir_1_val = 0;
int ir_2_val = 0;
int ir_3_val = 0;
int ir_4_val = 0;

// The setup routine runs once when you press reset:
void setup() {
  // Set up analog pins for input
  pinMode(A0, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);

  // Wire.begin(8);                // join i2c bus with address #8
  // Wire.onReceive(requestEvent); // register event

  // Initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

void loop() {

  // Read the input on all analog pins
  ir_1_val = analogRead(A0);
  ir_2_val = analogRead(A1);
  ir_3_val = analogRead(A2);
  ir_4_val = analogRead(A3);

  // Serial.print("IR 1 = ");
  Serial.print(ir_1_val);
  Serial.print(",");
  // Serial.print("IR 2 = ");
  Serial.print(ir_2_val);
  Serial.print(",");
  // Serial.print("IR 3 = ");
  Serial.print(ir_3_val);
  Serial.print(",");
  // Serial.print("IR 4 = ");
  Serial.println(ir_4_val);
  delay(25);
}

// // Write data to I2C bus whenever requested
// void requestEvent() {
//   Wire.write(ir_1_val + ',' + ir_2_val + ',' + ir_3_val + ',' + ir_4_val);
// }
