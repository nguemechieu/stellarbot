from setuptools import setup, find_packages

setup(
    name='stellarbot',
    version='1.0.0',
    description='stellarbot  is a professional trading bot that can be used to interact with the Stellar network.',
    author='nguemechieu',
    author_email='nguemechieu@live.com',
    packages=find_packages(),
    install_requires=[
        'requirements.txt'
    ],
    zip_safe=False
)