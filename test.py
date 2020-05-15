#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

bank1 = [ 2,  3,  4, 14, 18, 15, 17, 27]
bank2 = [22, 23, 24, 10,  9, 11, 25,  8]

banks = [bank1, bank2]

while True:
	b = 0
	for pins in banks:
		b = b + 1
		p = 0
		for pin in pins:
			p = p + 1
			print('Testing pin #%d, bank %d, output %d' % (pin, b, p))
			tst = LED(pin, active_high=False)
			tst.on()
			#sleep(3)
			input('Press enter to test next one...')
			tst.off
