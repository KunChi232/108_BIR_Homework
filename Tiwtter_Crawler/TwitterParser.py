import os
import json
import re
class TwitterParser:
    index = dict()
    def __init__(self, fileContent):
        self.jsonFiles = json.loads(fileContent)
        self.createIndex(self.jsonFiles)
        self.sortIndex()
        print(self.index)
    
    def createIndex(self, jsonFiles):
        num = 0
        for tweet in jsonFiles:
            if('text' in tweet):
                text = tweet['text']
                extarct = re.findall(r'\w+', text, re.IGNORECASE)
                for word in extarct:
                    word = word.lower()
                    if(word in self.index):
                        self.index[word].append(num)
                    else:
                        self.index[word] = [num]
            num += 1

    def sortIndex(self):
        for key, value in self.index.items():
            temp = sorted(value)
            temp = list(dict.fromkeys(temp))
            self.index[key] = temp

    def mark_content(self, position, string):
        for num, tup in enumerate(position):
            string = string[:tup[0] + num*23] + self.color.RED_START + string[tup[0] + num*23:tup[1] + num*23] + self.color.END + string[tup[1] + num*23:]
        return string

    def mark_hashtag(self, tags, string):
        for tag in tags:
            key = tag.split(' ')[1]
            string = string.replace(tag,'<a href=https://twitter.com/search?q=%23'+key+'&src=typd>'+tag+'</a>')
        return string

    def match(self, query):
        query_string = ''
        for q in query.split(' '):
            query_string += '(?<!(#\s))(?<!(%23))('+q+')|'
        query_string = query_string[:-1]
        texts = list()
        user_names = list()
        screen_names = list()
        created_ats = list()
        numOfCharacters = list()
        numOfWords = list()
        union = list()

        for q in query.split(' '):
            try:
                union = list(set(union) | set(self.index[q.lower()]))
            except KeyError as e:
                print(e)
        
        for i in union:
            text = self.jsonFiles[i]['text']
            print(text)
            numOfWords.append(len(re.findall(r'\w+', text)))
            numOfCharacters.append(len(re.findall(r'\S',text)))
            iterTag = re.findall('(#[a-z\d-]+|# [a-z\d-]+)', text, re.IGNORECASE)
            if(iterTag):
                text = self.mark_hashtag(iterTag, text)
            
            iterText = re.finditer(query_string, text, re.IGNORECASE)
            position = [(m.start(), m.end()) for m in iterText]
            if(position):
                texts.append(self.mark_content(position, text))
                user_names.append(self.jsonFiles[i]['author_id'])
                screen_names.append('@')
                created_ats.append(self.jsonFiles[i]['formatted_date'].replace('+0000', ''))
        # for tweet in self.jsonFiles:
        #     if('text' in tweet):
        #         text = tweet['text']
        #         numOfWords.append(len(re.findall('\w+', text)))
        #         numOfCharacters.append(len(re.findall('\S', text)))
        #         iterTag = re.findall('(#[a-z\d-]+|# [a-z\d-]+)', text, re.IGNORECASE)
        #         if(iterTag):
        #             text = self.mark_hashtag(iterTag, text)
        #         iterator = re.finditer(query_string, text, re.IGNORECASE)
        #         position = [(m.start(), m.end()) for m in iterator]
        #         if(position):
        #             texts.append(self.mark_content(position, text))
        #             user_names.append(tweet['author_id'])
        #             screen_names.append('@')
        #             created_ats.append(tweet['formatted_date'].replace('+0000 ',''))
        return texts, user_names, screen_names,created_ats, numOfWords, numOfCharacters

    class color:
        RED_START = '<font color=red>'  
        BULE_START = '<font color=blue>'
        GRAY_START = '<font color=gray>'
        END = '</font>'
        BOLD = '<b>'
        BOLD_END = '</b>'
        UNDERLINE = '<u>'
        UNDERLINE_END = '</u>'


                