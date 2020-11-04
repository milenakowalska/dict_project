from lxml import etree
import os, datetime


languages = {'francais':['fr','fre'], 'russe':['ru','rus'] ,'espagnol':['es','esp'], 'polonais':['pl','pol'], 'italien':['it','ita'], 'allemand':['de','ger'], 'anglais':['en','eng'],'portugais':['pt','por'],'chiois':['zh','chi']}

def dictionary_template(dictionary, language_from, language_to):
        dictionary_name = f'{dictionary}_{language_from}_{language_to}.xdxf'
        
        root = etree.Element('xdxf')
        root.set('lang_from', languages[language_from][1])
        root.set('lang_to', languages[language_to][1])
        root.set('format', 'visual')
        root.set('revision', 'DD')

        meta_info = etree.SubElement(root, 'meta_info')
        title = etree.SubElement(meta_info, 'title')
        title.text = f'{dictionary.capitalize()}: {language_from} - {language_to}'

        description = etree.SubElement(meta_info, 'description')
        description.text = f'Dictionary: {dictionary.capitalize()}; language-from: {language_from}; language-to: {language_to}'        

        full_name = etree.SubElement(meta_info, 'full_name')
        full_name.text = f'{dictionary.capitalize()}: {language_from} - {language_to}'

        creation_date = etree.SubElement(meta_info, 'creation_date')
        creation_date.text = datetime.date.today().strftime("%d-%m-%Y")

        etree.SubElement(root, 'lexicon')
        tree = etree.ElementTree(root)
        tree.write(f'dictionaries/{dictionary_name}', pretty_print=True, xml_declaration=True, encoding='utf-8')
