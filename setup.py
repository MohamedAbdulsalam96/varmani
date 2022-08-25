from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in trader/__init__.py
from trader import __version__ as version

setup(
	name="varmani",
	version=version,
	description="Varmani Network Management Application",
	author="Hemant Pema",
	author_email="hemant@pema.co.za",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
