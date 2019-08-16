# ps2catalog
A prestashop to facebook catalog creator.

It retrieves products from a prestashop API webservice and converts it to a sufficiently valid catalog to be uploaded to Facebook.

## Setup
The script uses prestapyt via a git submodule as pip package is outdated.

Create a virtualenv and install requirements
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Create a config.ini file with the following information:

```
[ps]
base_url=YOUR_PS_URL
api_url=YOUR_PS_API_URL
token=TOKEN_FOR_WEBSERVICE_ACCESS
lang_id=PS_LANGUAGE_ID

[report]
lang=LANGISOCODE
file_name=CATALOGFILENAME
folder_name=CATALOGFOLDER

[general]
brand=BRANDCODE

# Category mapping
# Key is category from prestashop
# Value is its corresponding Google Product Catalog category id
[catemap]
XX=YYY
```

## Execution
Just

```
python get-catalog.py
```

You'll find your catalog into report.folder_name.