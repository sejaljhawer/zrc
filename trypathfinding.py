import math
from pathfinding.core.grid import Grid
from pathfinding.finder.breadth_first import BreadthFirstFinder
from time import sleep
delay = 0


layout = [
  [1, 1, 1, 1, 1, 0, 0, 0],
  [0, 0, 0, 1, 1, 1, 1, 1],
  [1, 1, 1, 1, 1, 1, 1, 1], 
  [1, 1, 1, 1, 1, 1, 1, 1], 
  [0, 0, 0, 1, 1, 1, 1, 1], 
  [1, 1, 1, 1, 1, 1, 1, 1], 
  [1, 1, 1, 1, 1, 1, 1, 1], 
  [1, 1, 1, 1, 1, 1, 1, 1], 
]
grid = Grid(matrix=layout)

# returns the shelf the roomba is at / picking up items from
def getCurrShelf():
	global currY
	if currY == 1:
		return 0			#return stockroom 
	if currY == 2:
		return 1 			#return shelf # 1
	if currY == 3:
		return 2		# shelf number 2

def getCurrShelfPos():
	global currX
	return currX % 5
	# if currX == 0 or currX == 5:
	# 	return 0 		#shelf spot's number 1 is position 0 in the ItemPos / taskMatrix grid
	# elif currX == 1 or currX == 6:
	# 	return 1
	# else : # if currX == 2 or currX == 7:
	# 	return 2


# ISSUE: remove whitespaces??? 
# Creates an array of the tasklist data out of the string read from the barcode
def parseTaskData(data):
	data = data.split('\n')
	taskList = []
	for row in data: 
		row = row.split(',')
		taskList.append(row)

	#convert into a 3 by 3 matrix
	taskMatrix = [ [0, 0, 0] for i in range(3)]
	for task in taskList:
		shelfName = 0
		if task[0] == 'S1':
			shelfName = 0
		elif task[0] == 'A1':
			shelfName = 1
		else: 
			shelfName = 2
		position = int(task[1]) - 1
		taskMatrix[shelfName][position] = task[2].strip()
		#print(int(task[1]))
	return taskMatrix

# See which of our bins has space to put stuff in 
def findEmptyBin():
	global bins
	if bins[0] == False:
		return 0
	elif bins[1] == False:
		return 1
	elif bins[2] == False: 
		return 2
	else: return -1

# Check which bin is empty
# Update record keeping of bins
# Actually mechanically put item in bin
# remove item from shelf record keeping
def putInBin(barcodeData):
	global bins
	global itemPositions
	emptyBin = findEmptyBin()
	bins[emptyBin] = barcodeData
	# Serial commands to pick up and put in bin go here
	itemPositions[getCurrShelf()][getCurrShelfPos()] = 0

	
def inCorrectSpot():
	return itemPositions[getCurrShelf()][getCurrShelfPos()] == tasks[getCurrShelf()][getCurrShelfPos()]


def putOnShelf():
	global bins
	global itemPositions
	global tasks

	item = tasks[getCurrShelf()][getCurrShelfPos()] # what we want to put on the spot

	for i in range(3): 
		if bins[i] == item:
			# serially pick up item from bin[i]
			# serial put item on shelf
			itemPositions[getCurrShelf()][getCurrShelfPos()] = item
			bins[i] = False




# ISSUE: When scanning, it’s adding a leading 0 to the front of UPCA barcodes, which is causing errors in bins. Added [1:]
# image variable must come in correctly somehow
# can scan both UPCA barcodes on the items, or QR codes on the task list
# adds barcodes after reading to their appropriate record-keeping spots (tasks or itemPositions)
def decipherBarcode(image): #, symbology):
	from pyzbar.pyzbar import decode
	from PIL import Image
	from pyzbar.pyzbar import ZBarSymbol
	barcodes = decode(Image.open(image)) #, symbols=[ZBarSymbol.QRCODE]) #optional
	#decode(image, symbols=[symbology]) # optional, for zbar symbol . data returns the string of info

	symbology = 0

	if barcodes:
		for barcode in barcodes: 
			barcodeData = barcode.data.decode("utf-8")[1:] 		#returns the ID in this case, ID is a string
			#print(isinstance(barcodeData, str))
			symbology = barcode.type 
			print("[INFO] Found {} barcode: {}".format(symbology, barcodeData))

		global tasks
		global itemPositions
		if symbology == 'QRCODE': #ISSUE HERE "QRCODE not defined??????"
			tasks = parseTaskData(barcodeData)
			#print(tasks)
		else:									#if symbology == UPCA: (we have an item)
			

			print("about to update itemPositions")
			itemPositions[getCurrShelf()][getCurrShelfPos()] = barcodeData

			if not inCorrectSpot():
				putInBin(barcodeData)
		if symbology != 'QRCODE': #if we're not at task list and we're actually at a shelf
			putOnShelf() # check if we need to put something from our bins in the spot (either we took something off)
	else: 
		putOnShelf()



