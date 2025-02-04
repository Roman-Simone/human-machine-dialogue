from setuptools import setup, find_packages

setup(
    name="chat_app",
    version="0.1.0",
    description="A simple chat application with configurable parameters",
    author="Simone Roman",
    packages=find_packages(),  
    entry_points={
        "console_scripts": [
            "chat-app=chat_app.main:main", 
        ],
    },
    python_requires=">=3.7",  
)
