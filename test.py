#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

bank1 = [ 2,  3,  4, 14, 18, 15, 17, 27]
bank2 = [22, 23, 24, 10,  9, 11, 25,  8]

banks = [bank1, bank2]

while True:
	for pins in banks:
		for pin in pins:
			tst = LED(pin, active_high=False)
			tst.on()
			sleep(0.5)
			tst.off
