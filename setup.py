import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="hoprd-config-tool",
    version="0.1.3",
    scripts=["bin/hoprd-config-tool"],
    author="Jean Demeusy",
    author_email="jean.demeusy@hoprnet.org",
    description="Helper tool to easily create and run HOPRd nodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeandemeusy/hoprd-config-tool",
    packages=["hoprd-config-tool", "hoprd-config-tool/yaml", "hoprd-config-tool/templates"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pyYAML", "Jinja2", "pycurl", "click"]
)
