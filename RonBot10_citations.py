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


site = wiki.Wiki() #Tell Python to use the English Wikipedia's API
config = configparser.RawConfigParser()
config.read('credentials.txt')
site.login(config.get('enwiki_sandbot','username'), config.get('enwiki_sandbot', 'password')) #login

#routine to autoswitch some of the output - as filenames have accented chars!
def pnt(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode('utf-8'))

def startAllowed():
    """Checks to ensure that the bot's control panel bool is enabled/true"""
    h_page = page.Page(site, 'User:TheSandBot/status')
    text = h_page.getWikiText()
    return bool(json.loads(text)["run"]["ronbot10"])

def allow_bots(text, user):
    """Checks if the bot (user) is allowed to edit the given page based on its content (text)"""
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

def firsttimestamp(pagename):
    params = {'action':'query',
        'titles':pagename,
        'prop':'revisions',
        'rvprop':'timestamp',
        'rvlimit':'1',
        'rvdir':'newer'
        }
    req = api.APIRequest(site, params) #Set the API request
    res = req.query(False) #Send the API request and store the result in res
    #{
    #"continue": {
    #    "rvcontinue": "20101117204903|397372371",
    #    "continue": "||"
    #},
    #"query": {
    #    "pages": {
    #        "29641123": {
    #            "pageid": 29641123,
    #            "ns": 0,
    #            "title": "Journal of Internal Medicine",
    #            "revisions": [
    #                {
    #                    "timestamp": "2010-11-17T20:38:57Z"
    #                }
    #            ]
    #        }
    #    }
    #}
    #}
    #pnt(res)
    pageid = res['query']['pages'].keys()[0]
    #print pageid
    timestamp="X"
    if int(pageid)>0:
        timestamp=str(res['query']['pages'][pageid]['revisions'][0]['timestamp'])
        print timestamp
        #m = re.search(r'(.*?)T', timestamp)
        #datebit = m.group(1)
        #print datebit
    return timestamp

def checkitem(line1):
    line=line1[:-2] # remove the }}
    chop=line.split('|')
    choplist=list(chop)
    if choplist[0]=="{{JCW-exclude":
        if len(choplist)>2:
            if line not in CITconfig.ignore:
                testpage=choplist[2]
                createdate=firsttimestamp(testpage)
                #print line, createdate
                #2010-11-17T20:38:57Z
                if createdate<>"X":
                    timestamp1 = datetime.datetime.strptime(createdate, '%Y-%m-%dT%H:%M:%SZ')
                    timestamp2 = datetime.datetime.strptime(CITconfig.date, '%Y-%m-%dT%H:%M:%SZ')
                    print
                    if timestamp1 < timestamp2:
                        print '1 < 2'
                        CITconfig.datedlist.append(line1)

    return

def getJCWdate():
    pagepage = page.Page(site, 'Template:JCW-date')
    print "pagepage"
    pagetext = pagepage.getWikiText()
    chop=pagetext.split('<')
    choplist=list(chop)
    CITconfig.date=choplist[0]+"T00:00:00Z"
    print CITconfig.date
    return

def getandsort(x):
    print "getandsort"
    CITconfig.partlist=list()
    line = CITconfig.inputlist[x]
    while line<>"}}":
        if len(line)>2:
            CITconfig.partlist.append(line)
            checkitem(line)
        x=x+1
        line = CITconfig.inputlist[x]
    print "before dup rem", len(CITconfig.partlist)
    CITconfig.partlist=remove_duplicates(CITconfig.partlist)
    print "after dup rem", len(CITconfig.partlist)
    #pnt(CITconfig.partlist)
    CITconfig.partlist=sorted(CITconfig.partlist) #Normal sort first
    CITconfig.partlist=sorted(CITconfig.partlist, key=str.lower) #sorts using lowercase key
    pnt(CITconfig.partlist)
    #print CITconfig.inputlist[x] #should be "}}"
    for line in CITconfig.partlist: #transfer sorted section
        CITconfig.outputlist.append(line)
    return x

def writepage(title,mylist):
    pagetitle=title
    pagepage = page.Page(site, pagetitle)
    pagetext=""
    for line in mylist:
        pagetext=pagetext+line+"\n"
    print "witing page"
    pagepage.edit(text=pagetext, bot=True, skipmd5=True, summary="update page")

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
    stop = allow_bots(pagetext, "RonBot")
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
        #pagepage.edit(text=pagetext, bot=True, summary="(Task 10) sorting lists ([[User:RonBot|disable]])") #(DO NOT UNCOMMENT UNTIL BOT IS APPROVED)
        print pagetext
        print "writing changed page"
    except:
        print"Failed to write"
    print ""
    return

def getwritepage(search):
    pagetitle = search
    pagetitletext = pagetitle.encode('utf-8')
    pnt(pagetitletext)
    pagepage = page.Page(site, pagetitle)
    print "pagepage WP"
    pagetext = pagepage.getWikiText()
    CITconfig.datedlist=list()
    tplist=list()
    CITconfig.ignore=""
    ignoreflag=False
    tplist=pagetext.splitlines()
    for line in tplist:
        if "Report ignore" in line:
            ignoreflag=True
        if "-->" in line:
            ignoreflag=False
        if "Report begin" in line:
            break
        CITconfig.datedlist.append(line)
        if ignoreflag==True:
            if "{{" in line:
                CITconfig.ignore=CITconfig.ignore+line
    print""
    pnt(tplist)
    print""
    pnt(CITconfig.datedlist)
    print""
    pnt(CITconfig.ignore)
    print"end of start"
    return


def run(title):
    go = startAllowed() #Check if task is enabled
    if go == False:
        sys.exit(1)
    getJCWdate()
    getwritepage(title)
    CITconfig.datedlist.append("<!-- Report begin-->")
    CITconfig.datedlist.append("The following exclusions are likely no longer needed:")


    #parameters for API request
    Process(title)

    CITconfig.datedlist.append("<!-- Report end-->")
    writepage(title,CITconfig.datedlist)
    CITconfig.wipe()

def main():
    run('User:JL-Bot/Citations.cfg')
    run('User talk:JL-Bot/Citations.cfg')
    #go = startAllowed() #Check if task is enabled
    #if go == False:
    #    sys.exit(1)
    #getJCWdate()
    #getwritepage('User:JL-Bot/Citations.cfg')
    #CITconfig.datedlist.append("<!-- Report begin-->")
    #CITconfig.datedlist.append("The following exclusions are likely no longer needed:")


    #parameters for API request
    #search='User:JL-Bot/Citations.cfg'
    #Process(search)

    #CITconfig.datedlist.append("<!-- Report end-->")
    #writepage('User:JL-Bot/Citations.cfg',CITconfig.datedlist)

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        try:
            main()
        except KeyboardInterrupt:
            CITconfig.wipe()
            print("\nCancelled with Ctrl + C")
