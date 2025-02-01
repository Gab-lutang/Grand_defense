#include <SoftwareSerial.h>

SoftwareSerial myGSM(9, 10); // TX - RX
String phoneNumber1 = "+639618084684"; // Primary phone number
String phoneNumber2 = ""; // Secondary phone number
unsigned long lastLoadCheck = 0;
const unsigned long LOAD_CHECK_INTERVAL = 60000; // Check load every 1 minute
int smsBalance = 0; // Store SMS balance
int butswitch = 6;
int buzzer = 7;
int propanePin = A0;    // MQ-6 Gas sensor on analog pin A0
int butstate;
bool fireAlarmActive = false;
bool gasAlarmActive = false;
int propaneThreshold = 400;  // Adjust this threshold based on sensor calibration

void setup()
{
	Serial.begin(9600);
	pinMode(butswitch, INPUT_PULLUP);
	pinMode(buzzer, OUTPUT);
	pinMode(propanePin, INPUT);
	digitalWrite(buzzer, LOW);
	myGSM.begin(19200);
	delay(100);
}

void loop()
{
	// Check if there's a new phone number command
	if (Serial.available() > 0) {
		String command = Serial.readStringUntil('\n');
		if (command.startsWith("PHONE1:")) {
			phoneNumber1 = command.substring(7);
			Serial.println("{\"phone_updated\":\"" + phoneNumber1 + "\",\"type\":\"primary\"}");
		}
		else if (command.startsWith("PHONE2:")) {
			phoneNumber2 = command.substring(7);
			Serial.println("{\"phone_updated\":\"" + phoneNumber2 + "\",\"type\":\"secondary\"}");
		}
	}

	butstate = digitalRead(butswitch);
	int propaneLevel = analogRead(propanePin);

	// Check for fire alarm
	if (butstate == LOW) {
		fireAlarmActive = true;
		ActivateAlarm("FIRE");
	} else {
		fireAlarmActive = false;
	}

	// Check for propane gas
	if (propaneLevel > propaneThreshold) {
		gasAlarmActive = true;
		ActivateAlarm("GAS");
	} else {
		gasAlarmActive = false;
	}

	// Check SMS balance periodically
	if (millis() - lastLoadCheck >= LOAD_CHECK_INTERVAL) {
		checkSMSBalance();
		lastLoadCheck = millis();
	}

	// Send status to Python server
	Serial.print("{\"fire_detected\":");
	Serial.print(fireAlarmActive ? "true" : "false");
	Serial.print(",\"gas_detected\":");
	Serial.print(gasAlarmActive ? "true" : "false");
	Serial.print(",\"sms_balance\":");
	Serial.print(smsBalance);
	Serial.println("}");
	delay(1000);
}

void ActivateAlarm(String type)
{
	ActivateBuzzer();
	MakeCall();
	SendMessage(type);
	DeactivateBuzzer();
}

void ActivateBuzzer()
{
	digitalWrite(buzzer, HIGH);
	delay(100);
}

void DeactivateBuzzer()
{
	digitalWrite(buzzer, LOW);
	delay(500);
}

void MakeCall()
{
	// Call primary number
	myGSM.println("ATD" + phoneNumber1 + ";");
	delay(100);
	myGSM.println("Calling primary");
	delay(100);
	
	// If secondary number exists, call it too
	if (phoneNumber2.length() > 0) {
		delay(1000); // Wait a bit between calls
		myGSM.println("ATD" + phoneNumber2 + ";");
		delay(100);
		myGSM.println("Calling secondary");
		delay(100);
	}
}

void SendMessage(String type)
{
	// Send to primary number
	myGSM.println("AT+CMGF=1");
	delay(100);
	myGSM.println("AT+CMGS=\"" + phoneNumber1 + "\"\r");
	delay(100);
	SendMessageContent(type);
	
	// If secondary number exists, send to it too
	if (phoneNumber2.length() > 0) {
		delay(1000); // Wait a bit between messages
		myGSM.println("AT+CMGF=1");
		delay(100);
		myGSM.println("AT+CMGS=\"" + phoneNumber2 + "\"\r");
		delay(100);
		SendMessageContent(type);
	}
}

void SendMessageContent(String type)
{
	if (type == "FIRE") {
		myGSM.println("FIRE IS DETECTED!");
	} else if (type == "GAS") {
		myGSM.println("DANGEROUS PROPANE GAS LEVEL DETECTED!");
	}
	delay(100);
	myGSM.println((char)26);
	delay(100);
}

void checkSMSBalance() {
	myGSM.println("AT+CUSD=1,\"*143#\""); // Replace with your carrier's balance check code
	delay(1000);
	
	String response = "";
	while(myGSM.available()) {
		char c = myGSM.read();
		response += c;
	}
	
	// Parse the response to extract balance
	// This is a simple example - adjust based on your carrier's response format
	if (response.indexOf("Balance") != -1) {
		// Extract number from response
		int startIdx = response.indexOf("Balance:") + 8;
		int endIdx = response.indexOf(" ", startIdx);
		String balanceStr = response.substring(startIdx, endIdx);
		smsBalance = balanceStr.toInt();
	}
}