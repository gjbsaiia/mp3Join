import string
from pydub import AudioSegment
import glob
import argparse
import sys
import os
import re 

class JoinMp3Options():
    def __init__(self):
        self.pathToFiles = ""
        self.filterBy = None
        self.timeCapPerFile = 0
        self.fileTitle = ""
        self.output = ""
        self.dirChar = ""
    def isDir(self, path):
        if(os.path.isdir(path)):
            return True
        return False
    def trySetDirChar(self):
        self.dirChar = "\\"
        if("/" in self.pathToFiles):
            self.dirChar = "/"
    def getAllMp3Files(self):
        if (not self.dirChar):
            self.trySetDirChar()
        if(not self.pathToFiles.endswith(self.dirChar)):
            self.pathToFiles += self.dirChar
        if(not self.output.endswith(self.dirChar) and self.output not in [None, "", " "]):
            self.output += self.dirChar
        mp3s = glob.glob(self.pathToFiles + "*.mp3")
        return smartSort(mp3s)

def main(args: argparse.Namespace):
    if(args.config and os.path.isfile(args.config)):
        options = getOptionsFromFile(args.config)
    else:
        options = getOptionsFromUser()
    if(not options.isDir(options.pathToFiles)):
        print("directory does not exist: "+options.pathToFiles)
        return
    if(not options.isDir(options.output)):
        options.output = ""
    runJoin(options)
    print()
    print("join complete.")

def runJoin(options: JoinMp3Options):
    mp3Files = options.getAllMp3Files()
    part = 1
    fileTitle = options.fileTitle.replace(".mp3", "")
    print("attempting to join "+str(len(mp3Files))+" .mp3 files:")
    joined = None
    current = ""
    for file in mp3Files:
        mp3 = AudioSegment.from_mp3(file)
        if(not joined):
            current = fileTitle+".mp3" if part < 2 else fileTitle + "[" + str(part) + "].mp3"
            print()
            print("starting new file, "+current+":\r\n    with "+file.split(options.dirChar)[-1]+"...")
            joined = mp3
        else:
            print(" ...joining "+current+"\r\n    with "+file.split(options.dirChar)[-1]+"...")
            joined = joined + mp3
        if(options.timeCapPerFile != 0 and len(mp3) >= options.timeCapPerFile):
            print("***  writing " + options.output + current + "...")
            joined.export(options.output + current, format="mp3")
            joined = None
            part += 1
    if(joined):
        print("***  writing " + current + "...")
        joined.export(options.output + current, format="mp3")
        joined = None

def getOptionsFromFile(path: string) -> JoinMp3Options:
    optionSet = JoinMp3Options()
    args = []
    with open(path, 'r', encoding=sys.getfilesystemencoding()) as argFile:
        args = argFile.readlines()
    options = { 'pathToFiles': None, 'filterBy': None, 'timeCapPerFile': None, 'fileTitle': None, 'output': None}
    satisfied = []
    for line in args:
        line = line.replace(" ", "")
        notSatisfied = options.keys()
        for option in notSatisfied:
            i = line.find(option)
            if(i >= 0):
                i += len(option)+1
                end_i = int(line.find(",", i))
                arg = line[i : end_i] if end_i > 0 else line[i:]
                options[option] = arg
                satisfied.append(option)
    if(options["pathToFiles"]):
        optionSet.pathToFiles = options["pathToFiles"]
    if(options["filterBy"]):
        optionSet.filterBy = options["filterBy"]
    if(options["fileTitle"]):
        optionSet.fileTitle = options["fileTitle"] if options["fileTitle"] not in [None, "", " "] else "file"
    if(options["output"]):
        optionSet.output = options["output"]
    if(options["timeCapPerFile"]):
        try:
            optionSet.timeCapPerFile = int(options["timeCapPerFile"])
            optionSet.timeCapPerFile *= 60000
        except ValueError:
            optionSet.timeCapPerFile = 0
    return optionSet

def getOptionsFromUser() -> JoinMp3Options:
    options = JoinMp3Options()
    options.pathToFiles = input("input directory: ")
    options.output = input("output directory: ") 
    all = input("merge all? (y/n) ").lower() == "y"
    if(all):
        options.filterBy = None
    else:
        options.filterBy = input("filter by? (no regex yet) ")
    try:
        options.timeCapPerFile = int(input("time limit per file? (in min): "))
        options.timeCapPerFile *= 60000
    except ValueError:
        options.timeCapPerFile = 0
    options.fileTitle = input("new name for file(s)? ")
    return options

def smartSort(l): 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

# Execute the wrapper
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print()
        print('Interrupted \_[o_0]_/')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


