from setuptools import setup, find_packages

setup(
    name="supercontrast",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "boto3",
        "azure-ai-textanalytics",
        "google-cloud-language",
        "google-api-python-client",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-auth",
        "google-api-core",
        "google-cloud-vision",
        "google-cloud-translate",
        "google-cloud-speech",
        "google-cloud-language",
        "google-cloud-translate",
        "google-cloud-vision",
    ],
    author="SuperContrast Founders",
    author_email="founders@supercontrast.com",
    description="A package for supercontrast functionality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/supercontrast",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
