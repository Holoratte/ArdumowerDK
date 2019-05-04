 
 
 /** RF24Mesh_Example_Master.ino by TMRh20
  * 
  *
  * This example sketch shows how to manually configure a node via RF24Mesh as a master node, which
  * will receive all data from sensor nodes.
  *
  * The nodes can change physical or logical position in the network, and reconnect through different
  * routing nodes as required. The master node manages the address assignments for the individual nodes
  * in a manner similar to DHCP.
  *
  */
  
  
#include "RF24Network.h"
#include "RF24.h"
#include "RF24Mesh.h"
#include <SPI.h>
//Include eeprom.h for AVR (Uno, Nano) etc. except ATTiny
#include <EEPROM.h>
#include <avr/wdt.h>
/***** Configure the chosen CE,CS pins *****/
RF24 radio(9,10);
RF24Network network(radio);
RF24Mesh mesh(radio,network);

#define nodeId 2
byte otherNodeID = 119;
uint32_t displayTimer = 0;
char dataStr[140];
char dataStrSend[140];
char tmpStr[sizeof(dataStr) + 1];
char tmpStrSend[sizeof(dataStr) + 1];
char checksumStr[sizeof(dataStr) ];
uint8_t strCtr = 1;
unsigned int sizeReceivedCtr = 0;
boolean sendToMesh = false;

unsigned int sizeCtr = 1;
uint32_t errorCount = 0;
uint32_t duplicates = 0;
uint32_t totalData = 0;
uint8_t checkSum = 0;
uint8_t checksumReceived = 0;
boolean msgComplete = true;
boolean displayInfo = false;

void setup() {
  WatchDog_Setup();
  Serial.begin(19200);
  wdt_reset();
  // Set the nodeId to 0 for the master node
  mesh.setNodeID(0);
  wdt_reset();
  Serial.println(mesh.getNodeID());
  // Connect to the mesh
  mesh.begin();
  mesh.setChannel(107);
  //delay(1500);
  //mesh.setStaticAddress(119, 4);
  //mesh.setStaticAddress(28, 44);
  wdt_reset();

}



void loop() {    
  wdt_reset();
  // Call mesh.update to keep the network updated
  //if (msgComplete) mesh.update();
  mesh.update();
  // In addition, keep the 'DHCP service' running on the master node so addresses will
  // be assigned to the sensor nodes
  if (msgComplete) mesh.DHCP();
  

  // Check for incoming data from the sensors
 while (network.available()) {
    RF24NetworkHeader header;
    size_t dataSize = network.peek(header);
    totalData += dataSize;
    //Serial.println(dataSize);

    if (header.type == 'S') {
      int _ID = 0;
      _ID = mesh.getNodeID(header.from_node);
      network.read(header, &tmpStr, dataSize );
      memcpy(checksumStr, tmpStr, dataSize - 1);
      checkSum = stringCheckSum(checksumStr);
      checksumStr[dataSize - 1] = 10;
      //Serial.println(checkSum);
      //Serial.println(dataSize);
      checksumReceived = tmpStr[dataSize - 1];
      //Serial.println(checksumReceived);
      if (checkSum == checksumReceived){
        //Serial.print("*");
        Serial.print(_ID);
        Serial.print("#");
        Serial.print(checksumStr);
        if (checksumStr[dataSize-2] == 10) {
          msgComplete = true;
          //Serial.println((byte)checksumStr[dataSize-2]);
        }
        else {
          msgComplete = false;
          //Serial.println((byte)checksumStr[dataSize-2]);
        }
      }
      else Serial.println("Checksum wrong");
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
        if (_ID == nodeId) {
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
      Serial.println(F("-------------------------------------"));*/
    }  
  }

  while (Serial.available() >= 1) {
    if (Serial.available() >= 1){
      char serialReceived = (char)Serial.read();
      static boolean receivingCmd = false;
      if (serialReceived == '*'){
         receivingCmd = true;
      }
      else {
        dataStrSend[sizeReceivedCtr] =  serialReceived;
        sizeReceivedCtr++;
      }
      
      if (sizeReceivedCtr >= 100) {
        sendToMesh = true;
        break;
      }
      if (serialReceived == '\n'){
        if ((receivingCmd) && (sizeReceivedCtr == 2)){
          receivingCmd = false;
          if (dataStrSend[0] == 0) displayInfo = true;
          else otherNodeID = (byte)dataStrSend[0];
          memset(dataStrSend, 0, sizeof(dataStrSend));
          sizeReceivedCtr = 0;
        }
        else sendToMesh = true;
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

    memset(dataStrSend, 0, sizeof(dataStrSend));
    memset(tmpStrSend, 0, sizeof(tmpStrSend));
    sizeReceivedCtr = 0;
  }
  
  //if((millis() - displayTimer > 60000) && (msgComplete)){
    //displayTimer = millis();
  if((displayInfo) && (msgComplete)){
    displayInfo = false;
    Serial.println(" ");
    Serial.println(F("********Assigned Addresses********"));
     for(int i=0; i<mesh.addrListTop; i++){
       Serial.print("NodeID: ");
       Serial.print(mesh.addrList[i].nodeID);
       Serial.print(" RF24Network Address: 0");
       Serial.println(mesh.addrList[i].address,OCT);
     }
    Serial.print(F("Total Data Received: "));
    Serial.print(totalData);
    Serial.println(F(" bytes"));
    Serial.println(F("**********************************"));
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
  Serial.print("W");
  Serial.println("\t");
}
