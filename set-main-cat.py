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

def set_main_category(ps, c):
  plist = ps.get('products',options={'filter[active]': '1'})
  lang_id = c.get('ps','lang_id')
  base_url = c.get('ps', 'base_url')

  print("PROCESSING: {}".format(len(plist['products']['product'])))

  for product in plist['products']['product']:
    prod = ps.get('products/'+product['attrs']['id'])

    if prod['product']['active'] == '0':
      print("Product not active: "+product['attrs']['id'])
      continue

    # id - prod['product']['reference']
    id = prod['product']['reference']

    if prod['product']['id_category_default'] == '2':
      print("ProductID: {0} Ref: {1} with default_cat=2".format(prod['product']['id'], id))


if __name__ == '__main__':

  try:
      basedir = sys.argv[1]
  except IndexError:
      basedir = '.'

  config = ConfigParser()
  config.read(basedir+'/config.ini')

  ps = PrestaShopWebServiceDict(config.get('ps', 'api_url'), config.get('ps', 'token'))

  set_main_category(ps, config)