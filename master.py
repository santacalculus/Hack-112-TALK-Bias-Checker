import requests, bs4, urllib, re, copy, os, math, itertools, random, sys, string, copy, decimal
from cmu_112_graphics import *
from tkinter import *

masterDict = {'Far Left':{},'Left-of-centre':{},'Centre':{},'Centre Right':{},'Far Right':{}}

badWordsMasterList = {"illegal alien" : "undocumented immigrants", "illegal alien invasion" : "undocumented immigration", 
"illegal immigrant" : "undocumented immigrant", "witch hunt" : "criticism", "witch hunts" : "criticism", 
"illegals who" : "people who", "illegals" : "people", "his illegal status" : "his undocumented status", 
"her illegal status" : "her undocumented status", "their illegal status" : "undocumented status", "jihadi" : "radical muslim", 
"jihadis" : "radical muslims", '"transgender"' : 'transgender', "transvestite" : "transgender", '"transition"' : 'transition', 
"I knew a lot of Democrats were sexless drones but I never thought the number was this high." : "", 
"baby within the womb" : "fetus within the womb", "baby in the womb" : "fetus in the womb", "killing babies" : "pregnancy termination", 
"kill a baby" : "terminating a pregnancy", "climate alarmism" : "climate change activism", "mentally troubled" : "", 
"environmental alarmists" : "environmental activists", "hysterical" : "angry", "hysteria" : "anger", 
'fix illegal immigration' : 'reduce undocumented immigration','aghast' : 'displeased', 'up in arms' : 'displeased', 
'I’m not sure there’s any other way to put it.' : '', 'presumably' : 'possibly', 'rejects democracy' : 'disagrees with democracy', 
'rejected democracy' : 'disagreed with democracy', 'Let that sink in a minute.' : '', 
'Last time I checked my copy of the Constitution' : 'According to the Constitution', 'illegally entering' : 'undocumented entering', 
'legal workers' : 'documented workers'}

#####################################################
# readArticleCsvFile()
#####################################################

# Csv reading functions acquired from 
# http://www.kosbie.net/cmu/fall-18/15-110/notes/notes-2d-lists.html#csvFiles
# and modified slightly

# Reads a file from your computer file system
def readFile(path):
    # This makes a very modest attempt to deal with unicode if present
    with open(path, 'rt', encoding='ascii', errors='surrogateescape') as f:
        return f.read()


# Converts a csv file into a 2D list
def readCsvFile(path):
    # Returns a 2d list with the data in the given csv file
    result = [ ]
    for line in readFile(path).splitlines():
        result.append(line.split(','))
    return result


# Returns the 2D list of our article urls
def readArticleCsvFile():
    fileName = 'sampleArticleUrlCsv.csv'
    data = readCsvFile(fileName)
    print(f'Reading {fileName}...')
    return data

##########################################################################
# extractAndStripArticle()
##########################################################################

# Extracts html file from url and converts it into an article
def makeArticle(htmlFile):
    bigHeadersList = htmlFile.find_all('h1')
    bigHeadersText = [bigHeader.get_text() for bigHeader in bigHeadersList]
    smallHeadersList = htmlFile.find_all('h2')
    smallHeadersText = [smallHeader.get_text() for smallHeader in smallHeadersList]
    paragraphsList = htmlFile.find_all('p')
    paragraphsText = [paragraph.get_text() for paragraph in paragraphsList]
    divsList = htmlFile.find_all('div')
    divsText = []
    for div in divsList:
        if div.get('class') == ['zn-body__paragraph']:
            divsText.append(div.get_text())

    bigHeaders = ' '.join(bigHeadersText)
    smallHeaders = ' '.join(smallHeadersText)
    paragraphs = ' '.join(paragraphsText)
    specialText = ' '.join(divsText)

    article = bigHeaders + smallHeaders + paragraphs + specialText
    return article

