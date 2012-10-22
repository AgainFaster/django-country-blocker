from distutils.core import setup
import os

CLASSIFIERS = [
    'License :: OSI Approved :: BSD License',
    'Framework :: Django',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    name='django-country-blocker',
    version='0.1.2',
    packages=['country_block'],
    url='http://www.github.com/jslootbeek/django-country-blocker',
    license='BSD License',
    author='Jule Slootbeek',
    author_email='jslootbeek@gmail.com',
    requires=['Django (>=1.3)'],
    description='Django app introducing a Context Processor that adds users location information to the context.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    classifiers=CLASSIFIERS,
)
