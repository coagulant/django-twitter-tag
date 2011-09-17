from distutils.core import setup

setup(
    name='django-twitter-tag',
    version='0.1.0dev',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=['twitter_tag'],
    url='http://github.com/futurecolors/django-template-tag/',
    license='LICENSE.txt',
    description='Shows last N tweets of a user in django template.',
    long_description=open('README.rst').read(),
    install_requires=[
        "django-templatetag-sugar==0.1",
        "ttp==1.0",
        "python-twitter==0.8.2"
    ],
)