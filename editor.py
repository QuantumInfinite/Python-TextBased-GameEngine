import curses
import pickle #Serialization module for python
import time
#COSC 2P05 Kyle Jones 6082994 kj16wn
#Template provided by Earl Foxwell

class Document:
	def __init__(self,filename = None):
		self.filename = filename if filename else "binary.bindoc" #default name if still None
		# usage: pages[page number][line number]

		startupText = [
			"#Start#                                                                        ",
			"<----------------------------------------------------------------------------->",
			"Welcome to the basic editor. Basic controlls are listed at the bottom of the   ",
			"page. All pages should begin with a #Header#. Link to pages like so:           ",
			"*Header*ChoiceDescription. You can have 3 links per page                       ",
			"As you are editing, links will be highlighted automatically if the page exists ",
			"Pressing 1, 2, or 3 will automatically jump to the linking page if it exists,  ",
			"Otherwise, a new page will be created for you                                  ",
			"Headers can have a $ in them, and if they do, everything after the $ is hidden ",
			"from the player.                                                               ",
			"In place of a link, you can put use &Header& to create a continued page        ",
			"Much like links, pressing 4 will jump to or create the linked page             ",
			"Navigate through recent pages with PGUP and PGDWN.                             ",
			"                                                                               ",
			" This would be a bad start to a story, so delete this page at any time with DEL"		
		]

		self.pages = [startupText]
		self.pageHistory = []
		self.current = 0
		#self.addPage()
		self.posInHistory = 0
		self.lastAction = ""

	def addPage(self):
		self.pages.append(["".ljust(80) for i in range(20)])
		self.lastPage()
		self.pageHistory.append(self.current)
		self.posInHistory = len(self.pageHistory) - 1

	def delPage(self, pageNumber):
		#Delete pages that are connected to this one
		for line in self.pages[pageNumber]:
			if line[0] == '&':
				ident = line[line.find('&') + 1 : line.rfind('&')]					
				pageNum = self.GetPageFromID(ident)
				if (pageNum >= 0):
					self.delPage(pageNum)

		self.pages.pop(pageNumber)
		self.pageHistory[:] = (x for x in self.pageHistory if x != pageNumber) #remove references to this page
		self.pageHistory[:] = (x - 1 if x > pageNumber else x for x in self.pageHistory) #Update page numbers 
		if len(self.pages) <= 0:
			self.addPage()
		else:
			self.prevPage()

	def setChr(self,r,charInput ,ltr): #probably easier this way than with an operator, because of the dual-index
		self.pages[self.current][r] = self.pages[self.current][r][:charInput ]+ltr+self.pages[self.current][r][charInput +1:]

	def nextPage(self):
		#self.current = (self.current+1)%len(self.pages)
		self.posInHistory = self.posInHistory +1 if (self.posInHistory + 1 < len(self.pageHistory)) else self.posInHistory
		self.current = self.pageHistory[self.posInHistory]

	def lastPage(self):
		self.current = len(self.pages) - 1

	def prevPage(self):
		#self.current = (self.current-1+len(self.pages))%len(self.pages)
		self.posInHistory = self.posInHistory - 1 if (self.posInHistory > 0) else self.posInHistory
		self.current = self.pageHistory[self.posInHistory] if (len(self.pageHistory) > 1) else 0
	def __str__(self):
		try:
			return "\n".join(self.pages[self.current])
		except:
			raise Exception(str(self.current) + " is out of range")
	def getIDFromPageNum(self, pageNum):
		line = self.pages[pageNum][0]
		return line[line.find('#') + 1 : line.rfind('#')]

	def GetPageFromID(self, pageID):
		for pageNum in range(0,len(self.pages)):
			if (pageID == self.getIDFromPageNum(pageNum)):
				return pageNum
		return -1
	def Jump(self, pageNum):
		if pageNum < len(self.pages):
			self.current = pageNum

	def VerifyPages(self):
		for pageNum in range(0,len(self.pages)):
			if (self.pages[pageNum][0][0] != '#'):
				return pageNum
		return -1
	def JumpToPage(self, pageNum):
		if pageNum < len(self.pages):
			self.current = pageNum
			self.pageHistory.append(self.current)
			self.posInHistory = len(self.pageHistory) - 1

	def GetPageHistory(self):
		if (len(self.pageHistory) > 0):
			return "->".join(str(x) for x in self.pageHistory) + "| " + str(self.posInHistory)
		return "No history"

	def TakePath(self, pathNumber):
		choiceCounter = 0
		for line in self.pages[self.current]:
			if (len(line) > 0 and line[0] == '*'):
				choiceCounter += 1
				if (choiceCounter == pathNumber):
					ident = line[line.find('*') + 1 : line.rfind('*')]					
					pageNum = self.GetPageFromID(ident)
					if(pageNum >= 0):
						self.pageHistory = self.pageHistory[0 : self.posInHistory + 1] #Remove pageHistory after this point, if it exists
						#self.pageHistory.append(self.current)
						self.JumpToPage(pageNum)
					else:
						self.addPage()
						self.pages[len(self.pages) - 1][0] = '#' + ident + '#' + ' ' * (80 - len(ident))
					return ident

	def ContinuePage(self):
		for line in self.pages[self.current]:
			if len(line) > 0 and line[0] == '&':
				ident = line[line.find('&') + 1 : line.rfind('&')]					
				pageNum = self.GetPageFromID(ident)
				if(pageNum >= 0):
					self.pageHistory = self.pageHistory[0 : self.posInHistory + 1] #Remove pageHistory after this point, if it exists
					#self.pageHistory.append(self.current)
					self.JumpToPage(pageNum)
				else:
					self.addPage()
					self.pages[len(self.pages) - 1][0] = '#' + ident + '#' + ' ' * (80 - len(ident))
				return ident
		
