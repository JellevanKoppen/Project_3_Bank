#include <Keypad.h>
#include <SPI.h>
#include <MFRC522.h>
#define SDA 10
#define RST A0

/*
TO DO:
- Elke drie seconden checken voor RFID
- Uitvinden of arduino 49 of 1 ontvangt!
*/

const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS]{
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte rowPins[ROWS] = {5, 4, 3, 2};
byte colPins[COLS] = {9, 8, 7, 6};
String incomingByte;
bool received = false;
bool reading = false;

Keypad keypad = Keypad(makeKeymap(keys), colPins, rowPins, ROWS, COLS);

MFRC522 mfrc522(SDA,RST);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();//Start de rfid reader
}

void loop() {
  for(int i = 0; i<5;i++){
    readKeypad();
  }
  readRFID();
  delay(50);
}

void readKeypad(){
  char key = keypad.getKey();
  if(key){
    Serial.println(key);
  }
}

void readRFID(){
  if(!mfrc522.PICC_IsNewCardPresent()){
    return;
  }
  if(!mfrc522.PICC_ReadCardSerial()){
    return;
  }
  String content = "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) { 
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "); 
    Serial.print(mfrc522.uid.uidByte[i], HEX);
    content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
    content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }
  Serial.println(); 
}

