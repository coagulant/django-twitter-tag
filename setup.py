from os import path
import codecs
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

tests_require = [
    'nose==1.2.1',
    'mock==1.0.1',
    'httpretty==0.5.9',
    'sure==1.1.7',
]

setup(
    name='django-twitter-tag',
    version='1.2.1',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=find_packages(exclude="tests"),
    url='https://github.com/coagulant/django-twitter-tag',
    license='MIT',
    description="A django template tag to display user's recent tweets.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    install_requires=[
        "django-classy-tags>=0.4",
        "twitter>=1.9.1",
        "django-appconf>=0.6",
        'six>=1.2.0',
    ],
    tests_require=tests_require,
    test_suite="nose.collector",
    extras_require={'test': tests_require},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
