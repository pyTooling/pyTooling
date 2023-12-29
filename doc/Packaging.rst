.. _PACKAGING:

Overview
########

.. contents:: Table of Contents
   :depth: 2

.. _PACKAGING/Helper:

Helper Functions
################

.. _PACKAGING/Helper/loadReadmeFile:

loadReadmeFile
**************

The function :func:`~pyTooling.Packaging.loadReadmeFile` reads a ``README`` file. This text can then be used for the
package's *long description*.

.. rubric:: Supported file formats

* `Markdown <https://daringfireball.net/projects/markdown/>`__


.. _PACKAGING/Helper/loadRequirementsFile:

loadRequirementsFile
********************

The function :func:`~pyTooling.Packaging.loadRequirementsFile` reads a ``requirements.txt`` file and extracts all
specified dependencies into an array.

.. rubric:: Features

* Comments are skipped.
* Special dependency entries like Git repository references are translates to match the syntax expected by setuptools.


.. _PACKAGING/Helper/extractVersionInformation:

extractVersionInformation
*************************

The function :func:`~pyTooling.Packaging.extractVersionInformation` extracts version information from a Python source
file (module). Usually these module variables are defined in a ``__init__.py`` file.

.. rubric:: Supported fields

* Author name (``__author__``)
* Author email address (``__email__``)
* Copyright information (``__copyright_``)
* License name (``__license__``)
* Version number (``__version__``)
* Keywords (``__keywords__``)

The function returns an instance of :class:`~pyTooling.Packaging.VersionInformation`, which offers the gathered
information as properties.

.. admonition:: ``__init__.py``

   .. code-block:: python

      __author__ =    "Patrick Lehmann"
      __email__ =     "Paebbels@gmail.com"
      __copyright__ = "2017-2024, Patrick Lehmann"
      __license__ =   "Apache License, Version 2.0"
      __version__ =   "1.10.1"
      __keywords__ =  ["decorators", "meta classes", "exceptions", "platform", "versioning"]

.. admonition:: Usage in ``setup.py``

   .. code-block:: python

      from setuptools import setup
      from pyTooling.Packaging import extractVersionInformation

      file = Path("../pyTooling/Common/__init__.py")
      versionInfo = extractVersionInformation(file)

      setup(
        # ...
        version=versionInformation.Version,
  	    author=versionInformation.Author,
  	    author_email=versionInformation.Email,
        keywords=versionInformation.Keywords,
        # ...
      )

.. _PACKAGING/Descriptions:

PackageDescriptions
###################

.. rubric:: Example:

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

.. TODO:: PACKAGING:: Needs documentation for DescribePythonPackage


.. _PACKAGING/Descriptions/GitHub:

DescribePythonPackageHostedOnGitHub
***********************************

.. TODO:: PACKAGING:: Needs documentation for DescribePythonPackageHostedOnGitHub
