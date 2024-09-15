from setuptools import setup, find_packages

setup(
    name='stellarbot',
    version='1.0.2',
    description='stellarbot  is a professional trading bot that can be used to interact with the Stellar network.',
    author='nguemechieu',
    author_email='nguemechieu@live.com',
    packages=find_packages( '.'),
    install_requires=[
        'requirements.txt'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
          'stellarbot = stellarbot.stellarbot:main'
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
        'Source': 'https://github.com/nguemechieu/stellarbot'}

)