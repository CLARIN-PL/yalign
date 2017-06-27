Installation
============

1. Install required system packages:

	$ sudo apt-get install python-virtualenv python3-virtualenv python-dev build-essential

2. From directory "aligner_webapp" start:

	$ python3 start-aligner-webui.py

Also app requires nltk tokenizers to be installed, module name "punkt"

Yalign
======

Yalign models can be added to "aligner_webapp/models/", and will be automatically detected.

Accepted files
==============

Aligner WebApp accepts pain text utf-8 encoded files, and files in formats ".doc", ".docx", ".odt"