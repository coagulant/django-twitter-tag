try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'Django>=1.2,<1.4',
    'mock==0.7.2'
]

setup(
    name='django-twitter-tag',
    version='0.2.0',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=find_packages(exclude=("tests")),
    url='http://github.com/futurecolors/django-template-tag/',
    license='MIT',
    description="A django template tag to display user's recent tweets.",
    long_description=open('README.rst').read(),
    dependency_links=[
        'https://github.com/BonsaiDen/twitter-text-python/tarball/master#egg=twitter-text-python-1.0',
    ],
    install_requires=[
        "django-templatetag-sugar==0.1",
        "python-twitter==0.8.2",
        "twitter-text-python>=1.0"
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)