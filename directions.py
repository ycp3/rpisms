import json
import requests
import re

# google maps api key
api_key = "API_KEY_HERE"

baseurl = "https://maps.googleapis.com/maps/api/directions/json?"

p = re.compile(r"(directions)\s(from\s)?(.+?)\sto\s(.+?)\sby\s(.+)",
        re.IGNORECASE)

htmlreg = re.compile(r"<.+?>")

modesdict = {   "car"   : "driving",
                "foot"  : "walking",
                "bike"  : "bicycling",
                "train" : "transit",
                "bus"   : "transit", 
                "walk"  : "walking",
                "drive" : "driving" }

def validate(txtstr):
    if p.search(txtstr) != None:
        return True
    return False

def formatinput(txtstr):
    mo = p.search(txtstr)
    return mo.group(3), mo.group(4), mo.group(5)

def makeurl(start, end, mode):
    start = "+".join(start.split())
    end = "+".join(end.split())
    return (baseurl +
            "origin=" + start +
            "&destination=" + end +
            "&mode=" + mode +
            "&key=" + api_key)


def get_directions(txtstr):
    start, end, mode = formatinput(txtstr)
    if (mode != "driving" or mode != "walking"
        or mode != "transit" or mode != "bicycling"):
        if mode in modesdict:
            mode = modesdict[mode]
        else:
            return "Invalid mode of transporation"
    url = makeurl(start, end, mode)
    try:
        resp = requests.get(url)
        dirjson = resp.json()
    except:
        return "Error"
    
    if dirjson['status'] != "OK":
        return dirjson['status']
    
    distance = dirjson['routes'][0]['legs'][0]['distance']['text']
    duration = dirjson['routes'][0]['legs'][0]['duration']['text']
    start = dirjson['routes'][0]['legs'][0]['start_address']
    end = dirjson['routes'][0]['legs'][0]['end_address']
    steps = dirjson['routes'][0]['legs'][0]['steps']

    output = f"\n{start}\nto\n{end}\n{distance}, {duration}\n\nSteps:\n"

    for step in steps:
        stepdist = step['distance']['text']
        stepdur = step['duration']['text']
        instr = step['html_instructions']

        instmo = htmlreg.findall(instr)

        if instmo != []:
            for w in instmo:
                instr = instr.replace(w, "")

        output += f"\n{stepdist}, {stepdur}\n{instr}\n"

    output += "\nEND"

    return output