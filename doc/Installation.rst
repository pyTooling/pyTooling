.. |PackageName| replace:: pyTooling

.. _INSTALL:

Installation/Updates
####################

See the following instructions on how to install or update the package from common sources like PyPI. Developers can
also install the packages with development dependencies. In case of local development, see the additional sections on
how to run unit tests, type checks or how to build the documentation to create all the build artifacts.

See the list of :ref:`necessary dependencies <DEP>`.


.. _INSTALL/pip:

Using PIP to Install from PyPI
******************************

The following instruction are using PIP (Package Installer for Python) as a package manager and PyPI (Python Package
Index) as a source of Python packages.

PIP might download further packages as listed in :ref:`package dependencies <DEP/package>`.


.. _INSTALL/pip/install:

Installing a Wheel Package from PyPI using PIP
==============================================

Users can install the |PackageName| package as a minimal installation or the package with extensions (``packaging``,
``terminal``, ``yaml``) installing further dependencies. In case the provided extensions are not needed, it keeps the
list of dependencies low - especially the minimal installation is still dependency free.

See :ref:`DEP/package` for more details.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: Minimal installation
            :sync: Minimal

            .. code-block:: bash

               # Basic pyTooling package
               pip3 install pyTooling

               # Alternatively
               python3 -m pip install pyTooling

         .. tab-item:: With Packaging Support
            :sync: Packaging

            .. code-block:: bash

               # With setuptools support for pyTooling.Packaging
               pip3 install pyTooling[packaging]

               # Alternatively
               python3 -m pip install pyTooling[packaging]

         .. tab-item:: With Colored Console/Terminal Support
            :sync: Terminal

            .. code-block:: bash

               # With color support for pyTooling.TerminalUI
               pip3 install pyTooling[terminal]

               # Alternatively
               python3 -m pip install pyTooling[terminal]

         .. tab-item:: With YAML Support for Configuration Files
            :sync: YAML

            .. code-block:: bash

               # With YAML support for pyTooling.Configuration.YAML
               pip3 install pyTooling[yaml]

               # Alternatively
               python3 -m pip install pyTooling[yaml]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: Minimal installation
            :sync: Minimal

            .. code-block:: powershell

               # Basic pyTooling package
               pip install pyTooling

               # Alternatively
               py -m pip install pyTooling

         .. tab-item:: With Packaging Support
            :sync: Packaging

            .. code-block:: powershell

               # With setuptools support for pyTooling.Packaging
               pip install pyTooling[packaging]

               # Alternatively
               py -m pip install pyTooling[packaging]

         .. tab-item:: With Colored Console/Terminal Support
            :sync: Terminal

            .. code-block:: powershell

               # With color support for pyTooling.TerminalUI
               pip install pyTooling[terminal]

               # Alternatively
               py -m pip install pyTooling[terminal]

         .. tab-item:: With YAML Support for Configuration Files
            :sync: YAML

            .. code-block:: powershell

               # With YAML support for pyTooling.Configuration.YAML
               pip install pyTooling[yaml]

               # Alternatively
               py -m pip install pyTooling[yaml]

Developers can install the |PackageName| package itself or the package with further dependencies for documentation
generation (``doc``), running unit tests (``test``) or just all (``all``) dependencies.

See :ref:`DEP` for more details.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: Minimal installation
            :sync: Minimal

            .. code-block:: bash

               # Basic pyTooling package
               pip3 install pyTooling

               # Alternatively
               python3 -m pip install pyTooling

         .. tab-item:: With Documentation Dependencies
            :sync: Doc

            .. code-block:: bash

               # Install with dependencies to generate documentation
               pip3 install pyTooling[doc]

               # Alternatively
               python3 -m pip install pyTooling[doc]

         .. tab-item:: With Unit Testing Dependencies
            :sync: Unit

            .. code-block:: bash

               # Install with dependencies to run unit tests
               pip3 install pyTooling[test]

               # Alternatively
               python3 -m pip install pyTooling[test]

         .. tab-item:: All Developer Dependencies
            :sync: All

            .. code-block:: bash

               # Install with all developer dependencies
               pip3 install pyTooling[all]

               # Alternatively
               python3 -m pip install pyTooling[all]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: Minimal installation
            :sync: Minimal

            .. code-block:: powershell

               # Basic pyTooling package
               pip install pyTooling

               # Alternatively
               py -m pip install pyTooling

         .. tab-item:: With Documentation Dependencies
            :sync: Doc

            .. code-block:: powershell

               # Install with dependencies to generate documentation
               pip install pyTooling[doc]

               # Alternatively
               py -m pip install pyTooling[doc]

         .. tab-item:: With Unit Testing Dependencies
            :sync: Unit

            .. code-block:: powershell

               # Install with dependencies to run unit tests
               pip install pyTooling[test]

               # Alternatively
               py -m pip install pyTooling[test]

         .. tab-item:: All Developer Dependencies
            :sync: All

            .. code-block:: powershell

               # Install with all developer dependencies
               pip install pyTooling[all]

               # Alternatively
               py -m pip install pyTooling[all]


