
/*
nRF Serial Chat

Date : 22 Aug 2013
Author : Stanley Seow
e-mail : stanleyseow@gmail.com
Version : 0.90
Desc :
I worte this simple interactive serial chat over nRF that can be used for both sender
and receiver as I swapped the TX & RX addr during read/write operation.

It read input from Serial Monitor and display the output to the other side
Serial Monitor like a simple chat program.

Max payload is 32 bytes for radio but the serialEvent will chopped the entire buffer
for next payload to be sent out sequentially.


holoratte
8.5.2016 holoratte
updated for Ardumower communication und the latest RF24 librarry from TMRh20 
added a large serial TX buffer
*/


#include <SPI.h>
#include "RF24.h"
#include "printf.h"
//#include <Servo.h>
//#include <SoftwareSerial.h>

//SoftwareSerial mySerial(2, 3); // RX, TX
RF24 radio(9,10);

const uint64_t pipes[2] = { 0xDEDEDEDEE7LL, 0xDEDEDEDEE9LL };

volatile boolean stringComplete = false;  // whether the string is complete
static int dataBufferIndex = 0;
volatile boolean stringOverflow = false;
volatile char charOverflow = 0;
char SendPayload[32] = "";
char RecvPayload[32] = "";
char serialBuffer[32] = "";
const unsigned int MAX_INPUT_RF24 = 512;
/*
Servo mySwitch;  // create servo object to control a servo
Servo myMow;  // create servo object to control a servo
Servo mySteer;  // create servo object to control a servo
Servo mySpeed;  // create servo object to control a servo
*/
#define  pinSwitch  A5
#define  pinMow  A4
#define  pinSteer A3
#define  pinSpeed A2


struct dataStruct{
  byte remoteSwitch;
  byte remoteMow;
  byte remoteSteer;
  byte remoteSpeed;
}myData;
unsigned long RcFailSafeMillis = millis();
unsigned long currentMillis = millis();
unsigned long RcFailSafeInterval = 3000;

void setup(void) {
//  mySerial.begin(19200);
  Serial.begin(19200);

  myData.remoteSwitch = 0;
  myData.remoteMow = 0;
  myData.remoteSteer = 127;
  myData.remoteSpeed = 127;
  
  printf_begin();
  radio.begin();
 
  radio.setDataRate(RF24_2MBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(90);
 
  radio.enableDynamicPayloads();
  radio.setRetries(2,15);
  radio.setCRCLength(RF24_CRC_16);
  radio.setAutoAck(1); 
  
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]); 
 
  radio.startListening();
 //radio.printDetails();

 //Serial.println();
 //Serial.println("RF Chat V0.90");  
 radio.powerUp(); 
  delay(500);

}
/*void mySerialEvent() {
  
      char incomingByte = mySerial.read();
      //Serial.print("   ");
      //Serial.print(incomingByte);
      //Serial.print("   ");
     
      if (stringOverflow) {
         serialBuffer[dataBufferIndex++] = charOverflow;  // Place saved overflow byte into buffer
         serialBuffer[dataBufferIndex++] = incomingByte;  // saved next byte into next buffer
         stringOverflow = false;                          // turn overflow flag off
      } else if (dataBufferIndex > 29) {
         stringComplete = true;        // Send this buffer out to radio
         stringOverflow = true;        // trigger the overflow flag
         charOverflow = incomingByte;  // Saved the overflow byte for next loop
         dataBufferIndex = 0;          // reset the bufferindex
         return;
      }
      else if(incomingByte=='\n'){
          serialBuffer[dataBufferIndex++] = incomingByte;
          //serialBuffer[dataBufferIndex++] = incomingByte;
          //Serial.println(serialBuffer);
          serialBuffer[dataBufferIndex] = 0;
          
          
          stringComplete = true;
      } else {
          serialBuffer[dataBufferIndex++] = incomingByte;
          serialBuffer[dataBufferIndex] = 0;
      }         
  
} // end serialEvent()
*/
void hardSerialEvent() {
  
      char incomingByte = Serial.read();
      //Serial.print("   ");
      //Serial.print(incomingByte);
      //Serial.print("   ");
      if (stringOverflow) {
         serialBuffer[dataBufferIndex++] = charOverflow;  // Place saved overflow byte into buffer
         serialBuffer[dataBufferIndex++] = incomingByte;  // saved next byte into next buffer
         stringOverflow = false;                          // turn overflow flag off
      } else if (dataBufferIndex > 29) {
         stringComplete = true;        // Send this buffer out to radio
         stringOverflow = true;        // trigger the overflow flag
         charOverflow = incomingByte;  // Saved the overflow byte for next loop
         dataBufferIndex = 0;          // reset the bufferindex
         return;
      }
      else if(incomingByte=='\n'){
        stringComplete = true;
          serialBuffer[dataBufferIndex++] = incomingByte;
          //serialBuffer[dataBufferIndex++] = incomingByte;
          serialBuffer[dataBufferIndex] = 0;
          //Serial.println (*serialBuffer);
          
      } else {
          serialBuffer[dataBufferIndex++] = incomingByte;
          serialBuffer[dataBufferIndex] = 0;
      }         
  
} // end serialEvent()

