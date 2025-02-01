// Import testing libraries
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

describe('Fire Alarm Monitor Frontend', () => {
	let dom;
	let container;

	beforeEach(() => {
		// Load the HTML file
		const html = fs.readFileSync(path.resolve(__dirname, './index.html'), 'utf8');
		dom = new JSDOM(html);
		global.document = dom.window.document;
		global.window = dom.window;
		global.fetch = jest.fn();
		container = document.body;
	});

	test('initial UI elements are present', () => {
		expect(container.querySelector('h1').textContent).toContain('Fire Alarm');
		expect(container.querySelector('#status')).toBeTruthy();
		expect(container.querySelector('#phoneForm')).toBeTruthy();
		expect(container.querySelector('#smsBalance')).toBeTruthy();
	});

	test('status updates correctly for danger state', () => {
		const statusDiv = container.querySelector('#status');
		const updateStatus = window.updateStatus;
		
		updateStatus(true);
		expect(statusDiv.classList.contains('danger')).toBeTruthy();
		expect(statusDiv.textContent).toContain('ALERT: Danger Detected!');
	});

	test('status updates correctly for safe state', () => {
		const statusDiv = container.querySelector('#status');
		const updateStatus = window.updateStatus;
		
		updateStatus(false);
		expect(statusDiv.classList.contains('safe')).toBeTruthy();
		expect(statusDiv.textContent).toContain('Status: Normal');
	});

	test('phone number update form validation', () => {
		const form = container.querySelector('#phoneForm');
		const input = container.querySelector('#phoneInput');
		
		input.value = '1234567890'; // Invalid format
		form.dispatchEvent(new window.Event('submit'));
		
		expect(input.validity.valid).toBeFalsy();
	});

	test('SMS balance updates correctly', () => {
		const balanceElement = container.querySelector('#smsBalance');
		const updateSMSBalance = window.updateSMSBalance;
		
		updateSMSBalance(50);
		expect(balanceElement.textContent).toBe('50');
	});

	test('history updates on danger detection', () => {
		const historyDiv = container.querySelector('#history');
		const updateStatus = window.updateStatus;
		
		updateStatus(true);
		expect(historyDiv.children.length).toBe(1);
		expect(historyDiv.firstChild.textContent).toContain('Danger detected!');
	});

	test('API calls are made correctly', async () => {
		global.fetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve({
				fire_detected: false,
				gas_detected: false,
				sms_balance: 75
			})
		});

		await window.getArduinoData();
		expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/api/status');
	});
});