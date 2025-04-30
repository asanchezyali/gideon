from setuptools import setup, find_packages

setup(
    name="gideon",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-core>=0.1.0",
        "langchain-text-splitters>=0.0.1",
        "pypdf>=3.0.0",
        "ollama>=0.1.0",
        "pydantic>=2.0.0",
        "tiktoken>=0.5.2",
        "faiss-cpu>=1.7.4",
        "typing-extensions>=4.5.0",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "unstructured>=0.10.30",
        "python-magic>=0.4.27"
    ],
    scripts=["bin/gideon"],
    python_requires=">=3.10",
    include_package_data=True,
    zip_safe=False,
)