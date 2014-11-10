
#__author__ = 'SYSTEM'
import re
import json
#import nltk
import math
import random
from random import randrange

#read the content of the file and return it
def read_files(txt):
    file = open(txt, 'r') #storing txt in file
    data = file.read() #reading the file and storing it
    return separate_into_sentences(data) #separating into sentences and returning it

#returns the index of the end of the sentence
def first_sentence_end(data, a, b, c):
    if a:
        if b:
           if c:
               return len(data) - 1
           else:
               return data.find('!')
        else:
            if c:
                return data.find('?')
            else:
                if data.find('?') < data.find('!'):
                    return data.find('?')
                else:
                    return data.find('!')
    else:
        if b:
            if c:
                return data.find('.')
            else:
                if data.find('.')<data.find('!'):
                    return data.find('.')
                else:
                    return data.find('!')
        else:
            if c:
                if data.find('.')<data.find('?'):
                    return data.find('.')
                else:
                    return data.find('?')
            else:
                if data.find('.')<data.find('?'):
                    if data.find('.')<data.find('!'):
                        return data.find('.')
                    else:
                        return data.find('!')
                else:
                    if data.find('?')<data.find('!'):
                        return data.find('?')
                    else:
                        return data.find('!')

#separate raw data into sentences
def separate_into_sentences(data):
    if data.find('.')==-1 and data.find('?')==-1 and data.find('!')==-1: #if only 1 sentence in document return itself
        return data
    a, b, c = True, True, True #initializing booleans to see whether fullstops, exclamation marks and question marks exist
    if data.find('.')!=-1: #if no fullstops
        a = False
    if data.find('?')!=-1: #if no question marks
        b = False
    if data.find('!')!=-1: #if no exclamation marks
        c = False

    sentences = [] #initializing an empty set to contain a list of all the sentences
    while len(data)>0: #while there are sentences to sort out
        i = first_sentence_end(data, a, b, c) #find the first instance of the end of the sentence
        sentences.append(data[:i+1]) #add the new sentence to the list of sentences
        data = data[i+1:] #remove the sentence from the data left to be sorted
        a, b, c = True, True, True
        if data.find('.')!=-1: #updating the boolean values to see if there are any sentences left
            a = False
        if data.find('?')!=-1:
            b = False
        if data.find('!')!=-1:
            c = False
    return sentences

#to check if the input is a number
def is_not_number(s):
    try:
        float(s) #is a number
        return False
    except ValueError: #isn't a number
        return True

#to calculate the scores of all words in each sentence
def score_calculate(sentences):
    i = 0
    analysis = [] #an empty list which will store all sentences
    #initializing stop words which are words to be ignored if occurring
    stop_words=['a','able','about','across','after','all','almost','also','am','among','an','and','any','are','as','at','be','because','been','but','by','can','cannot','could','dear','did','do','don', 'does','down', 'either','else','ever','every','for','from','get','got','had','has','have','he','her','hers','him','his','how','however','i','if','in','into','is','it','its','just','last', 'least','let','like','likely','may','me','might','more','most','must','my','neither','no','nor','not','of','off','often','on','only','or','other','our','own','quite', 'rather','said','say','says','she','should','since','so','some','than','that','the','their','them','then','there','these','they','this','tis','to','too','twas','us','wants','was','we','were','what','when','where','which','while','who','whom','whose', 'why','will','with','would','yet','you','your']
    while i<len(sentences): #iterating through each sentence
        words1 = re.sub("[^\w]", " ", sentences[i]).split() #separating the sentence into words and storing it into list
        for word in words1: #iterating through each word
            if word.lower() not in stop_words and (len(word)>=3 or (word.upper()==word and len(word)==2) and is_not_number(word)): #checking to see that it isn't stop word, is not number and is long enough
                not_already = True #initializing boolean to see if word is already there in analysis
                for st in analysis: #iterating through words in analysis
                    if word.lower() == st[0].lower(): #if word already there
                        length = len(sentences)
                        length *= 1.0
                        score = (len(sentences) - i) / length #calculating the score of the word
                        st[1] += score #incrementing the score of the word by the new score
                        not_already=False #changing boolean to know that word was already there
                        break
                if not_already: #if word doesn't exist already
                    length = len(sentences)
                    score = (len(sentences) - i) / length
                    case = [word, score] #calculating the score and storing the word with the score in a list
                    analysis.append(case) #adding this list to the analysis
        i += 1
    return analysis

#Parameter: pathname of file
#Returns the list of words in the document with individual scores and list of sentences
def execute_program(txt):
    sentences = read_files(txt) #reading the files and sorting and saving them into sentences
    analysis = score_calculate(sentences)
    analysis = sorted(analysis, key=lambda x: x[1], reverse=True) #sorting analysis in descending order
    return analysis, sentences #returning analysis and list of sentences

