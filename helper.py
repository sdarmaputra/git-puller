import datetime

def printLog(*string):
	print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '->',
	for i in string:
		print i,
	print ''

def main():
	print "Helper library!"

if __name__ == "__main__":
	main()
	