.. _INSTALL/pip/requirements:

Referencing the package in ``requirements.txt``
===============================================

When |PackageName| is used by another Python package, it's recommended to list the dependency to the |PackageName|
package in a ``requirements.txt`` file.

.. admonition:: ``requirements.txt``

   .. code-block:: text

      pyTooling ~= 8.5


.. _INSTALL/pip/update:

Updating from PyPI using PIP
============================

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         # Update pyTooling
         pip3 install -U pyTooling

         # Alternatively
         python3 -m pip install -U pyTooling

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         # Update pyTooling
         pip install -U pyTooling

         # Alternatively
         py -m pip install -U pyTooling


.. _INSTALL/pip/uninstall:

Uninstallation using PIP
========================

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         # Uninstall pyTooling
         pip3 uninstall pyTooling

         # Alternatively
         python3 -m pip uninstall pyTooling

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         # Uninstall pyTooling
         pip uninstall pyTooling

         # Alternatively
         py -m pip uninstall pyTooling


.. _INSTALL/testing:

Running unit tests
******************

This package is provided with unit tests for `pytest <https://docs.pytest.org/>`__. The provided testcases can be
executed locally for testing or development purposes. In addition, code coverage including branch coverage can be
collected using `Coverage.py <https://coverage.readthedocs.io/>`__. All steps provide appropriate artifacts as XML or
HTML reports. The artifact output directories are specified in ``pyproject.toml``.

Ensure :ref:`unit testing requirements <DEP/testing>` are installed.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: Unit Testing
            :sync: UnitTesting

            .. code-block:: bash

               cd <pyTooling>

               # Running unit tests using pytest
               pytest -raP --color=yes tests/unit

         .. tab-item:: Unit Testing with Ant/JUnit XML Reports
            :sync: UnitTestingXML

            .. code-block:: bash

               cd <pyTooling>

               # Running unit tests using pytest
               pytest -raP --color=yes --junitxml=report/unit/unittest.xml --template=html1/index.html --report=report/unit/html/index.html --split-report tests/unit

         .. tab-item:: Unit Testing with Code Coverage
            :sync: Coverage

            .. code-block:: bash

               cd <pyTooling>

               # Running unit tests with code coverage using Coverage.py
               coverage run --data-file=.coverage --rcfile=pyproject.toml -m pytest -ra --tb=line --color=yes tests/unit

               # Write coverage report to console"
               coverage report

               # Convert coverage report to HTML
               coverage html

               # Convert coverage report to XML (Cobertura)
               coverage xml

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: Unit Testing
            :sync: UnitTesting

            .. code-block:: powershell

               cd <pyTooling>

               # Running unit tests using pytest
               pytest -raP --color=yes tests\unit

         .. tab-item:: Unit Testing with Ant/JUnit XML Reports
            :sync: UnitTestingXML

            .. code-block:: powershell

               cd <pyTooling>

               # Running unit tests using pytest
               pytest -raP --color=yes --junitxml=report\unit\unittest.xml --template=html1\index.html --report=report\unit\html\index.html --split-report tests\unit

         .. tab-item:: Unit Testing with Code Coverage
            :sync: Coverage

            .. code-block:: powershell

               cd <pyTooling>

               # Running unit tests with code coverage using Coverage.py
               coverage run --data-file=.coverage --rcfile=pyproject.toml -m pytest -ra --tb=line --color=yes tests\unit

               # Write coverage report to console"
               coverage report

               # Convert coverage report to HTML
               coverage html

               # Convert coverage report to XML (Cobertura)
               coverage xml


