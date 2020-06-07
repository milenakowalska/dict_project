from bs4 import BeautifulSoup  
import requests
from collections import namedtuple
from lxml import etree
from io import StringIO, BytesIO

Word = namedtuple('Word', ['key','translations','definition','example'])

def find_definition(language_from: str, language_to: str, word: str) -> list:
    source = requests.get(f'https://www.wordreference.com/{language_from}{language_to}/{word}').text
    soup = BeautifulSoup(source, 'lxml').body
    tables = soup.find_all("table", class_='WRD')

    current_class = ['odd']
    key = None
    definitio = None
    example = None
    list_of_translations = []
    list_of_word_objects = []

    for table in tables:
        new = table.find_all('tr')
        for tr in new:
            if tr['class'] == ['even'] or tr['class'] == ['odd']:
                if tr['class'] != current_class:
                    if key:
                        new_word = Word(key=key, translations=list_of_translations, definition=definitio, example=example)
                        list_of_word_objects.append(new_word)
                    list_of_translations = []
                    example = None
                    definitio = None
                    current_class = tr['class']
                    key = tr.find('td', class_='FrWrd').strong.text

                    if (tr.find('td', class_=None).text) is not None:
                        definitio = tr.find('td', class_=None).text

                    if (translation := tr.find('td', class_='ToWrd')) is not None:
                        list_of_translations.append(translation.find(text=True,recursive=False))
                
                else:
                    if (translation := tr.find('td', class_='ToWrd')) is not None:
                        list_of_translations.append(translation.find(text=True,recursive=False))

                    if (tr.find('td', class_='FrEx')) is not None:
                        example = tr.find('td', class_='FrEx').text

    return list_of_word_objects

my_dict = 'french_dict.xdxf'

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(my_dict, parser)
root = tree.getroot()
 
def check_word(word: str) -> list:
    results = []
    for element in tree.iter('ar'):
        if element.get('key') == word:
            key, translation, definition, example = '','','',''
            for tag in element.iter():
                if tag.tag == 'k':
                    key = tag.text
                elif tag.tag == 'span':
                    translation = tag.text
                elif tag.tag == 'def':
                    definition = tag.text
                elif tag.tag == 'ex':
                    example = tag.text
                elif tag.tag == 'hr':
                    results.append(Word(key, translation, definition='', example=''))
                    key, translation, definition, example = '','','',''

    if results == []:
        results = find_definition('fr','pl',word)
        ar = etree.SubElement(root[1], 'ar')
        ar.set('key',word)

        for definition in results:
            key = etree.SubElement(ar, 'k')
            key.text = definition.key
            if definition.definition:
                defin = etree.SubElement(ar, 'def')
                defin.text = definition.definition
            translation = etree.SubElement(ar, 'span')
            translation.text = ', '.join(definition.translations)
            if definition.example:
                example = etree.SubElement(ar, 'ex')
                example.text = definition.example

            etree.SubElement(ar, 'hr')

        tree.write(my_dict, encoding='utf-8', pretty_print=True, xml_declaration=True)

    return results

print(check_word("orage"))
