import requests
import xml.etree.ElementTree as ET
import re
import sys, os
import time
class PubMedParser:
    path = 'PubmedArticle/MedlineCitation/Article'
    index = dict()
    def __init__(self, fileContent):
        self.tree = ET.fromstring(fileContent)
        self.allArticle = self.getAllArticle(self.tree)
        self.allTitles = self.parsingTitle(self.allArticle)
        self.allContents, self.numOfWords, self.numOfCharacters = self.parsingContent(self.allArticle)
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
        result = []
        numOfWords = []
        numOfCharacters = []
        for article in allArticle:
            abstract = article.find('Abstract')
            if(abstract == None):
                result.append('')
                numOfWords.append(0)
                numOfCharacters.append(0)
            else:
                abstractText = abstract.findall('AbstractText')
                if(abstractText == None):
                    numOfWords.append(0)
                    numOfCharacters.append(0)
                    result.append('')
                else:
                    s = ''
                    words = 0
                    chars = 0
                    for text in abstractText:
                        self.createIndex(''.join(text.itertext()), len(result))
                        words += len(re.findall(r'\w+',''.join(text.itertext())))
                        chars += len(re.findall(r'\S',''.join(text.itertext())))
                        if 'Label' in text.attrib:
                            s+='<b>'+text.attrib['Label']+'</b>'+':<br>&nbsp&nbsp&nbsp&nbsp'+''.join(text.itertext())+' <br>'
                        else:
                            s+=' '+'<br>&nbsp&nbsp&nbsp'+''.join(text.itertext())+'\n'
                    numOfWords.append(words)
                    numOfCharacters.append(chars)
                    result.append(s)
        return result, numOfWords, numOfCharacters

    def parsingTitle(self,allArticle):
        result = []
        for article in allArticle:
            articleTitle = article.find('ArticleTitle')
            if(articleTitle == None or articleTitle.text == None):
                result.append('')
            else:
                self.createIndex(str(articleTitle.text), len(result))
                result.append(articleTitle.text)
        return result

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

    def match(self,query):
        start_time = time.time()
        query = query.split(' ')
        query_string = ''
        for q in query:
            query_string += '(' + q + ')|'
        query_string = query_string[:-1]
        titles = []
        contents = []
        authors = []
        numOfCharacters = []
        numOfWords = []
        # for key, value in self.title_content_dictionary.items():
        #     titleIterator = re.finditer(query_string, str(key), re.IGNORECASE)
        #     contentIterator = re.finditer(query_string, value, re.IGNORECASE)
        #     queryPosInTitle = [(m.start(), m.end()) for m in titleIterator]
        #     queryPosInContent = [(m.start(), m.end()) for m in contentIterator]
        #     if(queryPosInTitle or queryPosInContent):
        #         titles.append(key)
        #         numOfWords.append(self.title_numOfWords_dictionary[key])
        #         numOfCharacters.append(self.title_numOfCharacters_dictionary[key])
        #         contents.append(self.mark_content(queryPosInContent, value))
        #         authors.append(','.join(self.title_author_dictionary[key]))
        union = list()
        for q in query:
            union = list(set(union) | set(self.index[q]))
        for i in union:
            titleIterator = re.finditer(query_string, self.allTitles[i], re.IGNORECASE)
            contentIterator = re.finditer(query_string, self.allContents[i], re.IGNORECASE)
            queryPosInTitle = [(m.start(), m.end()) for m in titleIterator]
            queryPosInContent = [(m.start(), m.end()) for m in contentIterator]
            if(queryPosInTitle or queryPosInContent):
                titles.append(self.allTitles[i])
                numOfWords.append(self.numOfWords[i])
                numOfCharacters.append(self.numOfCharacters[i])
                contents.append(self.mark_content(queryPosInContent, self.allContents[i]))
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
        return titles, contents ,authors, numOfWords, numOfCharacters, comm

    def countNumOfWords(self,contents):
        numOfWords = []
        for content in contents:
            numOfWords.append(len(re.findall(wordPattern, content)))
        return numOfWords

    def countNumOfCharacters(self,contents):
        numOfCharacters = []
        for content in contents:
            numOfCharacters.append(len(re.findall(characterPattern, content)))
        return numOfCharacters

    class color:
        RED_START = '<font color=red>'
        BULE_START = '<font color=blue>'
        GRAY_START = '<font color=gray>'
        END = '</font>'
        BOLD = '<b>'
        BOLD_END = '</b>'
        UNDERLINE = '<u>'
        UNDERLINE_END = '</u>'