
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

*/


#include <SPI.h>
#include "RF24.h"
#include "printf.h"



RF24 radio(9,10);

const uint64_t pipes[2] = { 0xDEDEDEDEE7LL, 0xDEDEDEDEE9LL };

volatile boolean stringComplete = false;  // whether the string is complete
static int dataBufferIndex = 0;
volatile boolean stringOverflow = false;
volatile char charOverflow = 0;
char SendPayload[32] = "";
char RecvPayload[32] = "";
char serialBuffer[32] = "";
const unsigned int MAX_INPUT_RF24 = 1023;
boolean dataCorrupt = false;


void setup(void) {



  Serial.begin(115200);
  
  printf_begin();
  radio.begin();
 
  radio.setDataRate(RF24_2MBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(85);
 
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



void hardSerialEvent() {
  
      char incomingByte = Serial.read();
     
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
          
          
      } else {
          serialBuffer[dataBufferIndex++] = incomingByte;
          serialBuffer[dataBufferIndex] = 0;
      }         
  
} // end serialEvent()

void processIncomingByte (const byte inByte)
  {
  static char input_line [MAX_INPUT_RF24];
  static unsigned int input_pos = 0;
  if (dataCorrupt){
    for (int thatChar = 0; thatChar < sizeof(input_line); thatChar++) {
      input_line[thatChar] = 0;
    }
    
    input_pos = 0;
    dataCorrupt = false;
  }
  switch (inByte)
    {

    case '\n':   // end of text
      input_line [input_pos] = 0;  // terminating null byte
      
      // terminator reached! process input_line here ...
      
      //Serial.println();
      //Serial.print ("Serial out: ");
      Serial.println (input_line);

      
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
        dataCorrupt = true;
        radio.read(&RecvPayload,len);
        for (int thisChar = 0; thisChar < len; thisChar++) {
          RecvPayload[thisChar] = 0;
        }
        Serial.println("data corrupt");
        return; 
      }
    
    
    radio.read(&RecvPayload,len);
 

  
    //Serial.print("R Payload: ");
    
    for (int thisChar = 0; thisChar < len; thisChar++) {
      processIncomingByte(RecvPayload[thisChar]);
      //Serial.print(RecvPayload[thisChar]);
    }

    RecvPayload[0] = 0;  // Clear the buffers
  
   

} // end nRF_receive()

void serial_process(void){
 
  if (stringComplete) {
        strcat(SendPayload,serialBuffer);    
        // swap TX & Rx addr for writing
        radio.openWritingPipe(pipes[1]);
        radio.openReadingPipe(1,pipes[0]); 
        radio.stopListening();
        radio.writeFast(&SendPayload,strlen(SendPayload));
        if(radio.txStandBy(100)){ 

          stringComplete = false;
     
          radio.openWritingPipe(pipes[0]);
          radio.openReadingPipe(1,pipes[1]);
          radio.startListening(); 
          SendPayload[0] = 0;
          dataBufferIndex = 0;
        }else {return;}
  } // endif
} // end serial_receive() 

void loop(void) {
  if ( radio.available() ) { 
    nRF_receive();
    }
  while (Serial.available() > 0 ) {
    hardSerialEvent();
	serial_process();
  } // end while()
} // end loop()
