"""
 *  @@@@@@@@@@@@@@   TheYoungWolf Productions   @@@@@@@@@@@@@@
 *
 *  Copyright (C) 2020 File System Simulation
 *
 * Licensed under the Apache License, Version 1.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License from the author
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
"""
import os
import sys
import math
import llist
from llist import dllist, dllistnode  # Using Double Linked List Library


# ******************* Global Variables ********************

gl_inputfile = ""
gl_inputdir = ""
gl_disksize = 0
gl_blocksize = 0
gl_totalblock = 0
gl_filecount = 0
gl_dircount = 0
gl_fragmentation = 0
gl_freespace = 0


# ******************** All definitons **********************


# Node definition of Disk Linked List
class nodeDiskLL:
    def __init__(self):
        self.status = "FREE"
        self.begin = 0
        self.end = 0
        self.next = None


Disk = nodeDiskLL()

# Node definition of File Linked List


class nodeFileLL:
    def __init__(self):
        self.pma = 0  # offset aka physical memory address
        self.next = None  # Pointer to next node


# Node definition of File node in tree
class nodeFile:
    def __init__(self):
        self.filename = ""
        self.fullname = ""
        self.path = ""
        self.fileSize = 0
        # self.time = 0
        self.fileNode = None


# Node definition of Directory node in tree
class nodeDir:
    def __init__(self):
        self.parentDir = None
        self.fullname = ""
        self.name = ""
        self.path = ""
        self.dirDLList = None
        self.fileDLList = None


# Creating a root node
# root = nodeDir()
root = None


# ************* Main program helper functions ***************
# dir(t_dir *);
# chdir(t_dir *, char *); #CAN IGNORE THIS FOR NOW
# printout(t_dir *);
# mkdir(t_dir *, char *); #IMPORTANT
# rmdir(t_dir *, char *); #IMPORTANT
# mkfile(t_dir *, char *); #IMPORTANT
# rmfile(t_dir *, char *); #IMPORTANT
# remove(t_dir *, char *, int); #IMPORTANT
# append(t_dir *, char *, int); #IMPORTANT


# Prints out the items in a directory
def dirORls(node):
    for i in range(node.dirDLList.size):
        print(node.dirDLList[i].name)
    for j in range(node.fileDLList.size):
        print(node.fileDLList[j].filename)


# Print meta info
def printout(node):
    l = node.fileDLList
    for each in range(len(l)):
        currentChild = l[each]
        print("----------------------------------------------------------------")
        print("1. File name: " + currentChild.filename)
        print("2. Full name: " + currentChild.fullname)
        print("3. File path: " + currentChild.path+"/")
        print("4. File size: " + str(currentChild.fileSize)+" bytes")
        printFileLL(currentChild.fileNode, currentChild.fileSize)
        print("----------------------------------------------------------------")


# Change directory
def chdir(dir, name):
    l = dir.dirDLList
    if(l.first != None):
        for i in range(len(l)):
            currentChild = l[i]
            if(currentChild.name in name):
                return currentChild
        return None
    return None


# Creates a new directory if it doesn't exist.
def mkdir(node, name):
    global gl_dircount
    new = nodeDir()
    # Concat final full name of directory
    fullname = node.fullname + name
    # Creates a new directory if and only if it doesnt already exist
    if (node.fullname != fullname):
        new = initDir(node, fullname)
        node.dirDLList.append(new)
        gl_dircount += 1
    file = open(gl_inputdir, "a")
    file.write(fullname+"\n")
    file.close()


# Removes a directory
def rmdir(node, name):
    i = 0
    # if there is no directory to remove
    if node.dirDLList == None:
        return
    # Child directories
    dirList = node.dirDLList
    # Traverse over child directories to find directory to delete.
    for i in range(node.dirDLList.size):
        cd = dirList[i]
        if cd.name == name:
            # Inorder to remove a directory, it cannot have subdirectories
            if (cd.dirDLList.first != None):
                print("Failed to remove directory because it has subdirectories!")
                return
            else:
                dirList.remove(dirList.nodeat(i))
                # Update the dir_list.txt file
                fullname = cd.fullname
                file = open(gl_inputdir, "r")
                lines = file.readlines()
                file.close()
                file2 = open(gl_inputdir, "w")
                for line in lines:
                    if line.strip("\n") != fullname:
                        file2.write(line)
                file2.close()
                return


