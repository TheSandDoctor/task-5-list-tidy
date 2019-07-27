from wikitools import *
import time
import datetime
import urllib
import json
import configparser #Bot password
import warnings
import re
import mwparserfromhell
import datetime
import sys
import CITconfig
from mwclient import errors

site = wiki.Wiki() #Tell Python to use the English Wikipedia's API

config = configparser.RawConfigParser()
config.read('credentials.txt')
try:
    site.login(config.get('enwiki_sandbot','username'), config.get('enwiki_sandbot', 'password'))
except errors.LoginError as e:
    print(e)
    raise ValueError("Login failed.")
#site.login(userpassbot.username, userpassbot.password) #login

#routine to autoswitch some of the output - as filenames have accented chars!
def pnt(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode('utf-8'))

def startAllowed():
    h_page = page.Page(site, 'User:TheSandBot/status')
    text = h_page.getWikiText()
    return bool(json.loads(text)["run"]["ronbot10"])

def allow_bots(text, user):
    user = user.lower().strip()
    text = mwparserfromhell.parse(text)
    for tl in text.filter_templates():
        if tl.name.matches(['bots', 'nobots']):
            break
    else:
        return True
    print "template found" #Have we found one
    for param in tl.params:
        bots = [x.lower().strip() for x in param.value.split(",")]
	if param.name == 'allow':
            print "We have an ALLOW" # allow found
            if ''.join(bots) == 'none': return False
            for bot in bots:
                if bot in (user, 'all'):
                    return True
        elif param.name == 'deny':
            print "We have a DENY" # deny found
            if ''.join(bots) == 'none':
                print "none - true"
                return True
	    for bot in bots:
                if bot in (user, 'all'):
                    pnt(bot)
                    pnt(user)
                    print "all - false"
                    return False
    if (tl.name.matches('nobots') and len(tl.params) == 0):
        print "match - false"
        return False
    return True

def remove_duplicates(l):
    return list(set(l))

def mysort(mylist):
    mylist=sorted(mylist) #Normal sort first
    mylist=sorted(mylist, key=str.lower) #sorts using lowercase key
    return mylist

def reformat(line):
    #print">>",
    #pnt(line)
    line1=line
    sourcelist=list()
    notelist=list()
    wikilist=list()
    if "[[" in line:
        inwiki=False
        y=len(line)-1
        for x in range(0, y):
            check=line[x:x+2]
            if check=='[[':
                inwiki=True
            if check==']]':
                inwiki=False
            if inwiki:
                if line[x:x+1]=='|':
                    line=line[0:x]+"~~~~~~~"+line[x+1:]
    line=line[:-2] # remove the }}
    chop=line.split('|')
    choplist=list(chop)
    if choplist[0]=="{{JCW-selected":
        template=choplist[0]
        name=choplist[1]
        choplist.remove(template)
        choplist.remove(name)
        #pnt(choplist)
        for part in choplist:
            if re.match(r'^[Ss]ource\s*?=',part):
            #if "source" in part.lower():
                sourcelist.append(part)
            if re.match(r'^[Nn]ote\s*?=',part):
            #if "note" in part.lower():
                notelist.append(part)
        x=len(sourcelist)
        if x>0:
            for source in sourcelist:
                choplist.remove(source)
        y=len(notelist)
        if y>0:
            for note in notelist:
                choplist.remove(note)
        line=template+"|"+name
        z=len(choplist)
        if z>0:
            #print">>>>",
            #pnt(choplist)
            choplist=sorted(choplist)
            for part in choplist:
                linetest=line+"|"
                parttest="|"+part+"|"
                if parttest not in linetest:
                    line=line+"|"+part
        if x>0:
            added=False
            for part in sourcelist:
                if not added:
                    line=line+"|"+part
                    added =True
                else:
                    cutpart=re.sub(r'[Ss]ource=',', ',part)
                    cutpart2=re.sub(r'[Ss]ource=','',part)
                    if cutpart2 not in line:
                        line=line+cutpart
        if y>0:
            added=False
            for part in notelist:
                if not added:
                    line=line+"|"+part
                    added =True
                else:
                    cutpart=re.sub(r'[Nn]ote=',', ',part)
                    cutpart2=re.sub(r'[Nn]ource=','',part)
                    if cutpart2 not in line:
                        line=line+cutpart
        line=line+"}}"
        if line<>line1:
            print "##"
            pnt(line1)
            pnt(line)
            print "~~"
    else:
        print "Not JCW at atart"
        line=line+"}}"
    return line

