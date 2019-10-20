import requests
import xml.etree.ElementTree as ET
import re
import sys, os
import time, nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
sys.path.append('../Utils')
from Utils.minEditDist import minEditDist
class PubMedParser:
    path = 'PubmedArticle/MedlineCitation/Article'
    index = dict()
    ps = PorterStemmer()
    def __init__(self, fileContent):
        self.tree = ET.fromstring(fileContent)
        self.allArticle = self.getAllArticle(self.tree)
        self.allTitles ,self.allTiles_stem= self.parsingTitle(self.allArticle)
        self.allContents, self.allContents_stem, self.numOfWords, self.numOfWords_stem, self.numOfCharacters , self.numOfCharacters_stem= self.parsingContent(self.allArticle)
        self.allAuthorName = self.parsingAuthors(self.allArticle)
        # self.title_content_dictionary  = dict(zip(self.allTitles, self.allContents))
        # self.title_author_dictionary = dict(zip(self.allTitles, self.allAuthorName))
        # self.title_numOfWords_dictionary = dict(zip(self.allTitles, self.numOfWords))
        # self.title_numOfCharacters_dictionary = dict(zip(self.allTitles, self.numOfCharacters))
        self.sortIndex()
        
    def getAllArticle(self,root):
        article = root.findall(self.path)
        return article

    def sortIndex(self):
        for key, value in self.index.items():
            temp = sorted(value)
            temp = list(dict.fromkeys(temp))
            self.index[key] = temp

    def createIndex(self, string, num):
        extract = re.findall(r'\w+', string, re.IGNORECASE) 
        for word in extract:
            word = word.lower()
            if(word in self.index):
                self.index[word].append(num)
            else:
                self.index[word] = [num]

    def parsingContent(self,allArticle):
        content = []
        content_stem = []
        numOfWords = []
        numOfWords_stem = []
        numOfCharacters = []
        numOfCharacters_stem = []
        for article in allArticle:
            abstract = article.find('Abstract')
            if(abstract == None):
                content.append('')
                content_stem.append('')
                numOfWords.append(0)
                numOfWords_stem.append(0)
                numOfCharacters.append(0)
                numOfCharacters_stem.append(0)
            else:
                abstractText = abstract.findall('AbstractText')
                if(abstractText == None):
                    content.append('')
                    content_stem.append('')
                    numOfWords.append(0)
                    numOfWords_stem.append(0)
                    numOfCharacters.append(0)
                    numOfCharacters_stem.append(0)
                else:
                    s = ''
                    _s = ''
                    words = 0
                    words_stem = 0
                    chars = 0
                    chars_stem = 0
                    for text in abstractText:
                        fullText = ''.join(text.itertext())
                        self.createIndex(fullText, len(content))
                        words += len(re.findall(r'\w+', fullText))
                        words_stem += len(re.findall(r'\w+',self.stemming(fullText)))
                        chars += len(re.findall(r'\S', fullText))
                        chars_stem += len(re.findall(r'\S', self.stemming(fullText)))
                        if 'Label' in text.attrib:
                            s+='<b>'+text.attrib['Label']+'</b>'+':<br>&nbsp&nbsp&nbsp&nbsp'+fullText+' <br>'
                            _s+='<b>'+self.stemming(text.attrib['Label'])+'</b>'+':<br>&nbsp&nbsp&nbsp&nbsp'+self.stemming(fullText)+' <br>'
                        else:
                            s+=' '+'<br>&nbsp&nbsp&nbsp'+fullText
                            _s+=' '+'<br>&nbsp&nbsp&nbsp'+self.stemming(fullText)
                    numOfWords.append(words)
                    numOfWords_stem.append(words_stem)
                    numOfCharacters.append(chars)
                    numOfCharacters_stem.append(chars_stem)
                    content.append(s)
                    content_stem.append(_s)
        # print(content_stem)
        return content, content_stem, numOfWords, numOfWords_stem, numOfCharacters, numOfCharacters_stem

    def parsingTitle(self,allArticle):
        title = []
        title_stem = []
        for article in allArticle:
            articleTitle = article.find('ArticleTitle')
            if(articleTitle == None or articleTitle.text == None):
                title.append('')
                title_stem.append('')
            else:
                self.createIndex(str(articleTitle.text), len(title))
                title.append(articleTitle.text)
                title_stem.append(self.stemming(articleTitle.text))
        return title, title_stem

    def parsingAuthors(self,allArticle):
        result = []
        for article in allArticle:
            authorList = article.find('AuthorList')
            if(authorList == None):
                result.append('')
            else:
                authors = authorList.findall('Author')
                if(authors == None):
                    result.append('')
                else:
                    names = []
                    for author in authors:
                        string1 = '' if author.find("ForeName")==None else author.find('ForeName').text
                        string2 = '' if author.find("LastName")==None else author.find('LastName').text
                        names.append(string1.replace(" ",'') + " " + string2)
                    result.append(names)
        return result
    def mark_content(self,position, string):
        for num, tup in enumerate(position):
            string = string[:tup[0] + num*23] + self.color.RED_START + string[tup[0] + num*23:tup[1] + num*23] + self.color.END + string[tup[1] + num*23:]
        return string

    def match(self, query, cal_dist_flag):
        titles = list()
        titles_stem = list()
        contents = list()
        contents_stem = list()
        authors = list()
        numOfCharacters = list()
        numOfCharacters_stem = list()
        numOfWords = list()
        numOfWords_stem = list()
        union = list()
        edit = [0, query]
        if(cal_dist_flag == '1'):
            temp, correct= minEditDist(query, self.index)
            edit = [temp, correct]
            query = temp
            # if(minDist == 0):
            #     edit = [correct, query]
            # elif(minDist > 0 and minDist < 5):
            #     edit = [correct, temp]
            #     query = temp
        start_time = time.time()
        query = query.split(' ')
        query_string = ''
        query_string_stem = ''
        for q in query:
            query_string += '(' + q + ')|'
            query_string_stem += '(' + self.stemming(q) + ')|'
        query_string = query_string[:-1]
        query_string_stem = query_string_stem[:-1]
        for q in query:
            try:
                union = list(set(union) | set(self.index[q.lower()]))
            except KeyError as e:
                print(e)
        words_times_pair , word_stem_times_pair= (self.countAllWordsTimes(union))
                
        for i in union:
            titleIterator = re.finditer(query_string, self.allTitles[i], re.IGNORECASE)
            titleStemIterator = re.finditer(query_string_stem, self.allTiles_stem[i], re.IGNORECASE)
            contentIterator = re.finditer(query_string, self.allContents[i], re.IGNORECASE)
            contentStemIterator = re.finditer(query_string_stem, self.allContents_stem[i], re.IGNORECASE)

            queryPosInTitle = [(m.start(), m.end()) for m in titleIterator]
            queryPosInContent = [(m.start(), m.end()) for m in contentIterator]
            queryPosInTitle_stem = [(m.start(), m.end()) for m in titleStemIterator]
            queryPosInContent_stem = [(m.start(), m.end()) for m in contentStemIterator]
            if(queryPosInTitle or queryPosInContent):
                titles.append(self.allTitles[i])
                titles_stem.append(self.allTiles_stem[i])
                numOfWords.append(self.numOfWords[i])
                numOfWords_stem.append(self.numOfWords_stem[i])
                numOfCharacters.append(self.numOfCharacters[i])
                numOfCharacters_stem.append(self.numOfCharacters_stem[i])
                # allWordsTimes = self.countAllWordsTimes(self.allContents[i], allWordsTimes)
                contents.append(self.mark_content(queryPosInContent, self.allContents[i]))
                contents_stem.append(self.mark_content(queryPosInContent_stem, self.allContents_stem[i]))
                authors.append(','.join(self.allAuthorName[i]))
        comm = []
        for i, content in enumerate(contents):
            for j in range(len(query)):
                if(len(re.findall(query[j], content, re.IGNORECASE))):
                    if(j+1 == len(query)):
                        comm.append(i)
                else:
                    break
        end_time = time.time() - start_time
        print(end_time)
        return titles, titles_stem, contents , contents_stem, authors, numOfWords, numOfWords_stem, numOfCharacters, numOfCharacters_stem, comm, words_times_pair, word_stem_times_pair,edit

    def stemming(self, string):
        words = word_tokenize(string)
        reslut = list()
        for word in words:
            reslut.append(self.ps.stem(word))
        return ' '.join(reslut)

    def countAllWordsTimes(self, union):
        words_times_dict = dict()
        words_stem_times_dict = dict()
        tags = ['<br>', '</br>', '&nbsp', '<b>', '</b>']
        for i in union:
            content = self.allContents[i]
            content_stem = self.allContents_stem[i]
            for tag in tags:
                content = content.replace(tag, '')
                content_stem = content_stem.replace(tag, '')
            extract = re.findall(r'\w+', str(content))
            extract_stem = re.findall(r'\w+', str(content_stem))
            for word in extract:
                word = word.lower()
                count = words_times_dict.get(word, 0)
                words_times_dict[word] = count + 1
            for word in extract_stem:
                word = word.lower()
                count = words_stem_times_dict.get(word, 0)
                words_stem_times_dict[word] = count + 1
        return self.separate_dict_sort(words_times_dict), self.separate_dict_sort(words_stem_times_dict)
    #sort dict by value and turn to list
    def separate_dict_sort(self,words_times_dict):
        pairs = list(words_times_dict.items())
        pairs.sort(key = lambda tup:tup[1], reverse=True)
        return pairs

    class color:
        RED_START = '<font color=red>'
        BULE_START = '<font color=blue>'
        GRAY_START = '<font color=gray>'
        END = '</font>'
        BOLD = '<b>'
        BOLD_END = '</b>'
        UNDERLINE = '<u>'
        UNDERLINE_END = '</u>'