def readTaskList():
	goToPosition(7, 4)
	rotateRoombaDegrees(270) # face east. since we start at bottom facing north, we only need to turn 90 degrees
	# move arm to get into position to take picture
	# actually make camera scan/take picture on raspberry pi
	# convert picture to a numpy array
	# send this array here and convert back to an image. 
	# store this image in the correct location
	image = 'qrcode.png'
	#symbology = ZBarSymbol.QRCODE
	decipherBarcode(image) #, symbology) # scan and make the data
	# parseTaskData(data)




# Assumes direction/orientation is already correct
def mechanicalMoveForwardOne():
	pass
	# move forward one serially


# Fill in with Mechanical/ serial aspect of rotation, also updates currRotation in record-keeping
# same as your rotate(degrees, speed = None) except added last 2 lines
def rotateRoombaDegrees(degrees): 
	degrees %= 360	 	# negative numbers become positive ( - 90 becomes 270)
	if (degrees < 1 and degrees > 0): 
		degrees = 0
	if (degrees == 90):
		# serial commands to turn left 90
		pass
	elif (degrees == 180):
		pass
	elif (degrees == 270): 		# serial to turn right 90
		pass
	global currRotation
	currRotation = (currRotation + degrees) % 360



def faceShelf(): 	
	if getCurrShelf() == 0 or 1:	 	#if at stockroom or shelf 1
		faceDegree(90)
	else: #getCurrShelf() == 2:			#at shelf 2
		faceDegree(270)


# Fix determinant sign so we can reuse the code
def faceDegree(degreeToFace):
	bx = math.cos(math.radians( degreeToFace ))
	by = math.sin(math.radians( degreeToFace ))
	desiredVector = (bx, by)
	calculateDegreesToRotate(desiredVector, 1) # OPPOSITE SAD


# Calculates degrees to rotate and then actually makes the roomba rotate by calling rotateRoombaDegrees
# desiredVector is of degrees that we want to face (with moveOneSpot, because of direction we want to face)
def calculateDegreesToRotate(desiredVector, determinantSign): ###Fix determinant sign
	ax = math.cos(math.radians( currRotation ))
	ay = math.sin(math.radians( currRotation ))
	currOrientationVector = ( ax, ay )		#convert degrees to radians for math library. cos(theta), sin(theta)
	(bx, by) = desiredVector
	determinant = ax*by - bx*ay 	# -1, 0, or 1
	if (determinant < 1 and determinant > 0): # fix rounding
		determinant = 0
	if determinant == 0:  		#determinant of two vectors of matrices, either orientation aligned with direction of travel or not
		if desiredVector != currOrientationVector: # not aligned with direction of travel (facing 180 away from it)
			rotateRoombaDegrees(180) 
	else:   								# roomba needs to turn 90 degrees in a particular direction
		rotateRoombaDegrees(determinantSign*90*determinant) 	#sign is -1 with moveOneSpot, 1 for faceDegree
	




# Record-keeping, decides orientation and how many degrees necessary to turn/rotate. Also claculates number of degrees to rotate
def moveOneSpot(x, y): 	#destination coordinates
	sleep(delay)
	printPos()
	global currX, currY, currRotation
	if x >= 0  and  x <= 7 and y >= 0 and y <= 7 : # make sure new spot is in bounds. There is a grid.inside(x, y) bool function, how to access grid??
		# ROTATION STUFF
		bx = x - currX  		#delta position is (bx, by)
		by = y - currY		#tuple / vector of how much to go in each direciton, either -1, 0, or 1
		deltaPosVector = (bx, by)
		calculateDegreesToRotate(deltaPosVector, -1)
 		# MOVEMENT STUFF
		currX = x 			# update where we are in record-keeping
		currY = y
		mechanicalMoveForwardOne()
		



