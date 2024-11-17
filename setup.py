import subprocess
from setuptools import setup, find_packages


def get_version_from_git():
    try:
        # Fetch the latest tag
        version = (
            subprocess.check_output(["git", "describe", "--tags"])
            .strip()
            .decode("utf-8")
        )
        # Process the tag if it has additional information, like a commit hash
        if "-" in version:
            version = version.split("-")[0]  # Use only the tag prefix
        return version
    except Exception:
        return "0.0.0"  # Default version if no tag is found


setup(
    name="soilstat",
    version=get_version_from_git(),
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
