from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="flipkart-recommender-chatbot",  # Lowercase, normalized
    version="0.1.0",
    author="Girdhar97",
    description="Flipkart-style RAG chatbot with AstraDB and LangGraph",  # NEW: Brief desc
    keywords="RAG chatbot langchain astradb flask",  # NEW: Searchable tags
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[  # NEW: Standards compliance
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
