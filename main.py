from tkinter import *
import glob
import re
import nltk
import os
import numpy as np
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
stemmer=PorterStemmer()
d1 = {}
d2 = {}

#open stop word file and read stopwords from file
f = open("Stopword-List.txt")
stopwords = f.read()
stopwords = word_tokenize(stopwords)
f.close()

#set pat of files
file_folder = 'Abstracts/*'

#for loop for iterate every files in folder Abstract
#for inverted index
for file in glob.glob(file_folder):
    f = open(file)
    #read content of file
    content = f.read()
    content = content.lower()
    # convert 1.txt to 1 because i want doc id only
    file = re.sub('[^0-9]', '', file)
    file=int(file)

    #remove puntuations
    content = re.sub('[^0-9a-z\s]', ' ', content)

    #make tokens
    tokens = word_tokenize(content)

    #remove stopwords
    for word in tokens:
      if word in stopwords:
        tokens.remove(word)

    #apply stemming
    j=0
    for word in tokens:
        # apply stem on every token
      tokens[j]=stemmer.stem(word)
      j=j+1
    tokens_final = []
    #Romove duplicates
    [tokens_final.append(x) for x in tokens if x not in tokens_final]

    # making inverted index using dictionary
    for word in tokens_final:
        if word not in d1:
            d1[word]=[]
            d1[word].append(file)
        else:
            d1.get(word).append(file)

#sorting of posting list of every term
for item in d1:
    d1.get(item).sort()


#for position index
for file in glob.glob(file_folder):
    flag=0
    f = open(file)
    #read content of file
    content = f.read()
    content = content.lower()
    # convert 1.txt to 1 because i want doc id only
    file = re.sub('[^0-9]', '', file)
    file=int(file)

    #remove puntuations
    content = re.sub('[^0-9a-z\s]', ' ', content)

    #make tokens
    i=0
    tokens = word_tokenize(content)

    # remove stopwords
    for word in tokens:
      if word in stopwords:
        tokens.remove(word)

    # #apply stemming
    j = 0
    for word in tokens:
        # apply stem on every token
        tokens[j] = stemmer.stem(word)
        j = j + 1

    #Position index
    k=0
    for word in tokens:
        if word not in d2:
            d2[word]={}
            d2[word][file]=[]
            d2[word][file].append(k)

        else:
            #new word in dic
            if file not in d2[word]:
                d2[word][file] = []
                d2[word][file].append(k)

            #exixisting word with same document
            else:
                d2[word][file].append(k)
        k=k+1
    f.close()


# print position indexes
# for item in d2:
#     print(item ,d2[item],end="\n")

# And Operator
def AND(l1,l2):
    i=0
    result=[]
    j=0

    # if element same in list increament both indexes
    while(i<len(l1) and j<len(l2) ):
        if(l1[i]==l2[j]):
            result.append(l1[i])
            i=i+1
            j=j+1

        # if element of list1 less than list2 , increament index of list1
        elif(l1[i]<l2[j]):
            i=i+1
        # if element of list2 less than list1 , increament index of list2
        else:
            j=j+1
    return result

# Or Operator
def OR(l1,l2):
    i=0
    result=[]
    j=0
    while(i<len(l1) and j<len(l2) ):

        # if element same in list increament both indexes
        if(l1[i]==l2[j]):
            result.append(l1[i])
            i=i+1
            j=j+1
        # if element of list1 less than list2 , increament index of list1 and append element of list1
        elif(l1[i]<l2[j]):
            result.append(l1[i])
            i=i+1

        # if element of list2 less than list1 , increament index of list2 and append element of list2
        else:
            result.append(l2[j])
            j=j+1
    if(i<len(l1)):
        while(i<len(l1)):
            result.append(l1[i])
            i=i+1
    if (j < len(l2)):
        while (j < len(l2)):
            result.append(l2[j])
            j = j + 1
    return result

# NOT Operator
def NOT(l1):
    result=[]
    for t in range(448):
        result.append(t+1)
    for num in l1:
        if num  in result:
            result.remove(num)
    return result

#Proximity queuery
def proximity(result,t1,t2,d2,diff):
    print (diff)
    i=0
    flag=0
    j=0
    output=[]
    # iterate every document which come after and operation
    for item in result:
        flag=0
        print("\n\n")

        #item= doc no
        # position of documents of t1
        for i in d2[t1][item]:
            # position of documents of t2
            for j in d2[t2][item]:
                # check difference
                if(int(abs(i-j))-1<=int(diff)):
                    output.append(item)
                    flag=1
                    break
            if(flag==1):
                break
    return(output)

#if Click on Search button
def search():
    queury=screen.get()
    queury = queury.lower()

    # Make token if queuery
    queury = word_tokenize(queury)
    j = 0;
    #Apply Stemming on queuery
    for word in queury:
        queury[j] = stemmer.stem(word)
        j = j + 1

    # First token assignt to result
    result = d1.get(queury[0])
    length = len(queury)

    #if only one word in queuery
    if (length == 1):
        result = result
    else:
        i = 1
        while (i < length):
            if (queury[i] == "and"):
                # Apply AND queuery
                if (queury[i + 1] == "not"):
                    print(queury[i+2])
                    print(queury[i-1])
                    result = NOT(d1.get(queury[i+2]))
                    result=AND(d1.get(queury[i-1]),result)
                else:
                    result = AND(result, d1.get(queury[i + 1]))
            elif (queury[i] == "or"):
                # Apply OR queuery
                if (queury[i + 1] == "not"):
                    result = NOT(d1.get(queury[i+2]))
                    result=OR(d1.get(queury[i-1]),result)
                else:
                    result = OR(result, d1.get(queury[i + 1]))

            elif (queury[i - 1] == "not"):
                # Apply NOT queuery
                result = NOT(d1.get(queury[i]))
                i = i - 1


            elif((queury[i-1]!="and" and queury[i]!="and") or (queury[i-1]!="or" and queury[i]!="or")):
                # Apply Proximity Queury
                diff=re.sub('[^0-9]',"",queury[i+1])
                result=AND(result,d1.get(queury[i]))
                result=proximity(result,queury[0],queury[1],d2,diff)
            i = i + 2
    global output
    output = Label(root, text="", font=("Helvetica", 13), wraplength=700)
    output.place(x=30, y=300)
    global tx
    tx= Label(root, text="Retrieved Documents: ", font=("Helvetica", 18))
    tx.place(x=10, y=250)
    if(len(result)>0):
        output = Label(root, text=result, font=("Helvetica", 13),wraplength=1100)
        output.place(x=30, y=300)
        return None
    else:
        print("none")

root = Tk()

#Set size and background-color of window of Application
root.geometry("900x600")
root.configure(background='#6666ff')
root.title("Boolean Retrievel Model")

text = Label(root, text="Search Query: ", font=('Helvetica 22 bold'))
text.place(x=50,y=60)

# clear query and output
def clear_text():
    global output
    screen.delete(0,END)
    output.destroy()

#Create SearchBox for Input Queuery
screen=Entry(root, font="lucida 20" , bg='#33FFFF' ,bd="4",width=55 )
screen.place(x=50,y=100)

#Create button for search
b1=Button(root,text="Search",command=search,font='Helvetica', bg='#0000CC', height=2, width=12,fg='white')
b1.place(x=80,y=170)

#create button for clearing
b2=Button(root,text="Clear",command=clear_text,font='Helvetica', bg='#0000CC', height=2, width=12,fg='white')
b2.place(x=230,y=170)

root.mainloop()
