import os
import string



def getTrainData():
	sports, grocery,clothing,vegetables,electronics, traindata = [], [], [],[],[],[]
	for filename in os.listdir("train"):
		
		if filename == "sports.txt":
			with open('train/'+filename) as f:
				sports = [(item, 'sports') for item in f.readlines()]
		if filename == "grocery.txt":
			with open('train/'+filename) as f:
				grocery = [(item, 'grocery') for item in f.readlines()]
		if filename == "clothing.txt":
			with open('train/'+filename) as f:
				clothing = [(item, 'clothing') for item in f.readlines()]
		if filename == "vegetables.txt":
			with open('train/'+filename) as f:
				vegetables = [(item, 'vegetables') for item in f.readlines()]
		if filename == "electronics.txt":
			with open('train/'+filename) as f:
				electronics = [(item, 'electronics') for item in f.readlines()]
		print(filename)

	for (words, category) in sports+grocery+clothing+vegetables+electronics:
		words_filtered = [e for e in words.split() if len(e) > 2]
		traindata.append((words_filtered, category))

	return traindata


def export(filename, data, p):
	with open(filename, p) as output:
		for line in data:
			output.write(line)

