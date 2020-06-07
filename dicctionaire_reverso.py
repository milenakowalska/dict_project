from bs4 import BeautifulSoup  
import requests
from collections import namedtuple

Word = namedtuple('Word',['key','translation'])
Example = namedtuple('Example',['example','translation'])

def find_definition(language_from, language_to, word):
    list_with_words = []
    list_of_examples = []

    source = requests.get(f'https://dictionnaire.reverso.net/{language_from}-{language_to}/{word}', headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(source, 'lxml').body.find('form')

    for div in soup.find_all('tr', valign='top'):

        key = div.find('td', class_='CDResSource').find('span', class_='ellipsis_text').text
        translation = div.find('td', class_='CDResTarget').find('span', class_='ellipsis_text').text
        if word in translation:
            key, translation = translation, key
        list_with_words.append(Word(key, translation))

    if (examples := soup.find('table', class_='contextlist')) is not None:

        for tr in examples.find_all('tr'):
            if (translation := tr.find('td', class_='src').text) is not None:
                example = tr.find('td', class_='tgt').text
                list_of_examples.append(Example(example, translation))

    new = soup.find('div', class_='translate_box0')

    if (translations := new.find_all('span', direction='targettarget')) is not None:
        for translation in translations:
            list_with_words.append(Word(word, translation.text))

    if (examples := new.find_all('span', direction='')) is not None:
        for example in examples:
            if example is not None and len(example.text) > 0:
                if str(example.text)[0] == '→':
                    list_of_examples.append(Example(example.text, ''))

    return [list_with_words, list_of_examples]

print('\n\ndefinitions:\n')
for word in find_definition('francais', 'anglais','remplir')[0]:
    print(word.key, ' - ', word.translation)
print('\n\nexamples:\n')
for example in find_definition('francais', 'anglais','remplir')[1]:
    print(example.example, ' \n -  ', example.translation)