# Creates a file
def mkfile(node, name, size):
    global gl_filecount
    if(size > gl_freespace):
        print("No more freespace")
        return
    fullname = ""
    f = nodeFile()
    f.fileSize = size
    # Concat into final fullname
    fullname += node.fullname
    fullname += name
    # Assign to node variables.
    f.fullname = fullname
    f.filename = name
    f.path = node.path
    # Create a linked list for this file
    f.fileNode = createFileLL(f.fileSize)
    # The parent node should have this file in its files DLL
    node.fileDLList.append(f)
    gl_filecount += 1
    # Write new file to file_list.txt
    file = open(gl_inputfile, "a")
    file.write(str(size)+" "+fullname+"\n")
    file.close()


# Removes a file
def rmfile(node, name):
    global gl_freespace, gl_fragmentation
    # First check whether this node(dir) has any files in it
    # If not, return
    if(node.fileDLList == None):
        return
    # We traverse the list and find the file node to be deleted from DLL.
    for i in range(node.fileDLList.size):
        currentChild = node.fileDLList[i]
        # Once found, free up disk space, reduce fragmentation
        # Free up that files own Linked List
        # Lastly remove the file from the node(dir) DLL of all files
        if(currentChild.filename == name):
            fullname = currentChild.fullname
            gl_freespace += currentChild.fileSize
            gl_fragmentation -= countFragmentation(currentChild.fileSize)
            freeFileLL(currentChild.fileNode)
            node.fileDLList.remove(node.fileDLList.nodeat(i))
            # Update the file_list.txt file.
            file = open(gl_inputfile, "r")
            lines = file.readlines()
            file.close()
            file2 = open(gl_inputfile, "w")
            for line in lines:
                each = line.split()
                if each[1].strip("\n") != fullname:
                    file2.write(line)
            file2.close()
            return


# Remove file data aka reduce file size
def remove(node, name, size):
    global gl_blocksize
    temp = None
    # No files in the directory
    if node.fileDLList.first == None:
        return
    if size <= 0:
        return
    # Access nodes Files DLL
    filelist = node.fileDLLlist
    # Iterate over every file
    for i in range(node.fileDLList.size):
        cf = filelist[i]
        if cf.filename == name:
            onFileAdd(0)
            cf.fileSize = cf.fileSize - size
            filesize = cf.fileSize
            onFileRemove(filesize)
            if (filesize <= 0):
                freeFileLL(cf.fileNode)
                cf.fileNode = None
                cf.fileSize = 0
                return
            if filesize < gl_blocksize:
                return
            while filesize > gl_blocksize:
                filesize -= gl_blocksize
                if(temp == None):
                    temp = cf.fileNode
                temp = temp.next
            freeFileLL(temp.next)
            temp.next = None
            return


# Add file data aka increase file size
def append(root, name, size):
    global gl_blocksize
    # No files in the directory
    if root.fileDLList.first == None:
        return
    if size <= 0:
        return
    # Access nodes files DLL
    filelist = root.fileDLList
    # Iterate over every file
    for i in range(root.fileDLList.size):
        cf = filelist[i]
        if cf.filename == name:
            onFileRemove(cf.fileSize)
            cf.fileSize = cf.fileSize + size
            new = cf.fileSize
            onFileAdd(new)
            if cf.fileNode == None:
                cf.fileNode = createFileLL(new)
                return
            while new > gl_blocksize:
                new -= gl_blocksize
                if cf.fileNode.next == None:
                    cf.fileNode = cf.fileNode.next
                else:
                    cf.fileNode.next = createFileLL(new)
            return


# ********************** Input checks **********************
# std_input_check(int, char **);
# std_input_error(int);
# std_param_check(char *, int);
# std_input_files();
# read_file(char *);


# Check if there are 4 args. If yes, then checks their correctness
# If not, it displays the relavent error
def inputCheck(argc, argv):
    r = 1
    if(argc < 4):
        if(argv[1] != "?" or argv[1] != "help"):
            r = inputError(0)
        else:
            r = inputError(4-argc)
    elif(argc > 4):
        r = inputError(argc)
    else:
        for i in range(1, 4):
            r = paramCheck(argv[i], i)
            if(r != 1):
                return r
    return r


# Used to display various messages depending upon user entry
def inputError(arg):
    if(arg == 0):
        print("Please read the README.txt")
    elif(arg < 4):
        print("Some parameters missing\nSeek help using command ./FileSystem ? or ./FileSystem help")
    else:
        print("Too many arguments passed\nSeek help using command ./FileSystem ? or ./FileSystem help")
    return 0


