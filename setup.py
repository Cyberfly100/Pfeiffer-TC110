import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PfeifferTC110-Cyberly100", # Replace with your own username
    version="0.8.0",
    author="Lucas Schweickert",
    author_email="cyberfly@gmx.net",
    description="A small package for communicating with Pfeiffer vaccuum electronics (e.g. TC110) via RS485 and their telegram protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyberfly100/pfeiffertc110",
    package_dir={'':'src'},
    packages=['pfeifferTC110'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pyvisa-py'
        'pyusb'
        'pyserial'
    ]
)