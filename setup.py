import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='res2desc',  # Replace with your own username
    version='0.0.1',
    author='Bonan Zhu',
    author_email='zhubonan@outlook.com',
    description=
    'Commandline interface for computing descriptors for AIRSS search results',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zhubonan/res2desc',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['dscribe>=0.3.5', 'click>=7.0'],
    extras_require={'testing': ['pytest>=5.0']},
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        res2desc=res2desc.cli:cli
    ''')