# Check Parameters
def paramCheck(str, i):
    r = 1
    size = 0
    # Ignore the zeroth parameter
    # CASE 1: Validating the first parameter
    if(i == 1):
        size = len(str)
        if(size > 20):
            print("First parameter out of boundary")
            r = 0
        else:
            for k in range(size):
                if(str[k] == "."):
                    print("First parameter wrong form")
                    r = 0
            if(r == 1):
                global gl_inputfile
                gl_inputfile += "file_"+str+".txt"
                global gl_inputdir
                gl_inputdir += "dir_"+str+".txt"
    # CASE 2: Validating the second parameter
    elif(i == 2):
        val = eval(str)
        k = 1
        for j in range(31):
            if(val == k):
                global gl_disksize
                gl_disksize = val
                return r
            k *= 2
        print("Second parameter is invalid")
        r = 0
    # CASE 3: Validating the third parameter
    elif(i == 3):
        val = eval(str)
        k = 1
        for j in range(11):
            if(val == k):
                global gl_blocksize
                gl_blocksize = val
                return r
            k *= 2
        print("Third parameter is invalid")
        r = 0
    return r


# Display Input files
def inputFiles():
    print("Input file is "+gl_inputfile)
    print("Input directory is "+gl_inputdir)


# Prints the helper document on terminal
def readFile(argc):
    f = open(argc, "r")
    if(f == None):
        print("Cannot open help document")
        exit(1)
    print(f.read())


# ************************** Tree ***************************
# init_dir(t_dir *, char *);
# init_file(char **);
# create_GTree();
# init_GDirs();
# init_GFiles();
# print_GTree(t_dir *, int);


# Initializes a directory node
def initDir(parent, name):
    dir = nodeDir()
    dir.parentDir = parent
    # Put absolute path given by name parameter into fullname variable
    dir.fullname = name
    # print(dir.fullname[2] == "\n")
    # Put / symbol after the fullname except on root directory
    if(parent != None):
        dir.fullname += "/"
    dir.dirDLList = dllist()
    dir.fileDLList = dllist()
    # rfind finds the last occuring / and reutrns its index
    i = name.rfind("/")
    if(i != -1):
        # Put everything before the last / in path variable
        for j in range(i):
            dir.path += name[j]
        # Put everything after the last / in name variable
        for k in range(i+1, len(name)):
            dir.name += name[k]
    return dir


# Initializes a file node
def initFile(name, size=0):
    if (size > gl_freespace):
        print("Not enough memory space!\n")
        return
    newFile = nodeFile()
    newFile.fullname = name
    # newFile.fullname[len(newFile.filename)] = "\0"
    i = name.rfind("/")
    if(i != -1):
        # Put everything before the last / in path variable
        for j in range(i):
            newFile.path += name[j]
        # Put everything after the last / in filename variable
        for k in range(i+1, len(name)):
            newFile.filename += name[k]
    newFile.fileSize = size
    newFile.fileNode = createFileLL(size)
    return newFile


# Finds the directory of file given as 2nd argument
def findDir(dir, name):
    if(dir.fullname in name):
        if(dir.dirDLList.size == 0):
            return dir
        else:
            i = 0
            childList = dir.dirDLList
            currentChild = childList[i]
            while(currentChild.fullname not in name and i < childList.size):
                currentChild = childList[i]
                i += 1
            if(currentChild.fullname in name):
                return findDir(currentChild, name)
            else:
                return dir
    return None


# Create a tree structure
def createTree():
    initDirDLL()
    initFileDLL()


# Yet to comment
def initDirDLL():
    file = open(gl_inputdir, "r")
    file.flush()
    if(file == None):
        print("Cannot open dir_file")
        exit(1)
    temp = file.read().splitlines()
    for each in temp:
        global root, gl_dircount
        if(root == None):
            root = initDir(root, each)
            gl_dircount += 1
        else:
            current = findDir(root, each)
            if(current.fullname != each):
                new = initDir(current, each)
                current.dirDLList.append(new)
                gl_dircount += 1
    file.flush()
    file.close()


def initFileDLL():
    global gl_filecount
    # Input file has entries as follows
    # <size> <full name>
    # 2048 ./1A/2B/meema.txt
    f = open(gl_inputfile, "r")
    f.flush()
    if(f == None):
        print("Cannot open dir_file")
        exit(1)
    # For each line in in inputfile
    temp = f.read().splitlines()
    for each in temp:
        # Ex/ [int fSize, string fName]
        arraySplit = each.split()
        # initFile function instantiates a nodeFile instance
        new = initFile(arraySplit[1], eval(arraySplit[0]))
        # Re-calculating total space
        onFileAdd(new.fileSize)
        if(root == None):
            print("Can't find the root folder")
        else:
            current = root
            current = findDir(current, new.fullname)
            current.fileDLList.append(new)
            gl_filecount += 1
    f.flush()
    f.close()


