PackageDescriptions
###################

.. rubric:: Example

.. code-block:: Python

   from pathlib             import Path
   from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub

   packageName = "pyTooling.Packaging"

   DescribePythonPackageHostedOnGitHub(
     packageName=packageName,
     description="A set of helper functions to describe a Python package for setuptools.",
     gitHubNamespace="pyTooling",
     keywords="Python3 setuptools package wheel installation",
     sourceFileWithVersion=Path(f"{packageName.replace('.', '/')}/__init__.py"),
     developmentStatus="beta",
     pythonVersions=("3.8", "3.9", "3.10")
   )


DescribePythonPackage
*********************

.. TODO:: Write documentation here!



DescribePythonPackageHostedOnGitHub
***********************************

.. TODO:: Write documentation here!