# Removes simple stop words from the raw stripped article
def refineStrippedArticle(strippedArticle):
    stopWords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                "you", "your", "yours", "yourself", "yourselves", "he", "him", 
                "his", "himself", "she", "her", "hers", "herself", "it", "its", 
                "itself", "they", "them", "their", "theirs", "themselves", 
                "what", "which", "who", "whom", "this", "that", "these", 
                "those", "am", "is", "are", "was", "were", "be", "been", 
                "being", "have", "has", "had", "having", "do", "does", 
                "did", "doing", "a", "an", "the", "and", "but", "if", "or", 
                "because", "as", "until", "while", "of", "at", "by", "for", 
                "with", "about", "against", "between", "into", "through", 
                "during", "before", "after", "above", "below", "to", "from", 
                "up", "down", "in", "out", "on", "off", "over", "under", 
                "again", "further", "then", "once", "here", "there", "when", 
                "where", "why", "how", "all", "any", "both", "each", "few", 
                "more", "most", "other", "some", "such", "no", "nor", "not", 
                "only", "own", "same", "so", "than", "too", "very", "s", "t", 
                "can", "will", "just", "don", "should", "now", "the"]

    strippedArticleWordReferenceList = strippedArticle.split(' ')
    while '' in strippedArticleWordReferenceList:
        strippedArticleWordReferenceList.remove('') 
        # remove extra spaces in article
    strippedArticleWordDestroyList = copy.copy(strippedArticleWordReferenceList) 
    for word in strippedArticleWordReferenceList:
        if word in stopWords or word.isdigit() or word.isspace():
            strippedArticleWordDestroyList.remove(word)

    finalArticleProduct = ' '.join(strippedArticleWordDestroyList)
    return finalArticleProduct

# extractAndStripArticle but with weaker stripping
def extractAndWeakStripArticle(url):
    request = requests.get(url)
    soup = bs4.BeautifulSoup(request.text, 'html.parser')
    article = makeArticle(soup)
    finalArticleProduct = refineStrippedArticle(article)
    return finalArticleProduct

# Extracts news article and gives back raw words of article in a variable
def extractAndStripArticle(url):
    request = requests.get(url)
    soup = bs4.BeautifulSoup(request.text, 'html.parser')

    article = makeArticle(soup)
    # punctuation removal strategy with re.sub method acquired from
    # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-
    # from-a-string
    strippedArticle = re.sub(r'[^\w\s]','',article).lower() 
    # remove punctuation
    finalArticleProduct = refineStrippedArticle(strippedArticle)

    return finalArticleProduct

def justStrip(s):

    article = s
    # punctuation removal strategy with re.sub method acquired from
    # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-
    # from-a-string
    strippedArticle = re.sub(r'[^\w\s]','',article).lower() 
    # remove punctuation
    finalArticleProduct = refineStrippedArticle(strippedArticle)

    return finalArticleProduct

def importFiles():
  for colIndex in range(len(articleUrl2DList[0])):
      for rowIndex in range(len(articleUrl2DList)):
          category = articleUrl2DList[0][colIndex]
          if rowIndex == 0: # if at a category name...
            try:
              os.mkdir(f'./{category}/') 
              print(f'''
  Please note that a folder named {category} has been added to the same folder
  as this python file for the sake of program efficiency and avoiding extra web
  scraping. Delete it if you like.
  ''')
            except:
              print(f'Folder ./{category}/ already exists!')
            # ...make folder with the category name
          else: # add text files to appropriate folder
            url = articleUrl2DList[rowIndex][colIndex]
            if url != '':
              strippedArticleContents = extractAndStripArticle(url)
              addFrequencies(masterDict,category,generateFrequencies(strippedArticleContents))
              firstTwentyChrs = strippedArticleContents[:20]
              newArticleFile = open(f'{category}/{firstTwentyChrs}.txt', 'w')
              newArticleFile.write(strippedArticleContents)
              newArticleFile.close()

