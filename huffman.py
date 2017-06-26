#!/usr/bin/python2

import os
import sys
import marshal
import array
import Queue
from collections import Counter
#Represents the dictionary that will hold binary values
#for the variables in the message
dic = {}

try:
    import cPickle as pickle
except:
    import pickle

#Adds a number to the value of the variable which is then
#assigned to the dictionary
def assign(node, num):
    #Loops to assign value to a single variable
    for i in node:                  
        if type(i) == list:
            i[0] = num + i[0]
        elif type(i) == tuple:
            assign(i, num)

#Adds the variable and its value to the tree
def add(value):
    #Checks to determine whether it's adding a variable+value
    #combo to the tree
    if len(value) == 3:
        return value[1:]
    else:
        return value[1]

#Creates a Huffman tree of the message with the binary values
#attached to each variable
def tree(freq):
    #Creates PriorityQueue which orders the variables and is
    #efficient enough to support the program
    values = Queue.PriorityQueue()
    #Sets up the frame for the tree with values
    for x in freq:                   
        values.put((freq[x], x, [""]))
    #Fills the values for the variables in the tree
    #Initialization: We start with a queue full of tuples
    #Maintenance: Loop as long as the size of the queue is greater than 1
    #We get the two smallest values every loop so the size of the queue
    #is decreasing. Eventually, there will only be 1 tuple left. 
    #Termination: The loop terminates when there is only 1 tuple left.
    #This is the combined tuple with the binary values of each element.
    while values.qsize() > 1:           
        left, right = values.get(), values.get()    
        assign(left, "0")
        assign(right, "1")
        values.put((left[0] + right[0], (add(left), add(right))))
    #Returns the completed tree with values
    return values.get()[1]

#Creates a dictionary based on the tree with binary values
#attached to the variables
def getDictionary(tree):
    #Loops through the tree and creates the dictionary by
    #assigning the values to the appropriate variable
    for i in tree:
        if type(i) == tuple:
            if type(i[0]) == str:
                dic[i[0]] = ''.join(i[1])
            elif type(i[0]) == tuple:
                getDictionary(i)
    return dic

#Encodes the plain message
def code(msg):
    #Get the frequency dictionary before creating the dictionary
    #for the message
    counter = Counter(msg)
    getDictionary(tree(counter))
    #Makes the coded binary string based off of the message
    string = ""
    for i in msg:
        string += dic[i]
    #Returns the encoded string and the dictionary needed to
    #decode it
    return (string, dic)

#Decodes the coded message
def decode(string, tree):
    #Reverses the tree variables and values
    dictionary = tree
    reverse = {v: k for k, v in dictionary.iteritems()}
    #Temporary values used in the loop
    meaning = ""
    temp = string[0]
    i = 0
    #Constructs the meaning of the coded message
    #Initialization: We start with a nonempty string which is the coded message
    #Maintenance: We loop for the length of the string. We go through each char
    #one by one, so we're approaching the end of the string with every loop.
    #Termination: Eventually, we'll get the last char to decode. After that,
    #we will have reached the length of the string and there's nothing left
    #to decode so the loop will terminate.
    while (i < len(string)):
        #Checks to see whether the binary value belongs in
        #the tree using temp. If it does then its assigned
        #value is added to the string.  If it's not then
        #increment the temp by the next number.
        if temp in reverse:
            meaning += reverse[temp]
            try:
                temp = string[i+1]
            except IndexError:
                temp = string[i]
        else:
            temp += string[i+1]
        i += 1
    #Returns the meaning of the coded message
    return meaning

#Compresses the plain message
def compress(msg):
    #Creates the binary string and dictionary for the message
    string, dic = code(msg)
    #Represents compressed message
    bitstream = array.array("B")
    #Keeps track of the decimal value for the binary
    buf = 0
    #Ensures that we have at most 8 bit bytes
    count = 0
    #Loops through every binary value in the message and records
    #the equivalent decimal value for every set of 8 values

    #Initialization: There exists a nonempty string value
    #Maintenance: With every loop, we move on to the next bit
    #so the problem is getting smaller since there's a finite
    #number of bits that make up the string
    #Termination: We will eventually traverse every bit in the string
    #then there is nothing left to compress, so the loop terminates
    for bit in string:
        if bit == "0":
            buf = (buf << 1)
        elif bit == "1":
            buf = (buf << 1) | 1
        count += 1
        if count >= 8:
            bitstream.append(buf)
            buf = 0
            count = 0
    #If the message%8 != 0 then we add the remaining decimal value
    #equivalent portion of the message to the compressed message
    if count < 8:
        bitstream.append(buf)
    #Returns compressed message and a tuple of the dictionary
    #and the length of the original message
    return bitstream, [dic, len(string)]

#Decompresses the compressed message
def decompress(string, decoderRing):
    #Initialize a variable to store the string of converted binary values
    message = ""
    #Gets the array of decimal values
    bitstream = array.array('B', string)
    #Gets the dictionary that was returned in compress
    dictionary = decoderRing[0]
    #Gets the len of the original binary code that was returned in compress
    length = decoderRing[1]
    #Initialization: Bitstream is not empty
    #Maintenance: Loop through the contents of bitstream as long as a value exists
    #With every loop, we move on to the next value so the problem is getting smaller
    #since there's a finite number of values in the bitstream
    #Termination: Terminate once there are no more values in bitstream
    for x in bitstream:
        #Add the binary value to the message
        if bitstream[len(bitstream)-1] != x:
            message += bin(x)[2:].zfill(8)
        #For the last value, make sure there's the right num of leading zeroes
        #Do this by figuring out how many characters remain, then remove the
        #amount of unnecessary zeroes
        else:
            remaining = 8 - (length - len(message))
            remaining = (bin(x)[2:].zfill(8))[remaining:]    
            message += remaining
    #Once we have the binary, call decode to convert it into the original message
    final = decode(message, dictionary)
    return final

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        string = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(string)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = code(string)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickled_tree, msg = marshal.load(fp)
        tree = pickle.loads(pickled_tree)
        fp.close()
        if decompressing:
            string = decompress(msg, tree)
        else:
            string = decode(msg, tree)
            print(string)
        fp = open(outfile, 'wb')
        fp.write(string)
        fp.close()