storyBook = Document()

def drawOutlog(scr, doc):
	height,width = scr.getmaxyx()
	if height < 24 or width < 80:
		scr.move(0,0)
		scr.erase()
		curses.doupdate()
		return
	scr.hline(20,0,'~',width)
	pos_p = str(doc.current+1)+'/'+str(len(doc.pages)) #Not displaying zero-based indexing
	scr.addstr(20,width-len(pos_p),pos_p)
	
	commands = [["^C: Quit", "^N: new story", "^O: Binary save", "^L: Binary load"],
		[outLog]]
	#Could've used A_UNDERLINE for this, but the other decorations aren't as widely-supported across terminals
	#There's a decent chance A_BOLD will work, too
	for r in range(2):
		ct = 0
		for cmd in commands[r]:
			scr.addstr(21+r,ct*20+5,cmd,curses.A_REVERSE)
			ct += 1
	if width > 80: #if we need to fill in the excess space to the right of the document...
		for line in range(height-4):
			scr.addstr(line,80," "*(width-80),curses.A_REVERSE)
	scr.move(0,0)
def drawscreen(scr,doc):
	#To be clear, curses supports some very good mechanisms for subdividing the terminal screen
	#	e.g. 'windows', 'pads', 'TextBox'es, etc.
	#However, they do add a couple (very minor) complications that wouldn't have been ideal for this first look.
	#It's up to you whether you'storyBook prefer to employ them for your final product, or if you'storyBook like to stick with this
	#duct-tape-y approach.
	
	curRow,curColumn = curses.getsyx()	

	drawOutlog(scr,doc)
	lines = str(doc).split('\n')
	for lineNumber in range(len(lines)):
		line = lines[lineNumber]
		if len(line) > 0 and (line[0] == '*'or line[0] == '&'):
			specialChar = '*' if '*' in line else '&'
			pageID = (line[line.find(specialChar) + 1 : line.rfind(specialChar)])
			if len(pageID) > 1 and doc.GetPageFromID(pageID) >= 0: #valid pageID and pageID found
				scr.addstr(lineNumber, 0, line, curses.A_STANDOUT)
			else:
				scr.addstr(lineNumber,0,line)
		else:
			scr.addstr(lineNumber,0,line)
	scr.move(curRow,curColumn)
	scr.refresh()

