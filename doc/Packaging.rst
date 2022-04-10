.. _PACKAGING:

Overview
########

.. _PACKAGING/Helper:

Helper Functions
################

.. _PACKAGING/Helper/loadReadmeFile:

loadReadmeFile
**************

The function :py:func:`~pyTooling.Packaging.loadReadmeFile` reads a `README` file in e.g. Markdown format. This text can
then be used for the package's *long description*.


.. _PACKAGING/Helper/loadRequirementsFile:

loadRequirementsFile
********************

The function :py:func:`~pyTooling.Packaging.loadRequirementsFile` reads a `requirements.txt` file and extracts all
pecified dependencies into an array. Comments are skipped and special dependency entries like Git repository references
are translates to match the syntax expected by setuptools.


.. _PACKAGING/Helper/extractVersionInformation:

extractVersionInformation
*************************

.. TODO:: Write documentation here!

.. _PACKAGING/Descriptions:

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


.. _PACKAGING/Descriptions/Python:

DescribePythonPackage
*********************

.. TODO:: Write documentation here!


.. _PACKAGING/Descriptions/GitHub:

DescribePythonPackageHostedOnGitHub
***********************************

.. TODO:: Write documentation here!

