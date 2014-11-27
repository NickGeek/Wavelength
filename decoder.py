"""
Wavelength - Basic networking over sound
Copyright (c) Nick Webster 2014
This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/

Usage
python3 decoder.py file.wav

Notes
* Reads 16bit WAV files
* Data in 2 bit chunks
* Frequency decided by: 2^(3+n). Nmin = 0, Nmax = 3
* Chunks last 1ms
* 00 = >5400
* 01 = >5000<5400
* 10 = >4000<5000
* 11 = <4000
* Create a sine wave going from 2^(3+n) to 2^(3+n)*100, (e.g. 8Hz to 800Hz), they will average out to give the above chunks.
* This is easiest created using the chirp function in audacity
* Use a amplitude of 0.1 and 1.8

Units
* Bit = 1 binary digit
* Chunk = 2 consecutive bits (2 binary digits)
* Block = 4 consecutive chunks (8 bits, 8 binary digits)

"""

import wave
import struct
import sys
import string
import math

def binaryToASCII(binary):
	v000 = ['\0', '␁', '␂', '␃', '␄', '␅', '␆', '\a', '\b', '\t', '\n', '\v', '\f', '\r', '␎', '␏', '␏', '␐', '␑', '␒', '␒', '␔', '␕', '␖', '␗', '␘', '␙', '␚', '␛', '␜', '␝', '␞', '␟'] #Instructions
	v001 = [' ', '!', '"', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ':', ';', '<', '=', '>', '?'] #Numbers and punctuation
	v010 = ['@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_'] #Uppercase and a few special chars
	v011 = ['`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '␡'] #Lowercase and a few special chars

	binary = [binary[i:i+8] for i in range(0, len(binary), 8)]
	output = ""
	for i in range(0, len(binary)):
		asciiHeaders = binary[i][0:3]
		asciiBody = binary[i][3:8]

		totalCount = 0
		if asciiHeaders == "000":
			#Instructions
			if asciiBody[-1] == "1": totalCount += 1
			if asciiBody[-2] == "1": totalCount += 2
			if asciiBody[-3] == "1": totalCount += 4
			if asciiBody[-4] == "1": totalCount += 8
			if asciiBody[-5] == "1": totalCount += 16
			output += v000[totalCount]
		elif asciiHeaders == "001":
			#Numbers and punctuation
			if asciiBody[-1] == "1": totalCount += 1
			if asciiBody[-2] == "1": totalCount += 2
			if asciiBody[-3] == "1": totalCount += 4
			if asciiBody[-4] == "1": totalCount += 8
			if asciiBody[-5] == "1": totalCount += 16
			output += v001[totalCount]
		elif asciiHeaders == "010":
			#Upper case
			if asciiBody[-1] == "1": totalCount += 1
			if asciiBody[-2] == "1": totalCount += 2
			if asciiBody[-3] == "1": totalCount += 4
			if asciiBody[-4] == "1": totalCount += 8
			if asciiBody[-5] == "1": totalCount += 16
			output += v010[totalCount]
		elif asciiHeaders == "011":
			#Lower case
			if asciiBody[-1] == "1": totalCount += 1
			if asciiBody[-2] == "1": totalCount += 2
			if asciiBody[-3] == "1": totalCount += 4
			if asciiBody[-4] == "1": totalCount += 8
			if asciiBody[-5] == "1": totalCount += 16
			output += v011[totalCount]
	return output

def decodeWav(wavfile):
	try:
		audioFile = wave.open(wavfile)
	except IndexError:
		print("No wav file passed")
		sys.exit(1)

	chunks = int(round(audioFile.getnframes()/float(audioFile.getframerate()), 3)*1000)
	binary = ""
	for i in range(0, chunks):
		chunkNum = i+1
		audioList = []
		for j in range(int(str(audioFile.getframerate())[0:2])*(chunkNum-1), int(str(audioFile.getframerate())[0:2])*chunkNum):
			data = audioFile.readframes(1)
			data = struct.unpack("<h", data)
			audioList.append(data[0])

		#Get average frequency
		audioList.sort()
		total = 0
		for i in range(0, len(audioList)):
			total += audioList[i]
		average = total/len(audioList)

		if average > 5400:
			binary += "00"
		elif average > 5000 and average < 5400:
			binary += "01"
		elif average > 4000 and average < 5000:
			binary += "10"
		elif average < 4000:
			binary += "11"
	return binary


print(binaryToASCII(decodeWav(sys.argv[1])))