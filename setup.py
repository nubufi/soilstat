from setuptools import setup, find_packages

print(find_packages())
setup(
    name="soilstat",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Numan Burak Fidan",
    author_email="numanburakfidan@yandex.com",
    description="A toolbox for geotechnical engineering calculations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nubufi/soilstat",
    packages=find_packages(),  # Automatically find packages in the directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["numpy"],  # Dependencies your project needs
)
