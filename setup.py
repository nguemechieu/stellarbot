from setuptools import setup, find_packages
import os

# Read requirements.txt for install_requires
def read_requirements():
    """Read requirements.txt and return as a list of dependencies."""
    with open('requirements.txt') as req_file:
        return req_file.readlines()

setup(
    name='stellarbot',
    version='1.0.2',
    description='StellarBot is a professional trading bot that interacts with the Stellar network.',
    author='Nguemechieu',
    author_email='nguemechieu@live.com',
    packages=find_packages(where='src'),  # Find packages in the 'src' folder
    package_dir={'': 'src'},  # Tells setuptools that the packages are under 'src'
    install_requires=read_requirements(),  # Use the requirements.txt file
    zip_safe=False,
    entry_points={
        'console_scripts': [
          'stellarbot = stellarbot.main:main'  # Adjust this to the actual module with your main function
        ]
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.12',
    keywords='stellar network trading bot',
    url='https://github.com/nguemechieu/stellarbot',
    project_urls={
        'Bug Reports': 'https://github.com/nguemechieu/stellarbot/issues',
        'Source': 'https://github.com/nguemechieu/stellarbot'
    },
)
