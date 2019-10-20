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
    print("read")
    if(request.method == 'POST'):
        file_name = request.POST['file_name']
        contents = request.POST['contents']
        if (file_name.split('.')[1] == 'xml') :
            global pmp
            pmp = PubMedParser(contents)
        else:
            global tp
            tp = TwitterParser(contents)
    else:
        print('doesnt read')
    return JsonResponse({'success':'success'})

def PubMedSearch(request):
    print("searching")
    if(request.method == 'GET'):
        query = request.GET['query']
        flag = request.GET['flag']
        titles, titles_stem, contents , contents_stem, authors, numOfWords, numOfWords_stem, numOfCharacters, numOfCharacters_stem, comm, words_times_pair, word_stem_times_pair, edit = pmp.match(query, flag)
        numOfSentence, numOfSentence_stem, contents, contents_stem= countNumOfSentence(contents,contents_stem)
        return JsonResponse({'titles' : titles, 'titles_stem' : titles_stem, 'contents' : contents, 'contents_stem' : contents_stem,'authors' : authors, 
                            'numOfWords' : numOfWords, 'numOfWords_stem' : numOfWords_stem, 'numOfChars' : numOfCharacters, 'numOfChars_stem' : numOfCharacters_stem,
                            'numOfSentence' : numOfSentence, 'numOfSentence_stem' : numOfSentence_stem, 'comm' : comm, 'pair' : words_times_pair, 
                            'pair_stem' : word_stem_times_pair, 'edit' : edit})

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

def countNumOfSentence(contents, contents_stem):
    numOfSentence = []
    numOfSentence_stem = []
    for num, content in enumerate(contents):
        content = content + " "
        iterator = re.finditer(EOSPattern, content)
        EOSPatternPosition = [(m.start(), m.end()) for m in iterator]
        if(EOSPatternPosition):
            contents[num] = mark_EOS(EOSPatternPosition, content)
            numOfSentence.append(len(EOSPatternPosition))
        else:
            numOfSentence.append('0')

    for num, content_stem in enumerate(contents_stem):
        content_stem = content_stem + " "
        iterator = re.finditer(EOSPattern, content_stem)
        EOSPatternPosition = [(m.start(), m.end()) for m in iterator]
        if(EOSPatternPosition):
            contents_stem[num] = mark_EOS(EOSPatternPosition, content_stem)
            numOfSentence_stem.append(len(EOSPatternPosition))
        else:
            numOfSentence_stem.append('0')
    return numOfSentence, numOfSentence_stem, contents, contents_stem
def mark_EOS(position, content):
    for num , pos in enumerate(position):
        content = content[:pos[0] + num*50] + '<span style="background-color:#8bdaf7">&nbsp</span>' + content[pos[1] + num*50:]
    return content
    