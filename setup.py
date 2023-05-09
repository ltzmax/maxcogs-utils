import setuptools

__version__ = 2.0

setuptools.setup(
    name="maxcogs-utils",
    version=__version__,
    author="ltzmax",
    description="Cog utils for maxcogs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8.5",
)
