"""PyFlume setuptools for PyPi."""
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyFlume',
    version='0.6.2',
    author='ChrisMandich',
    author_email='Chris@Mandich.net',
    description='Package to integrate with Flume Sensor',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/ChrisMandich/PyFlume',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'pyjwt',
        'ratelimit',
        'pytz',
        'requests',
    ],
)
