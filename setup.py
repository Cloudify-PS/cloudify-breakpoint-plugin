from setuptools import setup
from setuptools import find_packages


setup(
    name='cloudify-breakpoint-plugin',
    version='1.1.2',
    author='Michal Mordawski',
    author_email='Michal.Mordawski@cloudify.co',
    license='LICENSE',
    zip_safe=False,
    packages=find_packages(exclude=['tests*']),
    install_requires=['cloudify-common>=5.0.5'],
)