# feed it a destination coordinate
def goToPosition(endX, endY):
	global currX, currY
	path = findPath(currX, currY, endX, endY)
	for coordinate in path[1:]:
		(x, y) = coordinate
		moveOneSpot(x, y)

#for debugging to see where we are
def printPos():
	print(grid.grid_str(start = grid.node(currX, currY)))
	print("Facing: ")
	print(currRotation)
	print(currX, currY)




#from pathfinding.core.diagonal_movement import DiagonalMovement
def findPath(sx, sy, ex, ey):

	grid = Grid(matrix=layout) # to reset the grid and remove old marks

	start = grid.node(sx, sy)
	end = grid.node(ex, ey)

	finder = BreadthFirstFinder() #finder = BreadthFirstFinder(diagonal_movement=DiagonalMovement.never)
	
	path, runs = finder.find_path(start, end, grid)

	# print('operations:', runs, 'path length:', len(path))
	# print(grid.grid_str(path=path, start=start, end=end))
	# print(path) 

	return path

# Serial necessary here
def goUpToShelfAndBack():
	faceShelf()
	# Serial move until bumpers are hit. DO NOT CALL MOVEONESPOT, it will update the global variables of position incorrectly
	image = 'upca998877665128.gif' # take Picture of barcodes and store image somewhere
	decipherBarcode(image)
	rotateRoombaDegrees(180) #turn around
	# serial move, go back until we are back on the intersection
	# faceDegree(shelfDirectionOfTravel) MOVED SOMEWHERE ELSE



# go to the end of the destination shelf that is closest to us
# 3 variables: where we are (shelf and position), shelf we want to go to
def goToClosestEndOfDesiredShelf(desiredShelf):
	shelfY = 0;
	if desiredShelf == 0:
		shelfY = 1
	elif desiredShelf == 1:
		shelfY = 2
	else:
		shelfY = 3

	shelfX = 0

	print(shelfY, getCurrShelf(), getCurrShelfPos(), desiredShelf)

	if currX == 7 and currY == 4: # reading task list at the beginning
		shelfX = 7 	# go to stock room third spot
	elif (getCurrShelfPos() == 0) and (desiredShelf == (1 or 2)) and (getCurrShelf() == 0):
		print("going to shelf1. or even shelf2 from stockroom")
		shelfX = 2	
	elif (getCurrShelfPos() == 0) and (desiredShelf == (1 or 2)) and (getCurrShelf() == (1 or 2)): #at normal shelves 
		print("going between shelves 1, 2[0]")
		shelfX = 0
	elif (getCurrShelfPos() == 2) and (desiredShelf == (1 or 2)) and (getCurrShelf() == (1 or 2)): # at normal shelves
		print("going between shelves 1, 2[2]")
		shelfX = 2
	# elif (desiredShelf == 1 or 2) and (getCurrShelf() == 0): # at stockroom
	# 	shelfX = 2
	elif ((getCurrShelf() == (1 or 2)) and (desiredShelf == 0)): #trying to go stockroom, always go to one spot
		print("going back to stockroom") 				# ISSUE: it's not going back to stock room/ entering this
		# while True:
		# 	try:exec(input("DEBUG: "))
		# 	except KeyboardInterrupt:break
		# 	except Exception as E:print("ERROR:"+str(E))
		shelfX = 5
	elif (getCurrShelf() ==  2 and (desiredShelf == 0) and getCurrShelfPos()==2):
		print("shelf 2, pos 2, going to stockroom")
		shelfX = 5

	goToPosition(shelfX , shelfY)


def getShelfDirectionOfTravel():
	return getCurrShelfPos() * 90 # shelf spot 0 is 0 degrees, shelf spot 2 is 180