#Returns the top 50 words of a document with scores and list of sentences
def get_top_words(filepathname):
    words, sentences=execute_program(filepathname) #getting list of words with scores and list of sentences
    return words[:50], sentences #returning the top 50 words of the document and a list with all sentences

#creates co_graph of word if not existing already
def graph_append(word, co_graph):
    if word not in co_graph: #if the word doesn't already exist in co_graph
        co_graph[word]=[] #initialize the co_graph of the word into a null set

#adds word to co_graph of another word
def add_word_in_relationship(word, w_to_add, co_graph, words1):
    for couplet in co_graph[word]: #iterating through each couplet of co_graph of the word
        if w_to_add in couplet: #if the word already is related to the co_graph of the word
            couplet[1] += 1 #incrementing the count by one
            return co_graph #break from loop
    co_graph[word].append([w_to_add,  1])
    return co_graph

#to find overall score of words in co_graph of a word
def add_scores(scores, words):
    for word in words:
        x=True
        for couplet in scores:
            if word[0] in couplet[0]:
                couplet[1] += word[1]
                x=False
        if x:
            scores.append(word)
    return scores

#nouns = set()
#def noun(word):
#    from nltk.corpus import wordnet as wn
#    if word in nouns:
#        return True
#    x = wn.synsets(word)
#    if x == None or len(x) == 0:
#        nouns.add(word)
#    return True
#    for syn in x:
#        if syn.pos == 'n':
#            nouns.add(word)
#            return True
#    return False

#initializing the list for containing paths of all documents
paths = ['D:/test.txt', 'D:/test1.txt', 'D:/test2.txt', 'D:/test3.txt', 'D:/test4.txt', 'D:/test5.txt', 'D:/test6.txt', 'D:/test7.txt', 'D:/test8.txt', 'D:/test9.txt', 'D:/test10.txt', 'D:/test11.txt', 'D:/test12.txt', 'D:/test13.txt', 'D:/test14.txt', 'D:/test15.txt', 'D:/test16.txt', 'D:/test17.txt', 'D:/test18.txt', 'D:/test19.txt', 'D:/test20.txt', 'D:/test21.txt', 'D:/test22.txt', 'D:/test23.txt', 'D:/test24.txt', 'D:/test25.txt', 'D:/test26.txt', 'D:/test27.txt', 'D:/test28.txt', 'D:/test29.txt', 'D:/test30.txt']
#print(paths)
ind_scores=[] #to store individual scores
co_graph={} #initializing empty cograph
cographforeverydocument=[]
for path in paths: #iterating through all the paths of all documents
    cog={}
    words1, sentences=get_top_words(path) #getting a list containing words with individual scores and list of sentences
    words2 = {}
    for e in words1:
        words2[e[0]] = e[1]
    #print (words1)
    ind_scores=add_scores(ind_scores, words1)
    words=[]
    for x in words1:
        words.append(x[0]) #taking only the words and saving them in list
    for word in words:
        graph_append(word, co_graph) #initializing the cographs of words to null sets
        graph_append(word, cog)
    #print (co_graph)
    i=0
    while i<len(sentences): #iterating through every sentence
        w=re.sub("[^\w]", " ", sentences[i]).split() #sorting sentence into words
        #print(w)
        j=0
        while j<len(w): #iterating through every word
            if w[j] in words: #if the word is an important word
                k=0
                while k<j: #iterating through every word in the sentence before it
                    if w[k] in words and w[k]!=w[j]: #if that word too is an important word
                        co_graph = add_word_in_relationship(w[j], w[k], co_graph, words2) #add it to relationship with the main word
                        cog=add_word_in_relationship(w[j], w[k], cog, words2)
                    k += 1
                k=j+1
                while k<len(w): #iterating through every word in the sentence after it
                    if w[k] in words and w[k]!=w[j]: #if that word too is an important word
                        co_graph = add_word_in_relationship(w[j], w[k], co_graph, words2) #add it to relationship with the main word
                        cog = add_word_in_relationship(w[j], w[k], cog, words2)
                    k += 1
            j += 1
        i += 1
    #pr    co_graph)
    count=0
    for key, value in co_graph.items():
        co_graph[key] = sorted(value, key=lambda x: x[1], reverse=True) #sorting the contents of the cograph of that word in descending order
        count += 1 #counting the number of keys in the cograph
    for key, value in cog.items():
        cog[key]=sorted(value, key=lambda x: x[1], reverse=True)
    #print(cog)
    cographforeverydocument.append(cog)
