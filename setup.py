from setuptools import setup, find_packages

setup(
    name="chat_app",
    version="0.1.0",
    description="A simple chat application with configurable parameters",
    author="Simone Roman",
    packages=find_packages(),  # Trova automaticamente i pacchetti nella directory
    entry_points={
        "console_scripts": [
            "chat-app=chat_app.main:main",  # Comando per eseguire l'app dalla linea di comando
        ],
    },
    python_requires=">=3.7",  # Specifica la versione minima di Python
)