# Print Tree recursively
def printTree(node, tab):
    # Do nothing if current node is None
    if(node == None):
        return
    # Create whitespace for display purpose
    for i in range(tab):
        print(".....", end="")
    # Print node name infront of the whitespace
    print(node.name)
    # Return if the current node has no more child directories
    if(node.dirDLList == None):
        return
    dirChild = node.dirDLList
    # Recursively go into directory depth
    for j in range(node.dirDLList.size):
        printTree(dirChild[j], tab+1)
    # Return if a directory has no files in it
    if(node.fileDLList == None):
        return
    fileChild = node.fileDLList
    # Print all files in the directory
    for k in range(node.fileDLList.size):
        for l in range(tab):
            print(".....", end="")
        print(fileChild[k].filename)
    return


# ******************** File Linked List *********************
# create_Lfile(int);
# print_Lfile(t_file *, int);
# free_Lfile(t_file *);
# count_fragmentation(int);
# plus_filesize(int);
# minus_filesize(int);


# Returns LL specifying all memory locations of file blocks.
def createFileLL(fSize):
    global gl_blocksize
    t_file = nodeFileLL()
    current = nodeFileLL()
    new = nodeFileLL()
    blocks = 1
    i = 0
    if fSize > 0:
        # Obtain number of blocks needed to store file info.
        blocks = math.floor(fSize/gl_blocksize)
        # Add extra block if file needs more room
        if fSize != (blocks * gl_blocksize):
            blocks += 1
    else:
        return None
    for i in range(blocks):
        # find offset of every block according to disk.
        new.pma = requestDiskSpace() * gl_blocksize
        new.next = None
        if i == 0:  # First node in LL.
            t_file = new
            current = new
        else:  # All subsequent nodes
            current.next = new
            current = current.next
    return t_file


# Visits every node and prints its PMA value
# along with the size every node is taking in memory
def printFileLL(LL, fSize):
    i = 1
    print("\nLinked list of size " + str(fSize)+":\n")
    while(LL != None):
        print("\t"+str(i)+". Memory location: " + str(LL.pma), end=" - ")
        i += 1
        if fSize > gl_blocksize:
            print("Used memory: " + str(gl_blocksize) +
                  "/"+str(gl_blocksize)+" bytes")
            # Decrease size every iteration by block size.
            fSize -= gl_blocksize
        else:
            # Print the value of used size within a block.
            print("Used memory: " + str(fSize)+"/"+str(gl_blocksize)+" bytes")
            break
        LL = LL.next


# Frees up used blocks in disk
def freeFileLL(LL):
    if(LL == None):
        return
    while(LL != None):
        freeOccupiedDiskSpace(LL.pma/gl_blocksize)
        LL = LL.next


# Returns the leftover space in last block
def countFragmentation(fSize):
    global gl_blocksize
    i = fSize
    if(i == 0):
        return 0
    while(i > gl_blocksize):
        i -= gl_blocksize
    return gl_blocksize - i


# Recalculates global freespace and global fragmentation
def onFileAdd(fSize):
    global gl_freespace, gl_fragmentation
    gl_freespace -= fSize
    gl_fragmentation += countFragmentation(fSize)


# Recalculates global freespace and global fragmentation
def onFileRemove(fSize):
    global gl_freespace, gl_fragmentation
    gl_freespace += fSize
    gl_fragmentation -= countFragmentation(fSize)


# ******************** Disk Linked List *********************
# init_Ldisk();
# print_Ldisk();
# request_Ldisk();
# update_Ldisk();
# free_Ldisk(int);

def initDisk():
    # Find the number of blocks in disk
    global gl_totalblock, gl_fragmentation, gl_freespace, Disk
    gl_totalblock = gl_disksize/gl_blocksize
    # Disk is empty aka free
    Disk.status = "FREE"
    # Disk blocks 0 to max-1 are all free
    Disk.begin = 0
    Disk.end = gl_totalblock - 1
    # Only one node
    Disk.next = None
    gl_fragmentation = 0
    # All space is free
    gl_freespace = gl_totalblock*gl_blocksize


