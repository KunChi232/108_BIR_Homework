import os, sys
import json
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
sys.path.append('../Utils')
from Utils.minEditDist import minEditDist
class TwitterParser:
    index = dict()
    ps = PorterStemmer()

    def __init__(self, fileContent):
        self.jsonFiles = json.loads(fileContent)
        self.createIndex(self.jsonFiles)
        self.sortIndex()
        # print(self.index)
    
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
        
    def stemming(self, string):
        words = word_tokenize(string)
        result = list()
        for word in words:
            result.append(self.ps.stem(word))
        return ' '.join(result)

    def countAllWordsTime(self, union):
        words_times_dict = dict()
        words_stem_times_dict = dict()

        for i in union:
            text = self.jsonFiles[i]['text']
            text_stem = self.stemming(text)
            extract = re.findall(r'\w+', str(text))
            extract_stem = re.findall(r'\w+', str(text_stem))
            for word in extract:
                word = word.lower()
                count = words_times_dict.get(word, 0)
                words_times_dict[word] = count + 1
            for word in extract_stem:
                word = word.lower()
                count = words_stem_times_dict.get(word, 0)
                words_stem_times_dict[word] = count + 1
        return words_times_dict, words_stem_times_dict
    def match(self, query):
        texts = list()
        texts_stem = list()
        user_names = list()
        screen_names = list()
        created_ats = list()
        numOfCharacters = list()
        numOfCharacters_stem = list()
        numOfWords = list()
        numOfWords_stem = list()
        union = list()


        query_string = ''
        query_string_stem = ''
        for q in query.split(' '):
            query_string += '(?<!(#\s))(?<!(%23))('+q+')|'
            query_string_stem += '(?<!(#\s))(?<!(%23))('+self.stemming(q)+')|'
        query_string = query_string[:-1]
        query_string_stem = query_string_stem[:-1]
        print(query_string_stem)
        print(query_string)
        for q in query.split(' '):
            try:
                union = list(set(union) | set(self.index[q.lower()]))
            except KeyError as e:
                print(e)
        words_times_dict, words_stem_times_dict = self.countAllWordsTime(union)
        for i in union:
            text = self.jsonFiles[i]['text']
            text_stem = self.stemming(text)
            # print(text)
            # print(text_stem)

            numOfWords.append(len(re.findall(r'\w+', text)))
            numOfWords_stem.append(len(re.findall(r'\w+', text_stem)))
            numOfCharacters.append(len(re.findall(r'\S',text)))
            numOfCharacters_stem.append(len(re.findall(r'\S', text_stem)))
            
            iterTag = re.findall('(#[a-z\d-]+|# [a-z\d-]+)', text, re.IGNORECASE)
            iterTag_stem = re.findall('(#[a-z\d-]+|# [a-z\d-]+)', text_stem, re.IGNORECASE)
            if(iterTag):
                text = self.mark_hashtag(iterTag, text)
            if(iterTag_stem):
                text_stem = self.mark_hashtag(iterTag_stem, text_stem)
            # print(text_stem)

            iterText = re.finditer(query_string, text, re.IGNORECASE)
            iterText_stem = re.finditer(query_string_stem, text_stem, re.IGNORECASE)
            position = [(m.start(), m.end()) for m in iterText]
            position_stem = [(m.start(), m.end()) for m in iterText_stem]
            if(position):
                texts.append(self.mark_content(position, text))
                user_names.append(self.jsonFiles[i]['author_id'])
                screen_names.append('@')
                created_ats.append(self.jsonFiles[i]['formatted_date'].replace('+0000', ''))
            if(position_stem):
                texts_stem.append(self.mark_content(position_stem, text_stem))
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
        return texts, texts_stem, user_names, screen_names,created_ats, numOfWords, numOfWords_stem, numOfCharacters, numOfCharacters_stem

    class color:
        RED_START = '<font color=red>'  
        BULE_START = '<font color=blue>'
        GRAY_START = '<font color=gray>'
        END = '</font>'
        BOLD = '<b>'
        BOLD_END = '</b>'
        UNDERLINE = '<u>'
        UNDERLINE_END = '</u>'


                