ind_scores = sorted(ind_scores, key=lambda x: x[1], reverse=True) #sorting the individual scores in descending order
sorted_graph=[] #this will store the co_graph in a sorted array
z=0
#print(co_graph['feeling'])
#print(len(co_graph['coach']))
for keyword in co_graph: #iterating through every word which has a co_graph
    sum = 0
    for list in co_graph[keyword]:
        sum = sum+list[1] #finding the sum of the contents of the scores of the words in the co_graph of the word
    sorted_graph.append((keyword, math.log(1.0 * len(co_graph[keyword]), 2) * sum)) #adding an array with the word, number of words connected with, and sum
#print(sorted_graph)

sorted_graph.sort(key=lambda x: x[1], reverse=True) #sorting based on length times sum of scores of word of co_graph
#sorted_graph.sort(key=lambda x: x[2], reverse=True) #sorting based on sum of scores of words in co_graph
#b = sorted_graph.copy()
#print(co_graph['football'])
#print (sorted_graph)
#for i in range(0,40):
  #print (a[i][0], a[i][1])#, '\t', b[i][0], b[i][2]) #printing it out
  #print(b[i])
cliques = []
edges_done=[]
i=0
edges_sorted=[]
for node in sorted_graph:
    for edge in co_graph[node[0]]:
        if [[edge[0], node[0]], edge[1]] not in edges_sorted and [[node[0], edge[0]], edge[1]] not in edges_sorted:
            edges_sorted.append([[edge[0], node[0]], edge[1]])
edges_sorted.sort(key=lambda x : x[1], reverse=True)
#for key in edges_sorted:
#    print(key)
topsum=0
for j in range(0, 200):
    topsum += edges_sorted[j][1]
topsum*=1.0
#print(i/200)
i=0
while edges_sorted[i][1]>topsum/200:
    print(edges_sorted[i])
    i+=1
i=0
j=0
cliques=[]
topsum=topsum/200
while edges_sorted[j][1]>=topsum:
    #print(i)
    cst=edges_sorted[j][1]
    rel=[edges_sorted[j][0][0], edges_sorted[j][0][1]]
    if rel in edges_done:
        j += 1
        continue
    ii=0
    jj=0
    while ii<len(co_graph[rel[0]]) and jj<len(co_graph[rel[1]]):
        if co_graph[rel[0]][ii][1]<0.5*cst and co_graph[rel[1]][jj][1]<0.5*cst:
            break
        if co_graph[rel[0]][ii][1]>co_graph[rel[1]][jj][1] and co_graph[rel[0]][ii][1]>=0.5*cst:
            for p in rel:
                x=False
                if [p, co_graph[rel[0]][ii][0]] in edges_done:
                    #print('Edge over 0', co_graph[rel[0]][ii][0])
                    x=False
                    break
                for coup in co_graph[p]:
                    if coup[0]==co_graph[rel[0]][ii][0] and coup[1]>=0.5*cst:
                        x=True
                        break
                if not x:
                    break
            if x:
                #for p in rel:
                #    edges_done.append([p, co_graph[rel[0]][ii][0]])
                #    edges_done.append([co_graph[rel[0]][ii][0], p])
                rel.append(co_graph[rel[0]][ii][0])
            ii += 1
            continue
        if co_graph[rel[0]][ii][1]<co_graph[rel[1]][jj][1] and co_graph[rel[1]][jj][1]>=0.5*cst:
            for p in rel:
                x=False
                if [p, co_graph[rel[1]][jj][0]] in edges_done:
                    #print('Edge over 1', co_graph[rel[1]][jj][0])
                    break
                for coup in co_graph[p]:
                    if coup[0]==co_graph[rel[1]][jj][0] and coup[1]>=0.5*cst:
                        x=True
                        break
                if not x:
                    break
            if x:
                #for p in rel:
                #    edges_done.append([p, co_graph[rel[1]][jj][0]])
                #    edges_done.append([co_graph[rel[1]][jj][0], p])
                rel.append(co_graph[rel[1]][jj][0])
            jj += 1
            continue
        if co_graph[rel[0]][ii][1]==co_graph[rel[1]][jj][1] and co_graph[rel[0]][ii][1]>=0.5*cst:
            if co_graph[rel[0]][ii+1][1]>co_graph[rel[1]][jj+1][1]:
                for p in rel:
                    x=False
                    if [p, co_graph[rel[0]][ii][0]] in edges_done:
                        #print('Edge over 21', co_graph[rel[0]][ii][0])
                        break
                    for coup in co_graph[p]:
                        if coup[0]==co_graph[rel[0]][ii][0] and coup[1]>=0.5*cst:
                            x=True
                            break
                    if not x:
                        break
                if x:
                    #for p in rel:
                    #    edges_done.append([p, co_graph[rel[0]][ii][0]])
                    #    edges_done.append([co_graph[rel[0]][ii][0], p])
                    rel.append(co_graph[rel[0]][ii][0])
                ii += 1
                continue
            if co_graph[rel[0]][ii+1][1]<co_graph[rel[1]][jj+1][1]:
                for p in rel:
                    x=False
                    if [p, co_graph[rel[1]][jj][0]] in edges_done:
                        #print('Edge over 22', co_graph[rel[1]][jj][0])
                        break
                    for coup in co_graph[p]:
                        if coup[0]==co_graph[rel[1]][jj][0] and coup[1]>=0.5*cst:
                            x=True
                            break
                    if not x:
                        break
                if x:
                    #for p in rel:
                    #    edges_done.append([p, co_graph[rel[1]][jj][0]])
                    #    edges_done.append([co_graph[rel[1]][jj][0], p])
                    rel.append(co_graph[rel[1]][jj][0])
                jj += 1
                continue
            if co_graph[rel[0]][ii+1][1]==co_graph[rel[1]][jj+1][1]:
                irand=randrange(0, 2)
                if irand==0:
                    for p in rel:
                        x=False
                        if [p, co_graph[rel[0]][ii][0]] in edges_done:
                            #print('Edge over 231', co_graph[rel[0]][ii][0])
                            break
                        for coup in co_graph[p]:
                            if coup[0]==co_graph[rel[0]][ii][0] and coup[1]>=0.5*cst:
                                x=True
                                break
                        if not x:
                            break
                    if x:
                        #for p in rel:
                        #    edges_done.append([p, co_graph[rel[0]][ii][0]])
                        #    edges_done.append([co_graph[rel[0]][ii][0], p])
                        rel.append(co_graph[rel[0]][ii][0])
                    ii += 1
                    continue
                else:
                    for p in rel:
                        x=False
                        if [p, co_graph[rel[1]][jj][0]] in edges_done:
                            #print('Edge over 232', co_graph[rel[1]][jj][0])
                            break
                        for coup in co_graph[p]:
                            if coup[0]==co_graph[rel[1]][jj][0] and coup[1]>=0.5*cst:
                                x=True
                                break
                        if not x:
                            break
                    if x:
                        #for p in rel:
                        #    edges_done.append([p, co_graph[rel[1]][jj][0]])
                        #    edges_done.append([co_graph[rel[1]][jj][0], p])
                        rel.append(co_graph[rel[1]][jj][0])
                    jj += 1
                    continue


    if len(rel)>2:
        cliques.append(rel)
        #print(rel)
        #print('added the new clique')
        #edges_done.append([rel[0], rel[1]])
        #edges_done.append([rel[1], rel[0]])
    j += 1
    #print('ready to look at the next clique')


