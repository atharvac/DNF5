from setuptools import setup


with open("README.md", "r") as readme:
    long_description = readme.read()

install_requirements = []
with open("requirements.txt", "r") as f:
    install_requirements = f.read().split("\n")

setup(
    name="dnf5",
    version="1.0.0",
    author="Atharva Chincholkar",
    author_email="atharvachincholkar@gmail.com",
    description="dnf5 is a toolwhich allows you to check DNS times",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["dnf5"],
    entry_points={"console_scripts": ["dnf5 = dnf5:cli"]},
    python_requires=">=3",
    install_requires=install_requirements,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ]
)
