# Fire Alarm System

A web-based fire alarm monitoring system with SMS notifications and gas detection capabilities.

## Setup Instructions

### Prerequisites
- Python 3.7+
- Arduino IDE
- GSM Module
- MQ-6 Gas Sensor
- Fire Alarm Button
- Buzzer

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Upload Arduino code:
   - Open `fire_alarm_gsm.ino` in Arduino IDE
   - Connect your Arduino board
   - Select correct board and port
   - Upload the code

3. Start the server:
```bash
python server.py
```

4. Access the web interface:
   - Open `http://localhost:5000` in your browser

## Testing

### Running Tests

The tests are located in the `tests` directory. To run the tests:

1. Server tests:
```bash
python -m unittest tests/test_server.py
```

2. Manual tests:
```bash
python tests/test_manual.py
```

The tests cover:
- Server endpoints
- Phone number validation
- Arduino communication
- SMS balance tracking
- Gas detection
- Error handling

### Manual System Testing

1. **Web Interface Testing**:
   - Check if status updates every 3 seconds
   - Verify phone number update functionality
   - Monitor SMS balance display
   - Observe alert history

2. **Hardware Testing**:
   - Press the fire alarm button
   - Check if buzzer activates
   - Verify SMS is sent
   - Test gas sensor with a safe gas source
   - Confirm phone call is received

3. **Error Scenarios**:
   - Disconnect Arduino and verify fallback behavior
   - Enter invalid phone number
   - Test system with low SMS balance

### Test Cases

1. **Phone Number Update**:
   - Input: "+639123456789" (Valid)
   - Expected: Success message
   - Input: "1234567890" (Invalid)
   - Expected: Error message

2. **Alarm Detection**:
   - Trigger fire alarm
   - Expected: 
     - UI shows danger state
     - SMS sent
     - Call initiated
     - History updated

3. **Gas Detection**:
   - Expose sensor to gas
   - Expected:
     - UI shows danger state
     - SMS sent
     - History updated

4. **SMS Balance**:
   - Check balance display
   - Verify updates after sending messages

## Troubleshooting

1. **Arduino Connection Issues**:
   - Check COM port in `server.py`
   - Verify baud rate (9600)
   - Check USB connection

2. **GSM Module Issues**:
   - Verify SIM card installation
   - Check signal strength
   - Confirm balance

3. **Sensor Problems**:
   - Calibrate gas sensor
   - Check wiring connections
   - Verify power supply

## Notes

- The system runs in simulation mode if Arduino is not connected
- Tests can be run without hardware using mock objects
- Default refresh rate is 3 seconds for status updates