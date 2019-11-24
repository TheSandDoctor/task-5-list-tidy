import time
import datetime
import urllib
import json
import configparser #Bot password
import warnings
import re
import mwparserfromhell
import datetime
import mwclient
import sys
import CITconfig
from mwclient import errors

site = mwclient.Site(('https','en.wikipedia.org'), '/w/')#Tell Python to use the English Wikipedia's API

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

def remove_duplicates(l):
    return list(set(l))

def mysort(mylist):
    mylist=sorted(mylist) #Normal sort first
    #mylist=sorted(mylist, key=str.lower) #sorts using lowercase key
    return mylist

def customSort(x):
    pass

def myrun(search):
    print("search", search)
    pagetitle = search
    page = site.Pages[search]
    text = page.text()
    temp = []
    code = mwparserfromhell.parse(text)
    index = 0
    for sec in code.get_sections():
        index = 0
        final = []
        temp = []
        pagetext = ""
        for template in sec.filter_templates():
            if template.name.matches("JCW-exclude"):
                temp.append(str(template))
                index += 1
        if len(temp) == 0:
            index = 0
            final = []
            temp = []
            pagetext = ""
            continue
    #print(temp)
        final = mysort(temp)
        print(len(final))
        print(len(remove_duplicates(final)))
        print(final[-1])
        print(final[-2])
        pagetext = '\n'.join(final)
        x = 0
        #for sec in code.get_sections():
        for template in sec.filter_templates():
            if template.name.matches("JCW-exclude"):
                if template not in final:
                    print("Found duplicate", template)
                    code.remove(template)
                    continue
                code.replace(template, final[x])
                if x < index:# - 1:
                    x += 1
    with open("boutput.txt", 'w') as f:
        f.write(pagetext)
    with open("coutput.txt", 'w') as f:
        f.write(str(code))
   # page.save(str(code), summary="([[Wikipedia:Bots/Requests for approval/TheSandBot 5|Task 5]]) sorting lists ([[User:TheSandBot|disable]])", bot=True, minor=True)
    print("Done")
    
def Process(search):
    print("search", search)
    pagetitle = search
    pagetitletext = pagetitle.encode('utf-8')
    pnt(pagetitletext)
    pagepage = page.Page(site, pagetitle)
    print("pagepage")
    pagetext = pagepage.getWikiText()
    CITconfig.inputlist = list()
    CITconfig.outputlist = list()
    CITconfig.inputlist=pagetext.splitlines()
    size=len(CITconfig.inputlist)
    print("SIZE=", size)
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
            print("X IN", (x+1))
            z=getandsort(x+1) #x+1 is the line to start with
            print("X OUT", z)
            x=z-1
        x=x+1
    pagetext='' # clear ready assemble new page
    for line in CITconfig.outputlist:
        pagetext=pagetext+line+"\n"
    try:
        #raise ValueError("Not print")
        pagepage.edit(text=pagetext, bot=True, summary="([[Wikipedia:Bots/Requests for approval/TheSandBot 5|Task 5]]) sorting lists ([[User:TheSandBot|disable]])") #(DO NOT UNCOMMENT UNTIL BOT IS APPROVED)
        print(pagetext)
        print("writing changed page")
    except:
        print("Failed to write")
        print("Unexpected error:", sys.exc_info()[0])
        with open("output.txt", 'w') as f:
            f.write(pagetext)
    print("")
    return


def main():
    #parameters for API request
    search='User:JL-Bot/Citations.cfg'
    myrun(search)
    #search='User:RonBot/Questionable.cfg'
    #Process(search)
    #search='User:JL-Bot/Citations.cfg'
    #Process(search)

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        main()
