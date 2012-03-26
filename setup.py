from os import path
import codecs
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

tests_require = [
    'Django>=1.2',
    'nose',
    'mock>=0.7.2',
]

setup(
    name='django-twitter-tag',
    version='0.4.0rc',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=find_packages(exclude=("tests")),
    url='https://github.com/coagulant/django-twitter-tag',
    license='MIT',
    description="A django template tag to display user's recent tweets.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    dependency_links=[
        'https://github.com/BonsaiDen/twitter-text-python/tarball/master#egg=twitter-text-python-1.0',
    ],
    install_requires=[
        "django-templatetag-sugar==0.1",
        "python-twitter==0.8.2",
        "twitter-text-python>=1.0"
    ],
    tests_require=tests_require,
    test_suite = "runtests",
    extras_require={'test': tests_require},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)