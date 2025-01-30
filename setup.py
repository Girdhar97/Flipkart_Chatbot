from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="FLIPKART RECOMMENDER CHATBOT",
    version="0.1",
    author="Girdhar97",
    packages=find_packages(),
    install_requires = requirements,
)