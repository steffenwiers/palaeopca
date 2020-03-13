import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "ppca-tool",
    version = "1.0.0",
    author = "Steffen Wiers",
    author_email = "steffen.p.wiers@gmail.com",
    description = "Tool to perform principal component analysis on palaeomagnetic data sets",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/steffenwiers/ppca-tool",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
    include_package_data = True,
)