def getandsort(x):
    print "getandsort"
    tuplist=list()
    cutlist=list()
    cutlist2=list()
    CITconfig.partlist=list()
    line = CITconfig.inputlist[x]
    while line<>"}}":
        if len(line)>2:
            line=reformat(line)
            CITconfig.partlist.append(line)
        x=x+1
        line = CITconfig.inputlist[x]
    CITconfig.partlist=sorted(CITconfig.partlist) # no more sorts, need to keep all in sync
    for line in CITconfig.partlist:
        chop=line.split('|')
        pnt(chop)
        tuplist.append(chop)
        cutlist.append(chop[0]+chop[1])
        cutlist2.append(chop[0]+chop[1])
    print len(CITconfig.partlist), len(cutlist), len(cutlist2)
    cutlist=remove_duplicates(cutlist)
    print len(CITconfig.partlist), len(cutlist), len(cutlist2)
    if len(cutlist)<>len(tuplist):
        print "Duplicates found in above list",len(cutlist),len(tuplist)
        for i in range(0,len(tuplist)-2):
            print i
            line1=cutlist2[i]
            line2=cutlist2[i+1]
            if line1==line2:
                print">>>>>>>>>>"
                pnt(line1)
                pnt(line2)
                pnt(tuplist[i])
                pnt(tuplist[i+1])
                pnt(CITconfig.partlist[i])
                pnt(CITconfig.partlist[i+1])
                print"<<<<<<<<<<"
                pnt(CITconfig.partlist[i])
                CITconfig.partlist[i]=merge(CITconfig.partlist[i], CITconfig.partlist[i+1])
                CITconfig.partlist[i+1]=CITconfig.partlist[i]
                print CITconfig.partlist[i]
                print"=========="
    print"++++++++++"
    print "before dup rem", len(CITconfig.partlist)
    CITconfig.partlist=remove_duplicates(CITconfig.partlist)
    print "after dup rem", len(CITconfig.partlist)
    #pnt(CITconfig.partlist)
    CITconfig.partlist=mysort(CITconfig.partlist)
    #pnt(CITconfig.partlist)
    #print CITconfig.inputlist[x] #should be "}}"
    for line in CITconfig.partlist: #transfer sorted section
        linefinal=re.sub("~~~~~~~","|",line)
        CITconfig.outputlist.append(linefinal)
    print"=========="
    return x

def merge (line1, line2):
    line1=line1[:-2] # remove the }}
    line1=line1+"|"+line2
    line1=reformat(line1)
    return line1

def Process(search):
    print "search", search
    pagetitle = search
    pagetitletext = pagetitle.encode('utf-8')
    pnt(pagetitletext)
    pagepage = page.Page(site, pagetitle)
    print "pagepage"
    pagetext = pagepage.getWikiText()
    CITconfig.inputlist = list()
    CITconfig.outputlist = list()
    CITconfig.inputlist=pagetext.splitlines()
    size=len(CITconfig.inputlist)
    print "SIZE=", size
    stop = allow_bots(pagetext, "TheSandBot")
    if not stop:
        return
    x=0
    while x<size:
        line=CITconfig.inputlist[x]
        #print x,
        #pnt(line)
        CITconfig.outputlist.append(line)
        if "columns-list" in line: # Start of a section
            print "X IN", (x+1)
            z=getandsort(x+1) #x+1 is the line to start with
            print "X OUT", z
            x=z-1
        x=x+1
    pagetext='' # clear ready assemble new page
    for line in CITconfig.outputlist:
        pagetext=pagetext+line+"\n"
    try:
        pagepage.edit(text=pagetext, bot=True, summary="([[Wikipedia:Bots/Requests for approval/TheSandBot 5|Task 5]]) sorting lists ([[User:TheSandBot|disable]])") #(DO NOT UNCOMMENT UNTIL BOT IS APPROVED)
        print pagetext
        print "writing changed page"
    except:
        print"Failed to write"
    print ""
    return


def main():
    go = startAllowed() #Check if task is enabled
    if go == False:
        sys.exit(1)
    #parameters for API request
    search='User:JL-Bot/Questionable.cfg'
    #search='User:RonBot/Questionable.cfg'
    Process(search)
    search='User:JL-Bot/Publishers.cfg'
    Process(search)

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        main()
