#-----------------------------------------------------------------
# To create a compressed package : python setup.py sdist
#
# To create a windows executable: python setup.py bdist_wininst
#-----------------------------------------------------------------
from distutils.core import setup
setup(name='PyXML2PDF',
      version='1.0',
      description='XML to PDF',
      author='David Vaillancourt',
      author_email='blake.diamond@gmail.com',
      url='https://github.com/kelvin0/PyXML2PDF',
      packages=['PyXML2PDF',],
      package_data={'PyXML2PDF': ['*.py',]}      
      )
