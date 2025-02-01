from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="flipkart-recommender-chatbot",  # Normalized lowercase
    version="0.1.0",
    author="Girdhar97",
    description="Flipkart-style RAG chatbot with AstraDB and LangGraph",
    keywords="RAG chatbot langchain astradb flask",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.11",  # Enforce Dockerfile match
    zip_safe=False,  # Avoid .zip eggs for LangChain imports
    tests_require=["pytest>=7.0"],  # Core tests
    extras_require={
        "tests": ["pytest>=7.0"],
        "dev": ["black", "flake8"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