def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    counter = [len(args) - 1]
    def sentinel():
        if not counter[0]:
            raise TypeError()
        counter[0] -= 1
        yield fillvalue
    fillers = itertools.repeat(fillvalue)
    iterators = [itertools.chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except:
        pass

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

Analysis = 'Analysis...' # Text that is being analyzed
Core = 'Core...' # non-stripped
catagoryFrequencies = {'Far Left':{},'Center Left':{},'Center':{},'Center Right':{},'Far Right':{}}

def generateFrequencies(s):
    out = {}
    l = len(s.split())
    for i in s.split():
        out[i] = out.get(i,0) + 1
    for i in out:
        out[i] =  math.log(out[i] / l)
    return out

def addFrequencies(d,c,n):
    for i in n:
        d[c][i] = d[c].get(i,0) + n[i]

def formatFrequencies(d):
    out = {}
    s = sum(d.values())+1
    for k in d:
        out[k] = math.log(d[k]/s)
    return out

def matchCatagories(s,d):
    catagories = [[k,0] for k in d]
    s = generateFrequencies(s)
    biasedWords = []
    for j in s:
        for k in range(len(d)):
            if s[j] != 0:
                catagories[k][1] -= abs(s[j]-d[catagories[k][0]].get(j,0))
    print(sorted(catagories,key=lambda x:x[1]))
    return sorted(catagories,key=lambda x:x[1])[-1][0]

def matchCatagoriesWithScoring(stringCheck,d):
    catagories = {k:0 for k in d}
    s = generateFrequencies(stringCheck)
    biasedWords = []
    for j in s:
        bestCatagory = 'Centre'
        bestScore = -19
        for k in d:
            currentScore = -abs(s[j]-d[k].get(j,-30))
            if currentScore > bestScore:
                bestScore = currentScore
                bestCatagory = k
        catagories[bestCatagory] += 1
    bestCatagory = 'Centre'
    bestScore = catagories['Centre']
    for i in catagories:
        if catagories[i] > bestScore:
            bestScore = catagories[i]
            bestCatagory = i
    return bestCatagory

def purgeBiasedWords(s,d):
    temp = s.lower()
    for badWord in d:
        if badWord in temp:
            temp = temp.replace(badWord.lower(),f'{badWord} ({d[badWord]})')
    return temp

d1 = generateFrequencies('President Donald Trump is a racist corrupt puppet of Putin who made a corrupt call to the President of Ukraine')
d2 = generateFrequencies('Polling indicates a result that is favorable towards Democrats but does not discount Republicans')
d3 = generateFrequencies('the President deployed the national guard to combat the forest fires in California this weekend')
d4 = generateFrequencies('Democrats are blowing their chances to defeat Trump in 2020 by running socialist candidadtes')
d5 = generateFrequencies('Hillary Clinton sold our Uranium to Putin and is currently running the deep state conspiracy against President Trump')
c = {'Far Left':d1,'Center Left':d2,'Center':d3,'Center Right':d4,'Far Right':d5}

def testML():
    s1 = 'Donald Trump is at it again with his racial rhetoric and endless corrupt behavior not to mentio involvment with Russia and Ukraine'
    s2 = 'Democrats are favored to take the House of Representatives, but Republicans are favored to hold the Senate'
    s3 = 'over the weekend Trump sent the national guard to California to put out the fires'
    s4 = 'Democrats chances are in 2020 are dependent on their candidates not being percieved as socialist or out of touch'
    s5 = 'There was no collusion, only a conspiracy against our rightfully elected president by Hillary Clinton supporting socialists'
    for i in [s1,s2,s3,s4,s5]:
        print(matchCatagoriesWithScoring(i,c),i[:50])
    print()
    addFrequencies(c,'Far Left',generateFrequencies('Hillary Clinton is the rightfully elected president President Trump stands against our state'))
    for i in [s1,s2,s3,s4,s5]:
        print(matchCatagoriesWithScoring(i,c),i[:50])
    sf = purgeBiasedWords('illegal aliens and fanatical muslims are overunning sanctuary cities',{'illegal aliens':'undocumented immigrants','fanatical':'devout','sanctuary cities':'places of refuge'})
    print(sf)

class isometric():
    def __init__(self,x,y,w,f):
        r,g,b = random.randint(100,255), random.randint(100,255), random.randint(100,255)
        self.c1 = '#' + hex(r)[2:] + hex(g)[2:] + hex(b)[2:]
        self.c2 = '#' + hex(r//2)[2:] + hex(g//2)[2:] + hex(b//2)[2:]
        self.c3 = '#' + hex(r//3)[2:] + hex(g//3)[2:] + hex(b//3)[2:]
        self.w = w
        self.f = f
        self.x0, self.y0 = x, y + 50
        self.x1, self.y1 = x + self.w/2, y + self.w/4 + 50
        self.x2, self.y2 = x + self.w, y + 50
        self.defineHeights(0)

    def defineHeights(self,timer):
        self.h = self.f(self.x0/self.w,self.y0/self.w,timer)
        self.x3, self.y3 = self.x0, self.y0 - self.h
        self.x4, self.y4 = self.x0 + self.w/2, self.y0 - self.h + self.w/4
        self.x5, self.y5 = self.x0 + self.w, self.y0 - self.h
        self.x6, self.y6 = self.x0 + self.w/2, self.y0 - self.h - self.w/4

    def drawIsometric(self,canvas):
        canvas.create_polygon(self.x0,self.y0,self.x1,self.y1,self.x4,self.y4,self.x3,self.y3,fill=self.c2)
        canvas.create_polygon(self.x3,self.y3,self.x4,self.y4,self.x5,self.y5,self.x6,self.y6,fill=self.c1)
        canvas.create_polygon(self.x4,self.y4,self.x5,self.y5,self.x2,self.y2,self.x1,self.y1,fill=self.c3)

def chunkifyString(s,l):
    g = grouper(s,l)
    m = list(map(lambda x: ''.join((filter(lambda y: type(y)==str,x))),g))
    print('\n'.join(m))
    return '\n'.join(m)

class SplashMode(Mode):

    def modeActivated(self):
        self.app._canvas.pack_forget()
        self.canvas = Canvas(self.app._root,width=400,height=400)
        self.cwidth = 400
        self.cheight = 400
        self.canvas.pack()
        self.isometrics = self.generateIsometrics(self.cwidth,self.cheight,20,18)
        self.tick = 0
        self.timerDelay = 50
        self.textInput = Entry()
        self.textInput.pack()
        self.b1 = Button(text='Analyze Text',command=self.displayEntry)
        self.b1.pack()
        self.b2 = Button(text='Analyze URL',command=self.getURL)
        self.b2.pack()

    def modeDeactivated(self):
        self.canvas.pack_forget()
        self.textInput.pack_forget()
        self.b1.pack_forget()
        self.b2.pack_forget()
        self.app._canvas.pack()

    def displayEntry(self):
        global Analysis
        global Core
        Core = self.textInput.get()
        Analysis = justStrip(Core)
        self.app.setActiveMode(self.app.AnalysisMode)

    def getURL(self):
        global Analysis
        global Core
        try:
            'https://medium.com/@nikhilbd/how-to-use-machine-learning-to-find-synonyms-6380c0c6106b'
            Core = extractAndWeakStripArticle(self.textInput.get())
            Analysis = extractAndStripArticle(self.textInput.get())
            self.app.setActiveMode(self.app.AnalysisMode)
        except:
            raise TypeError('Type in a VALID URL (noob)')

    def generateIsometrics(self,w,h,n,s):
        out = []
        for i in range(1,2*n):
            row = n-abs(i-n)
            y0 = h/2 + ((s/2 * (i - n)))/2
            xmid = (row + 1) / 2
            for j in range(row):
                x0 = w/2 + s * (j - xmid)
                out.append(isometric(x0,y0,s,lambda x,y,t: (200/(abs(y)**0.5))*abs(math.sin(1.1*(-y+t)))))
        return out

    def timerFired(self):
        self.tick += 0.1
        for i in self.isometrics:
            i.defineHeights(self.tick)

    def redrawAll(self,canvas):
        self.canvas.delete(ALL)
        self.canvas.create_text(self.cwidth/2,self.cheight-10,text='''
                        Welcome to the TALK bias checker!
        Paste a piece of long text into the field below and we will
        identify how biased it is, and make some suggestions:''')
        for i in self.isometrics:
            i.drawIsometric(self.canvas)

class AnalysisMode(Mode):
    def modeActivated(self):
        if not self.app.importedFiles:
            importFiles()
            self.app.importedFiles = True
        self.app._canvas.pack_forget()
        self.canvas = Canvas(self.app._root,width=800,height=600)
        self.vbar = Scrollbar(self.canvas,orient=VERTICAL)
        self.vbar.pack(side=RIGHT,fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=800,height=600)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT,expand=True,fill=BOTH)
        self.canvas.pack()
        self.width = 800
        self.height = 600
        self.b3 = Button(text='Go Back',command=self.Reset)
        self.b3.pack(side=BOTTOM,expand=True,fill=BOTH)
        print(matchCatagoriesWithScoring(Analysis,masterDict))

    def Reset(self):
        self.app.setActiveMode(self.app.splashMode)

    def modeDeactivated(self):
        self.canvas.pack_forget()
        self.vbar.pack_forget()
        self.b3.pack_forget()
        self.app._canvas.pack()

    def redrawAll(self,canvas):
        self.canvas.delete(ALL)
        self.canvas.create_text(self.width/2,0,text=matchCatagoriesWithScoring(Analysis,masterDict)+'\n\n\n'+chunkifyString(purgeBiasedWords(Core,badWordsMasterList),80),anchor='n')

class MainApp(ModalApp):
    def appStarted(self):
        self.importedFiles = False
        self.splashMode = SplashMode()
        self.AnalysisMode = AnalysisMode()
        self.setActiveMode(self.splashMode)

articleUrl2DList = readArticleCsvFile()
MainApp(width=800,height=600)

#testML()