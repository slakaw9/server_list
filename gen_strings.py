#!/bin/env python2.7

import random, string

def gen_random_strings(arr, l, longer=False):
	l+=5 if longer else 0
	for idx, i in enumerate(arr):
		x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(l))
		arr[idx] = x
	return arr