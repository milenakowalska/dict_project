from bs4 import BeautifulSoup  
import requests
from dataclasses import dataclass


@dataclass
class Word:
    key: str
    translations: str
    context: str = None

@dataclass
class Example:
    example: str
    translation_example: str = None


class DictionaryParser:
    @staticmethod
    def find_definition(language_from, language_to, word):
        '''Finds word definitions on a Website'''
        raise Exception("NotImplementedException")

languages = {'francais':['fr','fre'], 'russe':['ru','rus'], 'espagnol':['es','esp'],'polonais':['pl','pol'], 'italien':['it','ita'], 'allemand':['de','ger'], 'anglais':['en','eng'],'portugais':['pt','por'],'chiois':['zh','chi']}

class WordreferenceParser(DictionaryParser):
    """Searches word definition in wordreference.com"""
    dictionary_string = 'wordreference'
    @staticmethod
    def find_definition(language_from, language_to, word):
        language_from = languages[language_from][0]
        language_to = languages[language_to][0]
        source = requests.get(f'https://www.wordreference.com/{language_from}{language_to}/{word}').text

        soup = BeautifulSoup(source, 'lxml').body
        list_of_words = []
        list_of_examples = []

        tables = soup.find_all("table", class_='WRD')
        current_class = ['odd']

        list_of_translations = []
        key = None
        example = None
        translation_example = None
        context = None

        for table in tables:
            next_position = table.find_all('tr')
            for tr in next_position:
                if tr['class'] == ['even'] or tr['class'] == ['odd']:
                    if tr['class'] != current_class:
                        if key:
                            next_word = Word(key=key, translations=', '.join(list_of_translations), context=context)
                            list_of_words.append(next_word)
                            list_of_translations = []
                            key = None
                            context = None

                        if example:
                            list_of_examples.append(Example(example, translation_example))
                            example = None
                            translation_example = None

                        current_class = tr['class']
                        key = tr.find('td', class_='FrWrd').strong.text

                        if (tr.find('td', class_=None)) is not None:
                            context = tr.find('td', class_=None).text
                            
                        if (translation := tr.find('td', class_='ToWrd')) is not None:
                            list_of_translations.append(translation.find(text=True,recursive=False))
                    
                    else:
                        if (translation := tr.find('td', class_='ToWrd')) is not None:
                            list_of_translations.append(translation.find(text=True,recursive=False))

                        if (tr.find('td', class_='FrEx')) is not None:
                            example = tr.find('td', class_='FrEx').text
                        
                        if (tr.find('td', class_='ToEx')) is not None:
                            translation_example = tr.find('td', class_='ToEx').text

        return [list_of_words, list_of_examples]

class DictionnaireParser(DictionaryParser):
    """Searches word definition in dictionnaire.reverso.net"""
    dictionary_string = 'dictionnaire'
    @staticmethod
    def find_definition(language_from, language_to, word):
        source = requests.get(f'https://dictionnaire.reverso.net/{language_from}-{language_to}/{word}', headers={'User-Agent': 'Mozilla/5.0'}).text

        soup = BeautifulSoup(source, 'lxml').body
        list_of_words = []
        list_of_examples = []
        
        for div in soup.find('form').find_all('tr', valign='top'):

            key = div.find('td', class_='CDResSource').find('span', class_='ellipsis_text').text
            translation = div.find('td', class_='CDResTarget').find('span', class_='ellipsis_text').text
            if word in translation:
                key, translation = translation, key
            list_of_words.append(Word(key, translation))

        if (examples := soup.find('table', class_='contextlist')) is not None:

            for tr in examples.find_all('tr'):
                if tr.find('td', class_='src') is not None:
                    translation = tr.find('td', class_='src').text
                    example = tr.find('td', class_='tgt').text
                    list_of_examples.append(Example(example, translation))
            for tr in examples.find_all('tr'):
                if tr.find('td', class_='transName') is not None:
                    key = word
                    translation = tr.find('span', id='translationName')
                    if 'notrans' in translation.get_attribute_list('class'):
                        break
                    else:
                        translation = translation.text
                    list_of_words.append(Word(key, translation))

        if (new := soup.find('div', class_='translate_box0')) is not None:

            if (translations := new.find_all('span', direction='targettarget')) is not None:
                for translation in translations:
                    if (context := translation.findNext('span')) is not None:
                        if "(" in context.text:
                            list_of_words.append(Word(word, translation.text, context.text))
                        elif "(" in context.findNext('span').text:
                            list_of_words.append(Word(word, translation.text, context.findNext('span').text))
                    else:
                        list_of_words.append(Word(word, translation.text))

            if (examples := new.find_all('span', direction='')) is not None:
                for example in examples:
                    if example is not None and len(example.text) > 0:
                        if str(example.text)[0] == '→':
                            list_of_examples.append(Example(example.text, ''))
            
        return [list_of_words, list_of_examples]
