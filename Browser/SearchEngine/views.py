from django.shortcuts import render
from django.http import JsonResponse

import sys, os
sys.path.append(os.path.abspath(os.path.join('../')))
from Tiwtter_Crawler.TwitterParser import TwitterParser
from PubMed_WebCrawler.main import PubMedParser
import re

EOSPattern = '(?<!\w\.\w.)(?<!\d\d\.)(?<=\.|\?)\s(?!(\d\.){2})'
wordPattern = '\w+'
characterPattern = '\S'
tp = None
pmp = None
# Create your views here.


def index(request):
    return render(request, 'SearchEngine/index.html')

def upload(request):
    if(request.method == 'POST'):
        file_name = request.POST['file_name']
        contents = request.POST['contents']
        if (file_name.split('.')[1] == 'xml') :
            global pmp
            pmp = PubMedParser(contents)
        else:
            global tp
            tp = TwitterParser(contents)
    return JsonResponse({'success':'success'})

def PubMedSearch(request):
    print("searching")
    if(request.method == 'GET'):
        query = request.GET['query']
        titles, contents, authors , numOfWords, numOfCharacters, comm = pmp.match(query)
        numOfSentence ,contents = countNumOfSentence(contents)
        return JsonResponse({'titles' : titles, 'contents' : contents, 'authors' : authors, 
                            'numOfWords' : numOfWords, 'numOfChars' : numOfCharacters,
                            'numOfSentence' : numOfSentence, 'comm' : comm})

def TwitterSearch(request):
    print('searching')
    if(request.method == 'GET'):
        query = request.GET['query']
        texts, user_names,screen_names ,created_ats, numOfWords, numOfCharacters = tp.match(query)
        # print(texts, user_names, created_ats)
        return JsonResponse({'texts' : texts, 'user_names' : user_names,'screen_names' : screen_names, 
                            'created_ats' : created_ats, 'numOfWords' : numOfWords, 'numOfChars' : numOfCharacters})

#method
def countNumOfWords(contents):
    numOfWords = []
    for content in contents:
        numOfWords.append(len(re.findall(wordPattern, content)))
    return numOfWords

def countNumOfCharacters(contents):
    numOfCharacters = []
    for content in contents:
        numOfCharacters.append(len(re.findall(characterPattern, content)))
    return numOfCharacters

def countNumOfSentence(contents):
    numOfSentence = []
    for num, content in enumerate(contents):
        content = content + " "
        iterator = re.finditer(EOSPattern, content)
        EOSPatternPosition = [(m.start(), m.end()) for m in iterator]
        if(EOSPatternPosition):
            contents[num] = mark_EOS(EOSPatternPosition, content)
            numOfSentence.append(len(EOSPatternPosition))
        else:
            numOfSentence.append('0')
    return numOfSentence, contents
def mark_EOS(position, content):
    for num , pos in enumerate(position):
        content = content[:pos[0] + num*50] + '<span style="background-color:#8bdaf7">&nbsp</span>' + content[pos[1] + num*50:]
    return content
    