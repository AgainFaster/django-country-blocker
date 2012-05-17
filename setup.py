from distutils.core import setup

setup(
    name='django-country-blocker',
    version='0.1',
    packages=['country_block'],
    url='http://www.github.com/jslootbeek/django-country-blocker',
    license='BSD License',
    author='Jule Slootbeek',
    author_email='jslootbeek@gmail.com',
    description='Django app introducing a Context Processor that adds users location information to the context.'
)
