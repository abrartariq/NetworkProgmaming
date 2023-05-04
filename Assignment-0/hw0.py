# Edit this file so that it contains your complete solution to homework 0.
from datetime import datetime
import os

print("mtariq5@uic.edu")
print(["Muhammad","Abrar","Tariq"])
print(datetime.now())


def four(start,stop,step):
	ansList = list()
	while start<stop:
		ansList.append(start)
		start = start+step
	return ansList

print(four(17,40,6))
os.system("python -V")