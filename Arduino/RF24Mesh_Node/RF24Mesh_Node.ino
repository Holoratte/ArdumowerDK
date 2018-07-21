
/** RF24Mesh_Example_Node2Node.ino by TMRh20
 *
 * This example sketch shows how to communicate between two (non-master) nodes using
 * RF24Mesh & RF24Network
 **/


#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SPI.h>
//#include <printf.h>
#include <avr/wdt.h>

//########### USER CONFIG ###########

/**** Configure the nrf24l01 CE and CS pins ****/
RF24 radio(9, 10);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

/**
 * User Configuration:
 * nodeID - A unique identifier for each radio. Allows addressing to change dynamically
 * with physical changes to the mesh. (numbers 1-255 allowed)
 *
 * otherNodeID - A unique identifier for the 'other' radio
 *
 **/
#define nodeID 54
#define otherNodeID 0

//#################################

uint32_t millisTimer = 0;
uint32_t stringTimer = 0;
char dataStr[140];
char dataStrSend[140];
char tmpStr[sizeof(dataStr) + 1];
char tmpStrSend[sizeof(dataStr) + 1];
char checksumStr[sizeof(dataStr) ];
uint8_t strCtr = 1;
unsigned int sizeCtr = 2;
unsigned int sizeReceivedCtr = 0;
uint32_t errorCount = 0;
uint32_t duplicates = 0;
uint32_t totalData = 0;
boolean sendToMesh = false;
uint8_t checkSum = 0;
uint8_t checksumReceived = 0;

void setup() {
  WatchDog_Setup();
  Serial.begin(19200);
  //printf_begin();
  // Set the nodeID manually
  wdt_reset();
  mesh.setNodeID(nodeID);
  // Connect to the mesh
  Serial.println(F("Connecting to the mesh..."));
  mesh.begin();
  while ( ! mesh.checkConnection() ) {
        Serial.println(F("Renewing Address"));
        mesh.renewAddress();
  }
  Serial.println(F("Connection Ok"));
  //mesh.setChannel(107);
  wdt_reset();
}



void loop() {
  wdt_reset();
  mesh.update();

  while (network.available()) {
    RF24NetworkHeader header;
    size_t dataSize = network.peek(header);
    totalData += dataSize;

    if (header.type == 'S') {
      network.read(header, &tmpStr, dataSize );
      memcpy(checksumStr, tmpStr, dataSize - 1);
      checkSum = stringCheckSum(checksumStr);
      //Serial.println(checkSum);
      //Serial.println(dataSize);
      checksumReceived = tmpStr[dataSize - 1];
      //Serial.println(checksumReceived);
      if (checkSum == checksumReceived)Serial.print(checksumStr);
      //else Serial.println("Checksum wrong");
      memset(checksumStr, 0, sizeof(checksumStr));
      memset(tmpStr, 0, sizeof(tmpStr));

    } else if (header.type == 'M') {
      uint32_t mills;
      network.read(header, &mills, sizeof(mills));
      //Serial.print(F("Received "));
      //Serial.print(mills);
      int _ID = 0;
      _ID = mesh.getNodeID(header.from_node);
      /*if ( _ID > 0) {
        if (_ID == nodeID) {
          Serial.println(F(" from master."));
        } else {
          Serial.print(F(" from node(ID) "));
          Serial.print(_ID);
          Serial.println('.');
        }
      } else {
        Serial.println(F("Mesh ID Lookup Failed"));
      }
      Serial.print(F("Total Data Received: "));
      Serial.print(totalData);
      Serial.println(" bytes");
      Serial.print(F("Detected Errors in data received (Including Duplicates): "));
      Serial.println(errorCount);
      Serial.print(F("Duplicates: "));
      Serial.println(duplicates);
      Serial.println(F("-------------------------------------"));
    */
    }
  }


  // Send to the master node every second
  if (millis() - millisTimer >= 1000 ) {
    millisTimer = millis();

    // Send an 'M' type to other Node containing the current millis()
    if (!mesh.write(&millisTimer, 'M', sizeof(millisTimer), otherNodeID)) {
      //Serial.println(F("Send fail"));
      if ( ! mesh.checkConnection() ) {
        //Serial.println(F("Renewing Address"));
        mesh.renewAddress();
      } else {
        //Serial.println(F("Send fail, Test OK"));
      }
    } else {
      //Serial.print(F("Send OK: ")); Serial.println(millisTimer);
    }
  }

  while (Serial.available() >= 1) {
    if (Serial.available() >= 1){
      char serialReceived = (char)Serial.read();
      dataStrSend[sizeReceivedCtr] =  serialReceived;
      sizeReceivedCtr++;
      if (sizeReceivedCtr >= 100) {
        sendToMesh = true;
        break;
      }
      if (serialReceived == '\n'){
        sendToMesh = true;
        break;
      }
    }
  }
  
  if (sendToMesh) {
    sendToMesh = false;
    //Copy the current number of characters to the temporary array
    memcpy(tmpStrSend, dataStrSend, sizeReceivedCtr);
    //Set the last character to NULL
    checkSum = stringCheckSum(tmpStrSend);
    //Serial.println(checkSum);
    //Serial.println(sizeReceivedCtr);
    tmpStrSend[sizeReceivedCtr] = checkSum;
    tmpStrSend[sizeReceivedCtr + 1] = '\0';
    //Serial.println (dataStr);
    // Send the temp string as an 'S' type message
    // Send it to otherNodeID (An RF24Mesh address lookup will be performed)
    //bool ok = mesh.write(tmpStr,'S',strCtr+1,otherNodeID);
    if (!mesh.write(tmpStrSend, 'S', sizeReceivedCtr+1 , otherNodeID)) {
      //Serial.println(F("Send fail"));
      if ( ! mesh.checkConnection() ) {
        //Serial.println(F("Renewing Address"));
        mesh.renewAddress();
      } else {
        //Serial.println(F("Send fail, Test OK"));
      }
    } else {
      //Serial.print(F("Send OK: ")); Serial.println(dataStr);
    }
    //Serial.println(sizeReceivedCtr);
    millisTimer = millis();
    memset(dataStrSend, 0, sizeof(dataStrSend));
    memset(tmpStrSend, 0, sizeof(tmpStrSend));
    sizeReceivedCtr = 0;
  }
}

byte stringCheckSum(char *s)
{
    byte c = 0;
    while(*s != '\0'){
        if (*s != '\0') c ^= *s++;
    }
    return c;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void WatchDog_Setup(void)
{
  cli();                       // disable all interrupts
  wdt_reset();                 // reset the WDT timer

  // Enter Watchdog Configuration mode:
  WDTCSR |= (1 << WDCE) | (1 << WDE);
  // Set Watchdog settings:
  WDTCSR = (1 << WDIE) | (1 << WDE) | (0 << WDP3) | (1 << WDP2) | (1 << WDP1) | (1 << WDP0);
  sei();
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
   WDIE - Enables Interrupts. This will give you the
   chance to include one last dying wish (or a few
   lines of code...) before the board is reset. This is a
   great way of performing interrupts on a regular
   interval should the watchdog be configured to not
   reset on time-out.

*/
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
ISR(WDT_vect) // Watchdog timer interrupt.
{
  // Chance to express a last dying wish for the program
  // Include your code here - be careful not to use functions they may cause the interrupt to hang and
  // prevent a reset.
  //Serial.print("W");
  //Serial.println("\t");
}

