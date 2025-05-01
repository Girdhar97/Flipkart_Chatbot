from setuptools import setup, find_packages
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


try:
    logger.info("Loading requirements from requirements.txt")
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    logger.info(f"Loaded {len(requirements)} requirements successfully")
except Exception as e:
    logger.error(f"Error reading requirements.txt: {str(e)}")
    raise CustomException("Failed to load requirements.txt", e)


try:
    logger.info("Starting setuptools configuration")
    setup(
        name="flipkart-recommender-chatbot",
        version="0.1.0",
        author="Girdhar97",
        description="Flipkart-style RAG chatbot with AstraDB and LangGraph",
        keywords="RAG chatbot langchain astradb flask",
        packages=find_packages(),
        install_requires=requirements,
        python_requires=">=3.11",
        zip_safe=False,
        tests_require=["pytest>=7.0"],
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
    logger.info("Setuptools configuration completed successfully")
except Exception as e:
    logger.error(f"Error in setuptools setup: {str(e)}")
    raise CustomException("Setuptools package configuration failed", e)
