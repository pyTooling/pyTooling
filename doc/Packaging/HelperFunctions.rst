Helper Functions
################

loadReadmeFile
**************

The function :py:func:`~pyTooling.Packaging.loadReadmeFile` reads a `README` file in e.g. Markdown format. This text can
then be used for the package's *long description*.

.. autofunction:: pyTooling.Packaging.loadReadmeFile


loadRequirementsFile
********************

The function :py:func:`~pyTooling.Packaging.loadRequirementsFile` reads a `requirements.txt` file and extracts all
pecified dependencies into an array. Comments are skipped and special dependency entries like Git repository references
are translates to match the syntax expected by setuptools.

.. autofunction:: pyTooling.Packaging.loadRequirementsFile


extractVersionInformation
*************************

.. TODO:: Write documentation here!

.. autofunction:: pyTooling.Packaging.extractVersionInformation
