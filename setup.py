import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='data_feed',
    version='0.1.0',
    author='James Arnold',
    description='Library for setting up a publish subscribe pipeline based on remote data feeds',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[
        'boto3>=1.7.17',
        'redis>=2.10.6',
        'ujson>=1.35'
    ],
    extras_require={
        'dev': [
            'codecov',
            'mock',
            'pytest',
            'pytest-cov'
        ]    
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent'
    ]
)