void processIncomingByte (const byte inByte)
  {
  static char input_line [MAX_INPUT_RF24];
  static unsigned int input_pos = 0;

  switch (inByte)
    {

    case '\n':   // end of text
      input_line [input_pos] = 0;  // terminating null byte
      
      // terminator reached! process input_line here ...
      //Serial.print ("Serial out: ");
      Serial.println (input_line);
      //mySerial.println (input_line);
      
      // reset buffer for next time
      input_pos = 0;  
      break;

    case '\r':   // discard carriage return
      break;

    default:
      // keep adding if not full ... allow for terminating null byte
      if (input_pos < (MAX_INPUT_RF24 - 1))
        input_line [input_pos++] = inByte;
      break;

    }  // end of switch
   
  } // end of processIncomingByte  

void nRF_receive(void) {
  
  int len = radio.getDynamicPayloadSize();
      if(len < 1){
      // Corrupt payload has been flushed
        return; 
      }
    
    
    radio.read(&RecvPayload,len);
    
    

    if ((RecvPayload[0]) == 35) {     // ASCI 35 = # 
      RcFailSafeMillis = millis();
      //Serial.println("Servodata");
      if (RecvPayload[1] == 97) {   // ASCI 97 = a
        myData.remoteSwitch = RecvPayload[2];
        myData.remoteSwitch = map(myData.remoteSwitch, 0, 255, 40, 140);
      }
      if ((RecvPayload[1]) == 98) { // ASCI 98 = b
        myData.remoteMow = RecvPayload[2];
        myData.remoteMow = map(myData.remoteMow, 0, 255, 0, 180);
        //Serial.println("mow");
        //Serial.println(myData.remoteMow);
      }
      if ((RecvPayload[1]) == 99) {// ASCI 99 = c
        myData.remoteSteer = RecvPayload[2];
        myData.remoteSteer = map(myData.remoteSteer, 0, 255, 120, 60);
        //Serial.println("Steer");
        //Serial.println(myData.remoteSteer);
      }
      if ((RecvPayload[1]) == 100) {// ASCI 100 = d
        myData.remoteSpeed = RecvPayload[2];
        myData.remoteSpeed = map(myData.remoteSpeed, 0, 255, 120, 60);
        //Serial.println("Speed");
        //Serial.println(myData.remoteSpeed);
      }
      /*
      mySwitch.write(myData.remoteSwitch);
      myMow.write(myData.remoteMow);
      if (myData.remoteSteer != 90 && myData.remoteSpeed == 90){
        myData.remoteSpeed = 93;
      }
      mySteer.write(myData.remoteSteer);
      mySpeed.write(myData.remoteSpeed);*/
    }
    else{
      //Serial.print("R Payload: ");
      //Serial.println(RecvPayload);
      for (int thisChar = 0; thisChar < len; thisChar++) {
        processIncomingByte(RecvPayload[thisChar]);
      }
    

    RecvPayload[0] = 0;  // Clear the buffers
  }
   

} // end nRF_receive()

void serial_process(void){
 
  if (stringComplete) {
        strcat(SendPayload,serialBuffer);    
        // swap TX & Rx addr for writing
        radio.openWritingPipe(pipes[1]);
        radio.openReadingPipe(1,pipes[0]); 
        radio.stopListening();
        radio.writeFast(&SendPayload,strlen(SendPayload));
        //Serial.println(ok);
        if(radio.txStandBy(3000)){ 
          stringComplete = false;
          // restore TX & Rx addr for reading       
          radio.openWritingPipe(pipes[0]);
          radio.openReadingPipe(1,pipes[1]);
          radio.startListening();
          /*for (int thatChar = 0; thatChar < sizeof(SendPayload); thatChar++) {
            SendPayload[thatChar] = 0;
          } */
          SendPayload[0] = 0;
          dataBufferIndex = 0;
          
        }else {
          stringComplete = true;
          // restore TX & Rx addr for reading 
          //stringComplete = false;      
          radio.openWritingPipe(pipes[0]);
          radio.openReadingPipe(1,pipes[1]);
          radio.startListening(); 
          for (int thatChar = 0; thatChar < sizeof(SendPayload); thatChar++) {
            SendPayload[thatChar] = 0;
          }
          SendPayload[0] = 0;
          dataBufferIndex = 0;
          serial_process();
          
          
          }
  } // endif
} // end serial_receive() 

void loop(void) {
 if ( radio.available() ){
   nRF_receive();
   }
  /*while (mySerial.available() > 0 ) { 
    mySerialEvent();
    serial_process();
    } // end while()
    */
  while (Serial.available() > 0 ){
    hardSerialEvent();
    serial_process();
    }
  //currentMillis = millis();
  /*if(currentMillis - RcFailSafeMillis > RcFailSafeInterval){
    RcFailSafeMillis = currentMillis;
    mySwitch.write(0);
    myMow.write(0);
    hardSerialEvent();
    serial_process();
    mySteer.write(90);
    mySpeed.write(90);
    //Serial.println("{ro}");
    //Serial.println("RC Off");
  }*/
} // end loop()