# unlike the other moveOneSpot, this one doesn't take desitnation coordinates. instead just serially moves forward in whichever
# direction it is already facing, and updates record keeping of curr information
def moveOneForward():
	sleep(delay)
	global currX, currY
	orientation = currRotation % 360
	if orientation == 0:
		currX += 1
	elif orientation == 180:
		currX -= 1
	elif orientation == 90:
		currY -= 1
	else: #orientation == 270
		currY += 1
	printPos()
	mechanicalMoveForwardOne()

def allBinsEmpty():
	return ((bins[0] == False) and (bins[1] == False) and (bins[2] == False))




# reads all 3 barcodes/positions along a shelf 
# maintains direction of travel, except after the last barcode / image 
# must be at position 0 or position 2 (not the middle of the shelf) when calling this 
def traverseShelf(): 
	global currX, currY
	shelfDirectionOfTravel = getShelfDirectionOfTravel()	
	goUpToShelfAndBack()
	#print("just went to 1st shelf spot and back, facing south")
	faceDegree(shelfDirectionOfTravel)
	#print("now facing degree of travel")
	moveOneForward()
	goUpToShelfAndBack()
	#print("just went to 2nd shelf spot and back, facing south")
	#print(currX, currY,  currRotation, getCurrShelf(), getCurrShelfPos())
	faceDegree(shelfDirectionOfTravel)
	#print("face Direction of Travel")
	#print(currX, currY,  currRotation, getCurrShelf(), getCurrShelfPos())
	moveOneForward()
	goUpToShelfAndBack()
	#print("just went to 3rd shelf spot and back, facing south")
	#print(currX, currY,  currRotation, getCurrShelf(), getCurrShelfPos())

#get the shelf and position indices in tasks list
def getShelfandPosition(itemID):
	l = sum(tasks, [])
	index = l.index(itemID)
	shelf = index // len(l)
	shelfPosition = index % 3
	return shelf, shelfPosition


# get indices of itemID, go to that shelf
def findNextShelf():
	shelves = [0 for i in range(3)]
	for itemID in bins: 
		if itemID:  # not false
			shelf, shelfPosition = getShelfandPosition(itemID)


			# l = sum(tasks, [])
			# index = l.index(itemID)
			# shelf = index // len(l)
			# shelfPosition = index % 3
			shelves[shelf] += 1

	# while True:
	# 	try:exec(input("DEBUG: "))
	# 	except Exception as E:print("ERROR:"+str(E))
	# 	except KeyboardInterrupt:break		

	if shelves[2]: 					
		goToClosestEndOfDesiredShelf(2)
		faceDegree(180)
	elif shelves[1]:
		goToClosestEndOfDesiredShelf(1)
	elif shelves[0]:
		print("should go straight to stockroom")
		print(currX, currY)
		goToClosestEndOfDesiredShelf(0)




def start():
	# global shelfDirectionOfTravel
	# shelfDirectionOfTravel = 180 
	readTaskList()
	goToClosestEndOfDesiredShelf(0) # goToStockRoom()
	print("before reading stockRoom")
	traverseShelf()
	print("before going to Shelf1")
	print(currX, currY,  currRotation, getCurrShelf(), getCurrShelfPos())
	goToClosestEndOfDesiredShelf(1)
	traverseShelf()
	print("before going to Shelf2")
	goToClosestEndOfDesiredShelf(2) 
	traverseShelf()
	print(bins)
	print(tasks)
	# Second half allowing for optimizations
	if not allBinsEmpty():
		findNextShelf()  	# determine and go to next logical shelf


		# put everything in that shelf in correct spot
	# To finish, go to closest part of break room

	# while True:
	# 	try:exec(input("DEBUG: "))
	# 	except KeyboardInterrupt:break
	# 	except Exception as E:print("ERROR:"+str(E))


# From top to bottom: 
# Stockroom: Spots 0, 1, 2
# Shelf one: Spots 0, 1, 2
# Shelf two: Spots 0, 1, 2
itemPositions = [ [0, 0, 0] for i in range(3)]
bins = [False for i in range(3)] #contains ID of item in Bin 0, 1, 2
tasks = 0 #this will be the global task list
shelfDirectionOfTravel = 0


currX = 7
currY = 7
currRotation = 0	 # 0 = facing east, 90 = facing north, 180 = facing west, 270 = facing south (-90) <-- BUT would be better to turn left 90
start()
