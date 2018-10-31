#import the library needed to access web pages
import urllib2

#import the library needed to parse the web page
from bs4 import BeautifulSoup
#from sets import Set

import csv
import numpy
from sets import Set
from anew_module import anew
import numpy
import pandas
import math

class Scene:
	name = ""
	textByCharacter = {}
	index = 0

	def __init__(self, name, index):
		self.name = name
		self.index = index

	def setCharacterText(self, text, character):
		self.textByCharacter[character] = text
	def getCharacterText(self, character):
		return self.textByCharacter[character]

class Line:
	text = ""
	index = 0
	valence = 0
	arousal = 0
	scene = 0

	def __init__(self, index, text, valence, arousal):
		self.text = text
		self.index = index
		self.valence = valence
		self.arousal = arousal
	def setValence(self, valence):
		self.valence = valence
	def setArousal(self, arousal):
		self.arousal = arousal
	def setScene(self, scene):
		self.scene = scene
	def getValence(self):
		return self.valence
	def getArousal(self):
		return self.arousal
	def getScene(self):
		return self.scene
	def getText(self):
		return self.text

def parseHtml(url):
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	return soup

def getCharacterLines(character, tags):
	num = 0
	for tag in tags:
		if(character.strip() in tag.getText()):
			num+=1
	return num

#Get Emotion         
def get_emotion( arousal, valence):
	rad = (180/math.pi)* (math.atan2(valence-5, arousal-5))
	strength= math.sqrt((valence-5)**2 + (arousal-5)**2)/math.sqrt(50)
    
	if strength==0:
		Power=""
	elif strength <=.10:
		Power= 'Very Weak'
	elif strength <=.25:
		Power= 'Weak'
	elif strength <=.75:
		Power ='Strong'
	elif strength <=1:
		Power= 'Very Strong'
	else:
		Power= 'Error'
    
	if valence==0.0 and arousal==0.0:
		rad=-450
	if rad < 0:
		rad=rad+360
    
	if (rad>=327.5 or (rad<22.5 and rad >=0)):
		return 'Happy, Pleased'+" ("+Power+")"
	elif (rad>=22.5 and rad<67.5):
		return 'Excited, Elated'+" ("+Power+")"
	elif (rad>=67.5 and rad<102.5):
		return 'Aroused, Hyperactivated'+" ("+Power+")"
	elif (rad>=102.5 and rad<147.5):
		return 'Tense, Nervous, Stressed'+" ("+Power+")"
	elif (rad>=147.5 and rad<192.5):
		return 'Miserable, Sad, Unhappy'+" ("+Power+")"
	elif (rad>=192.5 and rad<237.5):
		return 'Tired, Bored, Depressed'+" ("+Power+")"
	elif (rad>=237.5 and rad<282.5):
		return 'Quiet, Still, Sleepy'+" ("+Power+")"
	elif (rad>=282.5 and rad<327.5):
		return 'Calm, Relaxed'+" ("+Power+")"
	else:
		return 'No Emotion Detected'

def stringfunction(string):
    result=[]
    valence=[] 
    arousal=[]
    k=1
    line="" 
        
    for i in string:
        
        #break sentences into paragraphs
        if i not in (".","!","?"):
            line ="".join([line,i])
        else:
            k == k + 1
            
            #feed each sentence through the ANEW scorer 
            #First check to see that each line has at least 2 terms
            term_list = line.split()
            total = 0
            for j in term_list:
                if anew.exist(j) == True:
                    total = total + 1
            if total > 1:
                #At least 2 registering terms, score the line! 
                #return arousal with the highest valence!
                grFiveV = False
                grFiveA = False
                toBeat = 0
                key = anew.sentiment(term_list)
                #finds distance value is from 5, puts into lisis
                #retains +/- from center (5)
                if key['valence'] > 5:
                    grFiveV = True
                else:
                    grFiveV = False
                    
                if key['arousal'] > 5:
                    grFiveA = True
                else:
                    grFiveA = False
                
                #how far from 5
                valence.append(key['valence'])
                arousal.append(key['arousal'])
            line=""
            
    #takes max list value and puts into result list.
    #choose biggest valence away from 5
    goal = 0
    current1 = 0
    for l in valence:
        if abs(l-5) > goal:
            current1 = l
    #repeat for arousal
    goal = 0
    current2 = 0
    for n in arousal:
        if abs(n-5) > goal:
            current2 = n
            
    result.append(current1) #valence
    result.append(current2) #arousal

    return result


def containsAny(string, set):
	return 1 in [c.lower() in string.lower() for c in set]


def getNames(string, set):
	names = []
	for c in set:
		if (c.lower() in string.lower()):
			names.append(c.upper())			
	return names


