import os
import collections
import json

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize


files_path= 'E:/Anul 4/sem 2/RIW/ProiectRIW/test_files'
stop_words_path = r'stopwords'
exceptions_words_path = r'exceptions'

ps = PorterStemmer()


class myTextParser:

    def __init__(self, dirPath):
        self.dirPath=dirPath
        self.files = []
        self.directories =[self.dirPath]
        self.exceptions = []
        self.stops = []
        self.words = collections.OrderedDict()
        self.inverted_index={}

        self.read_files()

    def read_stopwords_and_exceptions(self,file_path, list_of_words):
        with open(file_path, 'r',encoding='UTF-8') as file:
            word = ''
            letter = file.read(1)
            while letter != '':
                if letter != '\n':
                    word += letter.lower()
                else:
                    list_of_words.append(word)
                    word = ''
                letter = file.read(1)

    def creeaza_index_direct(self,file_path):

        f=open(file_path, 'r')
        self.words[file_path]={}
        letter=f.read(1).lower()
        word=letter
        while True :
            letter = f.read(1).lower()

            if  letter=='':
                break
            else:

                if letter >= 'a' and letter <= 'z' or letter >= '0' and letter <= '9':
                    word=word+letter
                else:
                    if word in self.exceptions:

                        if word in self.words[file_path]:
                            self.words[file_path][word]=self.words[file_path][word]+1

                        else:
                             self.words[file_path][word]=1
                    else:

                        if word!='' and word not in self.stops:
                            word=ps.stem(word)
                            if word in self.words[file_path]:
                                self.words[file_path][word]=self.words[file_path][word]+1
                            else:
                                self.words[file_path][word]=1

                    word=''
        f.close()

    def creaza_index_invers(self):
        index_invers={}

        with open('indexDirect.json') as input:
             d = json.load(input)

        for  k1,v1 in d.items():
            for k2,v2 in v1.items():
                if k2 not in index_invers.keys():
                    index_invers[k2] = {}
                    index_invers[k2][k1]=v2
                else:
                    index_invers[k2][k1] = v2

        self.inverted_index=index_invers

        with open('indexInvers.json', 'w') as scrieJson2:
            json.dump(index_invers, scrieJson2, indent=10)


    def read_files(self):

        self.read_stopwords_and_exceptions(exceptions_words_path, self.exceptions)
        self.read_stopwords_and_exceptions(stop_words_path, self.stops)

        for dir in self.directories:
            for f in os.listdir(os.path.join(self.dirPath,dir)):

                if os.path.isdir(os.path.join(dir,f)):
                  self.directories.append(os.path.join(dir,f))

                elif os.path.isfile(os.path.join(dir,f)):
                    key=os.path.join(dir,f)
                    self.creeaza_index_direct(key)

        with open('indexDirect.json', 'w') as scrieJson1:
            json.dump(self.words, scrieJson1,indent=10)


    def scrie_index_direct(self):
        w = f = open("Output.txt", 'w')
        for k1,v1 in self.words.items():
            w.write(k1)
            w.write(":\n\n")
            for k2,v2 in v1.items():
                w.write(k2)
                w.write("----->")
                w.write(str(v2))
                w.write("\n")
        w.close()


    def cautare_booleana(self,input):
        operatori=[]
        operanzi=[]
        rez=[]
        word=''
        for l in input:
            l=l.lower()
            if l =='&' or l=='|' or l=='!':
                operatori.append(l)
                if word in self.exceptions:
                    operanzi.append(word)
                else:
                    if word not in self.stops:
                        word=ps.stem(word)
                        operanzi.append(word)
                word=''

            if l !='&' and l!='|' and l!='!':
                if l >= 'a' and l <= 'z' or l >= '0' and l <= '9':
                    word=word+l
                else:
                    print("Secventa de intrare nu este corecta")
                    continue

        if word in self.exceptions:
            operanzi.append(word)
        else:
            if word not in self.stops:
                word = ps.stem(word)
                operanzi.append(word)

        print(operatori)
        print(operanzi)

        try:
            files0 = set(self.inverted_index[operanzi[0]])

        except:
            print("Error:Key #", operanzi[0], "# nu exista in fisiere")

        for i in range(1,len(operanzi)):
            try:
                filesI=set(self.inverted_index[operanzi[i]])
            except:
                print("Error:Key #"+operanzi[i]+"# nu exista in fisiere")

            if(i==1):
                if(operatori[0]=='|'):
                    rez=files0.union(filesI)
                if(operatori[0]=='!'):
                    rez=files0.difference(filesI)
                if(operatori[0]=='&'):
                    rez=files0.intersection(filesI)
            else:
                if(operatori[i-1]=='|'):
                    rez=rez.union(filesI)
                if(operatori[i-1]=='!'):
                    rez=rez.difference(filesI)
                if(operatori[i-1]=='&'):
                    rez=rez.intersection(filesI)
        print(rez)



def main():
############ 1 #################
     tp=myTextParser(files_path)

############ 2 #################
     tp.creaza_index_invers()


     key1='hunger!game&part&joc'
     key2='hunger|games&jm)n)'
     key3='hunger&games&all'

############ 3 ################
     tp.cautare_booleana(key1)


if __name__=='__main__':
    main()