.. _INSTALL/typechecking:

Running type checks
*******************

This package is provided with type checks. These can be executed locally for testing or development purposes using
`mypy <https://mypy-lang.org/>`__. The artifact output directory is specified in ``pyproject.toml``.

Ensure :ref:`unit testing requirements <DEP/testing>` are installed.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         cd <pyTooling>

         # Running type checking using mypy
         export MYPY_FORCE_COLOR=1
         mypy -p pyTooling

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         cd <pyTooling>

         # Running type checking using mypy
         $env:MYPY_FORCE_COLOR = 1
         mypy -p pyTooling


.. _INSTALL/documentation:

Building documentation
**********************

The documentation can be build locally using `Sphinx <https://www.sphinx-doc.org/>`__. It can generate HTML and LaTeX
outputs. In an additional step, the LaTeX output can be translated to a PDF file using a LaTeX environment like
`MiKTeX <https://miktex.org/>`__.

Ensure :ref:`documentation requirements <DEP/documentation>` are installed.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: Generating HTML
            :sync: HTML

            .. code-block:: bash

               cd <pyTooling>

               # Adding package root to PYTHONPATH
               export PYTHONPATH=$(pwd)
               cd doc

               # Building documentation using Sphinx
               sphinx-build -v -n -b html -d _build/doctrees -j $(nproc) -w _build/html.log . _build/html

         .. tab-item:: Generating LaTeX
            :sync: LaTeX

            .. code-block:: bash

               cd <pyTooling>

               # Adding package root to PYTHONPATH
               export PYTHONPATH=$(pwd)
               cd doc

               # Building documentation using Sphinx
               sphinx-build -v -n -b latex -d _build/doctrees -j $(nproc) -w _build/latex.log . _build/latex

         .. tab-item:: Generating PDF (from LaTeX)
            :sync: PDF

            .. todo:: Describe LaTeX to PDF conversion on Linux using Miktex.

            .. hint:: A `Miktex installation <https://miktex.org/>`__ is required.

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: Generating HTML
            :sync: HTML

            .. code-block:: powershell

               cd <pyTooling>

               # Building documentation using Sphinx
               .\doc\make.bat html --verbose

         .. tab-item:: Generating LaTeX
            :sync: LaTeX

            .. code-block:: powershell

               cd <pyTooling>

               # Building documentation using Sphinx
               .\doc\make.bat latex --verbose

         .. tab-item:: Generating PDF (from LaTeX)
            :sync: PDF

            .. todo:: Describe LaTeX to PDF conversion on Windows using Miktex.

            .. hint:: A `Miktex installation <https://miktex.org/>`__ is required.


.. _INSTALL/building:

Local Packaging and Installation via PIP
****************************************

For development and bug fixing it might be handy to create a local wheel package and also install it locally on the
development machine. The following instructions will create a local wheel package (``*.whl``) and then use PIP to
install it. As a user might have a |PackageName| installation from PyPI, it's recommended to uninstall any previous
|PackageName| packages. (This step is also needed if installing an updated local wheel file with same version number.
PIP will not detect a new version and thus not overwrite/reinstall the updated package contents.)

Ensure :ref:`packaging requirements <DEP/packaging>` are installed.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         cd <pyTooling>

         # Package the code in a wheel (*.whl)
         python3 -m build --wheel

         # Uninstall the old package
         python3 -m pip uninstall -y pyTooling

         # Install from wheel
         python3 -m pip install ./dist/pyTooling-8.5.0-py3-none-any.whl

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         cd <pyTooling>

         # Package the code in a wheel (*.whl)
         py -m build --wheel

         # Uninstall the old package
         py -m pip uninstall -y pyTooling

         # Install from wheel
         py -m pip install .\dist\pyTooling-8.5.0-py3-none-any.whl

.. note::

   The legacy ways of building a package using ``setup.py bdist_wheel`` and installation using ``setup.py install`` is
   not recommended anymore.