def createLines(inTags):
	characterLines = {}
	mainCharacters=  ["VADER", " BEN ", "LUKE","THREEPIO", " HAN ", "LEIA", "TROOPER", "TARKIN"]
	for x in mainCharacters:
		characterLines[x]=[]

	#create a line as a separate for context and line - to be able to add it to different characters
	i=0
	for character in inTags:
		text = ""
		context = ""
		characterN=""
		characterNames = []

		characterLine = character.next_sibling.string.split('\n')
		for line in characterLine:
			if line.startswith("                         "):
				text = text + line.strip() +" "
			else:
				context = context+line.strip() +  " "
		
		#create line objects and add them to list of lines		
		textLine = Line(i, str(text),stringfunction(str(text))[0], stringfunction(str(text))[1])
		lines.append(textLine)
		i+=1
		if(context!=""):
			contextLine = Line(i, str(context), stringfunction(str(context))[0], stringfunction(str(context))[1])
			lines.append(contextLine)
		i+=1

		#find the character name whose line this is (strip the spaces for han and ben)
		for mainCharacter in mainCharacters:
			if mainCharacter.strip() in  character.getText():
				characterN = mainCharacter
				characterNames.append(mainCharacter)
		
		#add the characters to the list of names who have their name mentioned in the context
		#make sure that they are unique - we don't want to add multiple same lines to a single character
		if (containsAny(context, mainCharacters) ):
			characterNames.extend(getNames(context, mainCharacters))
			characterNames = Set(characterNames)
		
		#add lines to the dictionary of characters	
		#print characterNames
		for characterName in characterNames:
			contextSentences = ""
			if characterName.strip() in characterN :
				if text!="":
					characterLines[characterName].append(textLine)
			if context!="":
				sentences = str(context).split('.')
				for sentence in sentences:
					if (characterName.lower() in sentence.lower()):
						#print sentence + "\n"
						contextSentences += " "+ sentence
				#create a context line corresponding to the current index but with just a part of the text that consists the character name
				newContext= Line(contextLine.index, contextSentences, stringfunction(str(contextSentences))[0], stringfunction(str(contextSentences))[1])	
				characterLines[characterName].append(newContext)
	return characterLines

#*************************************************************
#MAIN PROGRAM
#*************************************************************

#add new words to anew dictionary to use for sentiment analysis
anew.add_term( 'aliance', 6.0, 8.0 )
anew.add_term( 'senate', 3.0, 6.0 )
anew.add_term( 'rebel', 6.0, 8.0 )
anew.add_term( 'force', 6.5, 8.0 )
anew.add_term( 'saber', 6.0, 8.0 )
anew.add_term( 'empire', 2.0, 6.0 )
anew.add_term( 'jedi', 7.0, 5.5 )
anew.add_term( 'republic', 6.0, 5.0 )
anew.add_term( 'rebellion', 6.0, 8.0 )
anew.add_term( 'alderaan', 3.0, 7.0 )
anew.add_term( 'kid', 7.0, 6.0 )

#list of main characters
mainCharacters=  ["VADER", " BEN ", "LUKE","THREEPIO", " HAN ", "LEIA", "TROOPER", "TARKIN"]

#dictionary of all characters and their lines
characters = {}
scenes = []

#list of all scenes
lines = []

soup = parseHtml("http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html")


#dictionary with keys that are the important character. Each character's value is the list of touples of text and context
#structure1 = {}

tags = soup.find_all('b')[4:]

#dictionary of all characters and their lines
characters = createLines(tags)


#import the scenes as a DataFrame
scenes1 = pandas.read_csv("C:/Users/Mirna/Desktop/Scene Breaks.csv")

#Add scene numbers to lines
i = 1
for j in range(len(lines)):
	if(scenes1.ix[i]["First Line"] in lines[j].text):
		scenes.append(Scene(scenes1.ix[i]["Title"], scenes1.ix[i]["Scene #"]-1))
		i+=1
	lines[j].setScene(i-1)

#update the character lines with scene numbers
for key in characters.keys():
	for line in characters[key]:
		line.setScene(lines[line.index].getScene())


#test - print scenes
for scene in scenes:
	print str(scene.index ) + ": " + scene.name

#test - print all lines for a character
for line in  characters["LUKE"]:
	print str(line.scene) + ": "+  line.text + "\n"


#test - print the total scene
for line in lines:
	if(line.scene == 0):
		print line.text



#Write to csv
columnnames = ["Scene", "Title", "Character", "Valence", "Arousal", "Emotion"]
out = open( 'starwars4.csv', 'wb')	
writer = csv.writer( out )
writer.writerow( columnnames )


#Get emotions by scenes for characters
scenesCharacters = {}

for i in range(len(scenes)):	
	for character in mainCharacters:
		row = [str(i+1), scenes[i].name]
		sceneCharacter = filter(lambda x: x.getScene() == i+1, characters[character])
		if len(sceneCharacter)>0:
			if character in scenesCharacters:
				scenesCharacters[character] = scenesCharacters[character]+1
			else:
				scenesCharacters[character]=1

		sceneText=""
		for line in sceneCharacter:
			sceneText += " " + line.getText()
		(scenes[i]).setCharacterText(sceneText, character)
		row.append(character)
		row.append(stringfunction(sceneText)[0])
		row.append(stringfunction(sceneText)[1])
		row.append(get_emotion(stringfunction(sceneText)[0], stringfunction(sceneText)[1]))
		writer.writerow(row)
out.close()


out = open ('CharacterScenes.csv', 'wb')
writer = csv.writer(out)
writer.writerow(["Character", "Scenes"])
for scene in scenesCharacters.keys():
	writer.writerow([scene, scenesCharacters[scene]])
out.close() 
