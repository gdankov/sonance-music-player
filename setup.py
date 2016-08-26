from setuptools import setup, find_packages

setup(
    name="Sonance-Music-Player",
    version="0.1 Alpha",
    packages=find_packages(),
    author="Georgi Dankov",
    author_email="gddankov@gmail.com",
    description="This is a music player using PyQt5",
    license="GNU GPL v2",
    url="https://github.com/gdankov/sonance-music-player",
    install_requires=['PyQt5>=5.0', 'mutagen>=1.32'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ]
)