def printDisk():
    temp = Disk
    while(temp != None):
        if(temp.status == "FREE"):
            print("Free blocks from " + str(temp.begin) + " to " + str(temp.end))
        else:
            print("Used blocks from " + str(temp.begin) + " to " + str(temp.end))
        temp = temp.next
    print("Fragmentation: " + str(gl_fragmentation) + " bytes")
    print("Free Disk Space: " + str(gl_freespace) + " bytes")


# Returns the block number of the first vacant block found.
def requestDiskSpace():
    global Disk
    temp = nodeDiskLL()
    current = Disk
    previous = None
    # Iterate till an empty space is found
    while(current.status == "USED"):
        previous = current
        if(current.next == None):
            print("No more available storage space")
            return -1
        current = current.next
    # FREE space found
    # If more than one contigious block is free
    # Isolate the first free block and return its block number
    if(current.begin != current.end):
        temp.status = "USED"
        temp.begin = current.begin
        temp.end = current.begin
        current.begin += 1
        temp.next = current
    else:  # Only single block is free, use it.
        temp = current
        temp.status = "USED"
    # If the first block of disk is found to be free.
    if(previous == None):
        Disk = temp
    else:
        previous.next = temp
    updateDisk()
    return temp.begin


# Updates disk such that we have only 2 nodes(with status USED and FREE)
def updateDisk():
    temp = nodeDiskLL()
    previous = Disk
    current = Disk.next
    while(current != None):
        # If both statuses same, merge the blocks together
        if(previous.status == current.status):
            previous.end = current.end
            previous.next = current.next
            temp = current
            del temp
            current = current.next
            updateDisk()
        else:
            previous = current
            current = current.next


# PUT COMMENTS IN THIS FUNCTION
def freeOccupiedDiskSpace(start):
    global Disk
    new = nodeDiskLL()
    current = Disk
    previous = None
    new.status = "FREE"
    new.begin = start
    new.end = start
    while(current != None):
        if(current.begin <= start and current.end >= start):
            if(current.begin == start):
                if(previous != None):
                    previous.next = new
                else:
                    Disk = new
                new.next = current
                current.begin += 1
                updateDisk()
                break
            elif(current.end == start):
                current.end = current.end - 1
                new.next = current.next
                current.next = new
                updateDisk()
                break
            else:
                temp = nodeDiskLL()
                temp.status = "USED"
                temp.begin = current.begin
                temp.end = start-1
                if(previous != None):
                    previous.next = temp
                else:
                    Disk = temp
                temp.next = new
                new.next = current
                current.begin = start+1
                updateDisk
                break
        previous = current
        current = current.next


def main(argc, argv):
    n = 0

    if (os.getcwd() == None):
        print("Virtual Memory Exhausted!")
        exit(1)
    x = inputCheck(argc, argv)
    if (x == 0):
        exit(1)

    inputFiles()
    initDisk()
    createTree()
    print("\n-------- FileSystem status --------")
    printDisk()
    print("-----------------------------------\n")
    current = root
    # printTree(current, 0)

    while(True):
        val = input(current.fullname+"> ")
        vect = val.split()
        if (vect[0] == "exit"):
            exit(0)
        elif ((vect[0] == "dir") or (vect[0] == "ls")):
            dirORls(current)
        elif (vect[0] == "prdisk"):
            printDisk()
        elif (vect[0] == "cd"):
            if (vect[1] == ".."):
                if(current == root):
                    print("Permission denied!")
                else:
                    current = current.parentDir
            else:
                temp = chdir(current, vect[1])
                if (temp != None):
                    current = temp
                else:
                    print(vect[1]+": No such file or directory")
        elif (vect[0] == "printfiles"):
            printout(current)
        elif (vect[0] == "printtree"):
            printTree(current, 0)
            print("")
        elif (vect[0] == "mkdir"):
            mkdir(current, vect[1])
        elif (vect[0] == "rmdir"):
            rmdir(current, vect[1])
        elif (vect[0] == "delete"):
            rmdir(current, vect[1])
            rmfile(current, vect[1])
        elif (vect[0] == "create"):
            mkfile(current, vect[1], eval(vect[2]))
        elif (vect[0] == "removefile"):
            rmfile(current, vect[1])
        elif (vect[0] == "removebytes"):
            remove(current, vect[1], eval(vect[2]))
        elif (vect[0] == "appendbytes"):
            append(current, vect[1], eval(vect[2]))
        else:
            print(vect[0]+": No such command, try again.")
    return 0


# Driver code
if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
