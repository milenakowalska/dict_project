from bs4 import BeautifulSoup  
import requests, os, datetime
from lxml import etree
from dictionary_template import dictionary_template
from dict_parser import WordreferenceParser, DictionnaireParser, Word, Example


installed_dictionaries = [WordreferenceParser, DictionnaireParser]

def check_word(dictionary: str, language_from: str, language_to: str, word: str) -> list:
    current_dictionary = f'dictionaries/{dictionary}_{language_from}_{language_to}.xdxf'

    list_of_words, list_of_examples = [],[]
    if os.path.exists(current_dictionary):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(current_dictionary, parser)
        root = tree.getroot()
        for element in tree.iter('ar'):
            if element.get('key') == word:
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
                            list_of_words.append(Word(key, translation, context))
                        if example != '':
                            list_of_examples.append(Example(example, translation_example))
                        key, translation, definition, example = '','','',''
    else:
        dictionary_template(dictionary, language_from, language_to)
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(current_dictionary, parser)
        root = tree.getroot()

    if list_of_words == [] and list_of_examples == []:  
        for dictionary_class_name in installed_dictionaries:
            if dictionary_class_name.dictionary_string == dictionary:
                dictionary_class = dictionary_class_name  
        list_of_words, list_of_examples = dictionary_class.find_definition(language_from, language_to, word)

        ar = etree.SubElement(root.find('lexicon'), 'ar')
        ar.set('key',word)

        for definition in list_of_words:
            key = etree.SubElement(ar, 'k')
            key.text = definition.key
            if definition.translations:
                defin = etree.SubElement(ar, 'span')
                defin.text = definition.translations
            if definition.context:
                context = etree.SubElement(ar, 'context')
                context.text = definition.context
            etree.SubElement(ar, 'hr')

        for example in list_of_examples:
            if example.example:
                ex = etree.SubElement(ar, 'ex')
                ex.text = example.example
            translation_example = etree.SubElement(ar, 'trans')
            translation_example.text = example.translation_example
            etree.SubElement(ar, 'hr')
            
        if list_of_words != []: 
            tree.write(current_dictionary, encoding='utf-8', pretty_print=True, xml_declaration=True)

    if list_of_words != []: 
        return [list_of_words, list_of_examples]
    else:
        return [[Word('Word not found!', '')],[]]



