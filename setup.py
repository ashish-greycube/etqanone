from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in etqanone/__init__.py
from etqanone import __version__ as version

setup(
	name="etqanone",
	version=version,
	description="Customization for Etqansoft",
	author="admin@greycube.in",
	author_email="admin@greycube.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
