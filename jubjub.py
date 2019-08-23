import curses
import re as regex
import pickle #Serialization module for python


#COSC 2P05 Kyle Jones 6082994 kj16wn
#Template provided by Earl Foxwell
class Document:
	"""Pages are presumed to have dimensions of 80 wide by 20 tall."""
	def __init__(self,filename = None):
		self.filename = filename if filename else "binary.bindoc" #default name if still None
		self.pages = [[" "]]
		self.pageHistory = []
		self.current = 0
		self.posInHistory = 0
		self.lastAction = ""

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
		self.current = self.pageHistory[self.posInHistory]
	def __str__(self):
		try:
			return "\n".join(self.pages[self.current])
		except:
			raise Exception(str(self.current) + " is out of range")
	
	def getLastAction(self):
		return self.lastAction if hasattr(self, 'lastAction') else " "

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
						self.lastAction = line[line.rfind('*') + 1 : len(line)]
						self.pageHistory = self.pageHistory[0 : self.posInHistory + 1] #Remove pageHistory after this point, if it exists
						#self.pageHistory.append(self.current)
						self.JumpToPage(pageNum)
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

def drawscreen(scr,doc):
	#To be clear, curses supports some very good mechanisms for subdividing the terminal screen
	#	e.g. 'windows', 'pads', 'TextBox'es, etc.
	#However, they do add a couple (very minor) complications that wouldn't have been ideal for this first look.
	#It's up to you whether you'storyBook prefer to employ them for your final product, or if you'storyBook like to stick with this
	#duct-tape-y approach.
	height,width = scr.getmaxyx()
	if height < 24 or width < 80:
		scr.move(0,0)
		scr.erase()
		curses.doupdate()
		return
	pos_r,pos_c = curses.getsyx()
	scr.hline(20,0,'~',width)
	pos_p = str(doc.current+1)+'/'+str(len(doc.pages)) #Not displaying zero-based indexing
	scr.addstr(20,width-len(pos_p),pos_p)
	
	commands = [["^C: Quit", "^L: Binary load", "^K: Restart"],
		[outLog]]
	#Could've used A_UNDERLINE for this, but the other decorations aren't as widely-supported across terminals
	#There's a decent chance A_BOLD will work, too
	for r in range(2):
		ct = 0
		for cmd in commands[r]:
			scr.addstr(21+r,ct*20+5,cmd,curses.A_BOLD)
			ct += 1
	if width > 80: #if we need to fill in the excess space to the right of the document...
		for row in range(height-4):
			scr.addstr(row,80," "*(width-80),curses.A_REVERSE)
	scr.move(0,0)
	lines = str(doc).split('\n')
	choiceCounter = 0
	for lineNumber in range(len(lines)):
		line = lines[lineNumber]

		#Format room title
		#All text after a '$' is ommited from the jubjub viewer, allowing multiple rooms to share the 'same' room name

		if (line[0] == '#'):
			dollarIndex = line.find('$') if '$' in line else line.rfind('#')	
			line =  line[1 : dollarIndex]
			lastAction = doc.getLastAction()
			line = ("(" + lastAction.rstrip() + ") -> " + line) if len(lastAction) > 0 else line
			line += " " * (80 - len(line))
			scr.addstr(lineNumber, 0, line, curses.A_STANDOUT )
		#Format choices 
		elif (line[0] == '*'):
			pageID = line[line.find('*') + 1 : line.rfind('*')]
			if len(pageID) > 1 and doc.GetPageFromID(pageID) >= 0: #valid pageID and pageID found 
				choiceCounter += 1
				regexLine = regex.sub('\*.+?\*', '', line)
				scr.addstr(lineNumber,0,"[" + str(choiceCounter) + "]" + regexLine)
			else:
				scr.addstr(lineNumber, 0, " " * 80)
		elif (line[0] == "&"):
			regexLine = regex.sub('\&.+?\&', '', line)
			scr.addstr(lineNumber,0,"[ENTER]" + regexLine)
		else:
			scr.addstr(lineNumber, 0, line)

	scr.move(pos_r,pos_c)