def sizecheck(scr):
	h,w = scr.getmaxyx()
	return h,w,h >= 24 and w >= 80

def main(stdscr):
	global storyBook #We need to bother with this, because storyBook will be reassigned during loading (which would otherwise make it local)
	global outLog 
	
	outLog = PadString("Please make new file or load existing")

	stdscr.clear()
	drawscreen(stdscr,storyBook)
	stdscr.move(0,0)
	s_height,s_width,enabled = sizecheck(stdscr)

	while True:
		charInput = stdscr.getch()
		if enabled:
			if charInput == curses.KEY_UP:
				curRow,curColumn = curses.getsyx() #There's honestly no need to have both the curses cursor position and separate variables
				curRow = max(curRow-1,0)
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_DOWN:
				curRow,curColumn = curses.getsyx()
				curRow = min(curRow+1,19)
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_LEFT:
				curRow,curColumn = curses.getsyx()
				curColumn = max(curColumn-1,0)
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_RIGHT:
				curRow,curColumn = curses.getsyx()
				curColumn = min(curColumn+1,79)
				stdscr.move(curRow,curColumn)
			
			elif curses.keyname(charInput) == '1': #Guess you guys arnt allowed to have numbers
				pathName = storyBook.TakePath(1)
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 1,0
				stdscr.move(curRow,curColumn)
			elif curses.keyname(charInput) == '2': #Guess you guys arnt allowed to have numbers
				storyBook.TakePath(2)
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 1,0
				stdscr.move(curRow,curColumn)
			elif curses.keyname(charInput) == '3': #Guess you guys arnt allowed to have numbers
				storyBook.TakePath(3)
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 1,0
				stdscr.move(curRow,curColumn)
			elif curses.keyname(charInput) == '4':
				storyBook.ContinuePage()
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 1,0
				stdscr.move(curRow,curColumn)

			elif charInput >= 32 and charInput <= 126: #Matches on any of teh 'standard' printable characters.
				curRow, curColumn = curses.getsyx()
				stdscr.addstr(curRow,curColumn,chr(charInput ))
				storyBook.setChr(curRow,curColumn,chr(charInput ))
				drawscreen(stdscr,storyBook)
				#stdscr.move(curRow,curColumn + 1)
				#outLog = PadString("(" + str(curRow) + " " + str(curColumn) + ")")
				if (curColumn < 79):
					stdscr.move(curRow,curColumn + 1)	
				else:
					if curRow < 19:
						stdscr.move(curRow + 1,0)
					

			elif charInput == curses.KEY_HOME: #Jump to start of the current lineNumber
				curColumn = 0
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_END: #Jump to end of the current lineNumber
				curColumn = 79
				stdscr.move(curRow,curColumn)


			elif charInput == curses.KEY_PPAGE: #PGUP (previous page)
				storyBook.prevPage()
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 0,0
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_NPAGE: #PGDN (next page)
				storyBook.nextPage()
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 0,0
				stdscr.move(curRow,curColumn)


			elif charInput == curses.KEY_IC: #Insert (add page)
				storyBook.addPage()
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 0,0
				stdscr.move(curRow,curColumn)
			elif charInput == curses.KEY_DC: #Delete (remove page)
				storyBook.delPage(storyBook.current)
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 0,0
				stdscr.move(curRow,curColumn)


			elif charInput == curses.KEY_BACKSPACE or curses.keyname(charInput ) == '^H': #^H is weirdness for some terminals
				curRow,curColumn = curses.getsyx()
				curColumn -= 1
				if curColumn < 0:
					curColumn = s_width-1
					curRow -= 1
					if curRow < 0:
						curRow = 0
						curColumn = 0
				stdscr.addch(curRow,curColumn,32)
				storyBook.setChr(curRow,curColumn,' ')
				drawscreen(stdscr,storyBook)
				stdscr.move(curRow,curColumn)

			elif charInput == 10: #linefeed
				curRow,curColumn = curses.getsyx()
				curColumn = 0
				curRow = min(curRow+1,19)
				stdscr.move(curRow,curColumn)
			
			elif curses.keyname(charInput) == '^K': #show page history path
				drawscreen(stdscr,storyBook)
				outLog = PadString(storyBook.GetPageHistory())
				drawOutlog(stdscr,storyBook)

			elif curses.keyname(charInput) == '^R': #Redraw screen
				drawscreen(stdscr,storyBook)

			elif curses.keyname(charInput) == '^X': #testing
				val = storyBook.GetPageFromID("Boss")
				storyBook.Jump(val)
				drawscreen(stdscr,storyBook)
				curRow,curColumn = 0,0
				stdscr.move(curRow,curColumn)
				
			elif curses.keyname(charInput ) == '^N': #ctrl+n - new story
				outLog = PadString("NewFile Name: ")
				drawOutlog(stdscr,storyBook)
				curses.echo()
				stdscr.move(22,20)
				storyBook.filename = stdscr.getstr(22,20)
				curses.noecho()
				outLog = PadString("Currently editing: " + storyBook.filename)
				drawscreen(stdscr,storyBook)
				stdscr.move(0,0)
			elif curses.keyname(charInput ) == '^L': #ctrl+l - Binary restore
				outLog = PadString("LoadFile Name: ")
				drawOutlog(stdscr,storyBook)
				curses.echo()
				stdscr.move(22,20)
				filename = stdscr.getstr(22,20)
				filename = filename if len(filename) > 0 else "binary.bindoc"
				curses.noecho()
				try:
					f = open(filename,'r') #open in 'read' mode
					storyBook = pickle.load(f)				
					f.close()
					storyBook.filename = filename
					storyBook.current = 0
					storyBook.pageHistory = [0]
					storyBook.posInHistory = 0
					outLog = PadString("Currently editing: " + storyBook.filename)
				except IOError: #e.g. if the file doesn't exist yet
					outLog = PadString("Could not open: " + filename)
					pass
				drawscreen(stdscr,storyBook)
				stdscr.move(0,0)
			elif curses.keyname(charInput ) == '^O': #ctrl+o - Binary save
				
				problemPage = storyBook.VerifyPages()
				
				if (problemPage < 0):
					f = open(storyBook.filename,'w') #open in 'write' mode
					pickle.dump(storyBook,f) #pickling is much simpler than Java serialization
					f.close()
					outLog = PadString("Save successful")
				else:
					outLog = PadString("Can not save because page " + str(problemPage + 1) + " is not named")
				
				drawscreen(stdscr,storyBook)
				
			elif charInput == curses.KEY_RESIZE: #As odd as it sounds, resizing the terminal is treated like any other character
				s_height,s_width,enabled = sizecheck(stdscr)
				drawscreen(stdscr,storyBook)
		else: #We want to keep everything disabled until the window is back to a legal size
			if charInput == curses.KEY_RESIZE: #We still need to listen for this one, so we'll know it's safe again
				s_height,s_width,enabled = sizecheck(stdscr)
				drawscreen(stdscr,storyBook)
		curses.doupdate()
		#drawscreen(stdscr,storyBook)

def PadString(ol):
	tmp = ol
	while (len(tmp) < 75):
		tmp += " "
	return tmp

#The try/except is just so pressing ctrl+charInput is treated as 'normal'
#If we'storyBook wanted to throw up a, "you have unsaved work!" warning, we could've put it inside the loop instead
try:
	curses.wrapper(main) #We use this wrapper to ensure the terminal is restored to a 'normal' state, even if something crashes
	pass
except KeyboardInterrupt:
	pass