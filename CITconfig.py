inputlist=list()
outputlist=list()
partlist=list()
tagged=0
datedlist=list()
date=""
ignore=""


def wipe():
    """Resets CITconfig to all its default values."""
    try:
        inputlist *= 0
    except NameError:
        pass
    try:# is not None and len(outputlist) > 0:
        outputlist *= 0
    except NameError:
        pass
    try:# is not None and len(partlist) > 0:
        partlist *= 0
    except NameError:
        pass
    tagged = 0
    try:# is not None and len(datedlist) > 0:
        datedlist *= 0
    except NameError:
        pass
    date = ""
    ignore = ""