def sizecheck(scr):
	h,w = scr.getmaxyx()
	return h,w,h >= 24 and w >= 80

def main(stdscr):
	global storyBook #We need to bother with this, because storyBook will be reassigned during loading (which would otherwise make it local)
	global outLog 
	curses.curs_set(0)
	outLog = "Welcome to JubJub. Load a game already"

	stdscr.clear()
	drawscreen(stdscr,storyBook)
	stdscr.move(0,0)
	s_height,s_width,enabled = sizecheck(stdscr)
	
	while True:
		charInput = stdscr.getch()
		if enabled:
			#Why are these in a tonberry of if/elif's? Because... I can?					
			if charInput == curses.KEY_PPAGE: #PGUP (previous page)
				#storyBook.prevPage()
				#drawscreen(stdscr,storyBook)
				pos_r,pos_c = 0,0
				stdscr.move(pos_r,pos_c)
			elif charInput == curses.KEY_NPAGE: #PGDN (next page)
				#storyBook.nextPage()
				#drawscreen(stdscr,storyBook)
				pos_r,pos_c = 0,0
				stdscr.move(pos_r,pos_c)
			elif charInput == curses.KEY_BACKSPACE or curses.keyname(charInput ) == '^H': #^H is weirdness for some terminals
				pos_r,pos_c = curses.getsyx()
				pos_c -= 1
				if pos_c < 0:
					pos_c = s_width-1
					pos_r -= 1
					if pos_r < 0:
						pos_r = 0
						pos_c = 0
				stdscr.addch(pos_r,pos_c,32)
				storyBook.setChr(pos_r,pos_c,' ')
				stdscr.move(pos_r,pos_c)
			elif curses.keyname(charInput) == '1':
				storyBook.TakePath(1)
			elif curses.keyname(charInput) == '2':
				storyBook.TakePath(2)
			elif curses.keyname(charInput) == '3':
				storyBook.TakePath(3)
			elif charInput == 10: #enter
				storyBook.ContinuePage()

			elif curses.keyname(charInput) == '^K': #Restart
				try:
					f = open(storyBook.filename,'r') #open in 'read' mode
					storyBook = pickle.load(f)
					f.close()
					storyBook.current = 0
					storyBook.pageHistory = [0]
					storyBook.posInHistory = 0
					outLog = PadString("Currently Playing: " + storyBook.filename)
				except IOError: #e.g. if the file doesn't exist yet
					outLog = PadString("Could not open: " + filename)
					pass
				drawscreen(stdscr,storyBook)				

			elif curses.keyname(charInput ) == '^L': #ctrl+l - Binary restore
				outLog = PadString("LoadFile Name: ")
				drawscreen(stdscr,storyBook)
				curses.echo()				
				curses.curs_set(1)
				stdscr.move(22,20)
				filename = stdscr.getstr(22,20)
				filename = filename if len(filename) > 0 else "binary.bindoc"
				curses.curs_set(0)
				curses.noecho()
				try:
					f = open(filename,'r') #open in 'read' mode
					storyBook = pickle.load(f)				
					f.close()
					storyBook.filename = filename
					storyBook.current = 0
					storyBook.pageHistory = [0]
					storyBook.posInHistory = 0
					outLog = PadString("Currently Playing: " + storyBook.filename)
				except IOError: #e.g. if the file doesn't exist yet
					outLog = PadString("Could not open: " + filename)
					pass
				drawscreen(stdscr,storyBook)
				stdscr.move(0,0)		
			elif charInput == curses.KEY_RESIZE: #As odd as it sounds, resizing the terminal is treated like any other character
				s_height,s_width,enabled = sizecheck(stdscr)
				#drawscreen(stdscr,storyBook)
			#else: #eventually delete this
			#	stdscr.addstr(0,0,curses.keyname(charInput ))
		else: #We want to keep everything disabled until the window is back to a legal size
			if charInput == curses.KEY_RESIZE: #We still need to listen for this one, so we'll know it's safe again
				s_height,s_width,enabled = sizecheck(stdscr)
		drawscreen(stdscr,storyBook)		
		curses.doupdate()
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