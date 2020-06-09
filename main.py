from bs4 import BeautifulSoup  
import requests
from collections import namedtuple
from lxml import etree
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

def find_definition(dictionary: str, language_from: str, language_to: str, word: str) -> list:
    '''Find word definitions in specified dictionary'''

    languages = {'francais':'fr', 'polonais':'pl', 'italien':'it', 'allemand':'de', 'anglais':'en','portugais':'pt','chinois':'zh'}
    
    if dictionary == 'wordreference':
        language_from = languages[language_from]
        language_to = languages[language_to]
        source = requests.get(f'https://www.wordreference.com/{language_from}{language_to}/{word}').text

    if dictionary == 'dictionnaire':
        source = requests.get(f'https://dictionnaire.reverso.net/{language_from}-{language_to}/{word}', headers={'User-Agent': 'Mozilla/5.0'}).text

    soup = BeautifulSoup(source, 'lxml').body
    list_of_words = []
    list_of_examples = []

    if dictionary == 'wordreference':
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

    if dictionary == 'dictionnaire':
        
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


def check_word(dictionary: str, language_from: str, language_to: str, word: str) -> list:
    if dictionary == 'wordreference':
        current_dictionary = 'dict_wordreference.xdxf'
    if dictionary == 'dictionnaire':
        current_dictionary = 'dict_dictionnaire.xdxf'

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(current_dictionary, parser)
    root = tree.getroot()

    results = [[],[]]
    for element in tree.iter('ar'):
        if element.get('key') == word and element.get('lang_from') == language_from and element.get('lang_to') == language_to:
            key, translation, context, translation_example, example = '','','','',''
            for tag in element.iter():
                if tag.tag == 'k':
                    key = tag.text
                elif tag.tag == 'span':
                    translation = tag.text
                elif tag.tag == 'context':
                    context = tag.text
                elif tag.tag == 'trans':
                    translation_example = tag.text
                elif tag.tag == 'ex':
                    example = tag.text
                elif tag.tag == 'hr':
                    if key != '' and translation != '':
                        results[0].append(Word(key, translation, context))
                    if example != '':
                        results[1].append(Example(example, translation_example))
                    key, translation, definition, example = '','','',''

    if results == [[],[]]:    
        results = find_definition(dictionary, language_from, language_to, word)

        ar = etree.SubElement(root[1], 'ar')
        ar.set('key',word)
        ar.set('lang_from', language_from)
        ar.set('lang_to', language_to)

        for definition in results[0]:
            key = etree.SubElement(ar, 'k')
            key.text = definition.key
            if definition.translations:
                defin = etree.SubElement(ar, 'span')
                defin.text = definition.translations
            if definition.context:
                context = etree.SubElement(ar, 'context')
                context.text = definition.context
            etree.SubElement(ar, 'hr')

        for example in results[1]:
            if example.example:
                ex = etree.SubElement(ar, 'ex')
                ex.text = example.example
            translation_example = etree.SubElement(ar, 'trans')
            translation_example.text = example.translation_example
            etree.SubElement(ar, 'hr')
            
        tree.write(current_dictionary, encoding='utf-8', pretty_print=True, xml_declaration=True)

    return results

print(check_word('wordreference', 'francais','polonais','remplir'))
check_word('dictionnaire', 'francais','italien','remplir')
