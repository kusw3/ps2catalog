# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import sys
import json
import argparse

import requests
import codecs
from configparser import ConfigParser
from distutils.version import LooseVersion

# Hackety Hack. Puc mantenir el prestapyt com a submodul i buscar la lib dins d'aquest.
# git submodule add https://github.com/prestapyt/prestapyt.git
# El paquet disponible a pip no es prou nou per prestashop 1.7
sys.path.insert(1, 'prestapyt/')
from prestapyt import PrestaShopWebServiceDict

def get_fb_catalog(ps, f, c):
    plist = ps.get('products',options={'filter[active]': '1'})
    lang_id = c.get('ps','lang_id')
    base_url = c.get('ps', 'base_url')

    print("PROCESSING: {}".format(len(plist['products']['product'])))

    # field header
    f.write(u'id\ttitle\tdescription\tlink\timage_link\tavailability\tprice\tcurrency\tgoogle_product_category\tbrand\tage_group\tgender\tcondition\n')

    for product in plist['products']['product']:
        prod = ps.get('products/'+product['attrs']['id'])

        if prod['product']['active'] == '0':
            print("Product not active: "+product['attrs']['id'])
            continue

        # id - prod['product']['reference']
        id = prod['product']['reference']

        # title - for name in prod['product']['name']['language']:  name['value'] if lang == 'ES' else next
        if isinstance(prod['product']['name']['language'], list):
            for name in prod['product']['name']['language']:
                if name['attrs']['id'] == lang_id:
                    title = name['value']
        else:
            title = prod['product']['name']['language']['value']


        # description - for desc prod['product']['description_short']['language']:  desc['value'] if lang == 'ES' else next
        if isinstance(prod['product']['description']['language'], list):
            for name in prod['product']['description']['language']:
                if name['attrs']['id'] == lang_id:
                    description = name['value'].replace('<p>','').replace('</p>','')
        else:
            description = prod['product']['description']['language']['value'].replace('<p>','').replace('</p>','')

        # link -
        if isinstance(prod['product']['link_rewrite']['language'], list):
            for ln in prod['product']['link_rewrite']['language']:
                if ln['attrs']['id'] == lang_id:
                    link = "{0}/{1}-{2}.html".format(base_url, product['attrs']['id'], ln['value'])
        else:
            link = "{0}/{1}-{2}.html".format(base_url, product['attrs']['id'], prod['product']['link_rewrite']['language']['value'])

        # image_link
        r = requests.get("{0}/get-image.php?imageid={1}".format(base_url, prod['product']['id_default_image']['value']))
        image_link = r.text

        # availability -
        # TODO: stocks available quan hi ha més d'una combinació
        # si stock_available es una llista vol dir que hi ha més d'una combinació.
        # de moment assumim stock = len de la llista
        if isinstance(prod['product']['associations']['stock_availables']['stock_available'], list):
            stocks_avail['stock_available']['quantity'] = str(len(prod['product']['associations']['stock_availables']['stock_available']))
        else:
            stocks_avail = ps.get('stock_availables/'+prod['product']['associations']['stock_availables']['stock_available']['id'])
        
        print("ID: "+id+" Quantity: "+stocks_avail['stock_available']['quantity'])
        if int(stocks_avail['stock_available']['quantity']) > 0:
            print("in stock")
            #if lang_id == '1':
            avail = 'in stock'
            #else:
            #    avail = 'disponible'
        else:
            print("out of stock")
            #if lang_id == '1':
            avail = 'out of stock'
            #else:
            #    avail = 'agotado'

        # price
        price = "{:.2f}".format(float(prod['product']['price'])*1.21)
        currency = "EUR"

        # google_product_category
        catemap = dict(c.items('catemap'))
        try:
            gpc = catemap[ prod['product']['id_category_default'] ]
        except KeyError:
            print("Key ERROR - Product ID: {0} Category ID: {1}".format(prod['product']['id'], prod['product']['id_category_default']))
            quit()
        
        # brand - from config
        brand = c.get('general', 'brand')

        # age_group - adult
        age_group = 'adult'

        # TODO: color
        #color = ''

        # gender - female
        gender = 'female'

        # TODO: shipping

        # condition - new
        condition = 'new'

        # with shipping info
        #print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}".format(id, title, description, link, image_link, avail, price, gpc, brand, age_group, color, gender, shipping, condition))

        # without shipping info, color
        f.write(u'{0}\t"{1}"\t"{2}"\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\n'.format(id, title, description, link, image_link, avail, price, currency, gpc, brand, age_group, gender, condition))

    return 

if __name__ == '__main__':

    try:
        basedir = sys.argv[1]
    except IndexError:
        basedir = '.'

    config = ConfigParser()
    config.read(basedir+'/config.ini')

    file = codecs.open("{0}/{1}-{2}.tsv".format(config.get('report','folder_name'), config.get('report','file_name'), config.get('report','lang')), "w", "utf-8-sig")

    ps = PrestaShopWebServiceDict(config.get('ps', 'api_url'), config.get('ps', 'token'))

    get_fb_catalog(ps, file, config)

    file.close()