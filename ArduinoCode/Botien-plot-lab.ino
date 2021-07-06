String stringData;
int data;
int analogPin = 0;
char flag[4];
size_t byteSize;
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    byteSize = Serial.readBytes(flag, 3);//reads the incoming bytes send from the python script
    while (1 == 1) {
      if (strcmp(flag, "GET") == 0) { //checks if the recived bytes is equal to 'GET' then arduino responds by sending data
        data = analogRead(analogPin);
        stringData = String(data) + "\n";
        Serial.print(stringData);
      }
    }
  }
}