#print(len(cliques))
#cliques.sort(key=lambda x: len(x), reverse=True)
i=0
for k in cliques:
    print('Clique', i, k)
    print('\n')
    j=0
    while j<len(k):
        y=0
        while y<j:
            for x in co_graph[k[j]]:
                if x[0]==k[y]:
                    print (k[j], x[1], k[y])
            y += 1
        y = j+1
        while y<len(k):
            for x in co_graph[k[j]]:
                if x[0]==k[y]:
                    print(k[j], x[1], k[y])
            y += 1
        j += 1
    print('\n')
    i += 1

communities=[]
for x in cliques:
    if len(x)>3:
        communities.append(x)
x=True
while x:
    i=0
    x=False
    while i<len(communities):
        j=i+1
        while j<len(communities):
            count=0
            for p in communities[i]:
                if p in communities[j]:
                    count += 1
            if count>=3:
                cnt=1
                c=communities[j]
                ppp=j
                while ppp<len(communities)-1:
                    communities[ppp]=communities[ppp+1]
                    ppp+=1
                del communities[len(communities)-1]
                for x in c:
                    if x not in communities[i]:
                        communities[i].append(x)
                x=True
            j += 1
            if x:
                break
        if x:
            break
        i += 1

i=0
print('Time to look at communities')
print('\n')
print('\n')
print('\n')
print('\n')
for k in communities:
    print('Community', i, k)
    print('\n')
    j=0
    while j<len(k):
        y=0
        while y<j:
            for x in co_graph[k[j]]:
                if x[0]==k[y]:
                    print (k[j], x[1], k[y])
            y += 1
        y = j+1
        while y<len(k):
            for x in co_graph[k[j]]:
                if x[0]==k[y]:
                    print(k[j], x[1], k[y])
            y += 1
        j += 1
    print('\n')
    i += 1
exit()



""" the possible improvements which can be made now are:
    1. running time
    2. identifying whether cliques are repeated with elements in a different order
    3. check whether cliques can be made bigger
    4. check whether cliques can be formed without just 1, 2 and instead something like 1, 4, 5, 7 and so on
    5. possibly form cliques wrt each document
    """


