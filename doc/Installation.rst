.. _installation:

Installation/Updates
####################

.. _installation-pip:

Using PIP to Install from PyPI
******************************

The following instruction are using PIP (Package Installer for Python) as a package manager and PyPI (Python Package
Index) as a source of Python packages.

Installing a Wheel Package from PyPI using PIP
==============================================

Users of pyTooling can select if the want to install a basic variant of pyTooling or an enhanced variant with support
for colored console/terminal outputs (``terminal``) and/or support for YAML configuration files (``yaml``). In these
cases additional dependencies might be installed. See :ref:`dependency` for more details.

.. tab:: Linux/MacOS

   .. tab:: Normal Installation

      .. code-block:: bash

         # Basic pyTooling package
         pip3 install pyTooling

   .. tab:: With Colored Console/Terminal Support

      .. code-block:: bash

         # With color support for pyTooling.TerminalUI
         pip3 install pyTooling[terminal]

   .. tab:: With YAML Support for Configuration Files

      .. code-block:: bash

         # With YAML support for pyTooling.Configuration.YAML
         pip3 install pyTooling[yaml]

.. tab:: Windows

   .. tab:: Normal Installation

      .. code-block:: powershell

         # Basic pyTooling package
         pip install pyTooling

   .. tab:: With Colored Console/Terminal Support

      .. code-block:: powershell

         # With color support for pyTooling.TerminalUI
         pip install pyTooling[terminal]

   .. tab:: With YAML Support for Configuration Files

      .. code-block:: powershell

         # With YAML support for pyTooling.Configuration.YAML
         pip install pyTooling[yaml]

Developers can install further dependencies for documentation generation (``doc``) or running unit tests (``test``) or
just all (``all``) dependencies.

.. tab:: Linux/MacOS

   .. tab:: With Documentation Dependencies
      :new-set:

      .. code-block:: bash

         # Install with dependencies to generate documentation
         pip3 install pyTooling[doc]

   .. tab:: With Unit Testing Dependencies

      .. code-block:: bash

         # Install with dependencies to run unit tests
         pip3 install pyTooling[test]

   .. tab:: All Developer Dependencies

      .. code-block:: bash

         # Install with all developer dependencies
         pip install pyTooling[all]

.. tab:: Windows

   .. tab:: With Documentation Dependencies

      .. code-block:: powershell

         # Install with dependencies to generate documentation
         pip install pyTooling[doc]

   .. tab:: With Unit Testing Dependencies

      .. code-block:: powershell

         # Install with dependencies to run unit tests
         pip install pyTooling[test]

   .. tab:: All Developer Dependencies

      .. code-block:: powershell

         # Install with all developer dependencies
         pip install pyTooling[all]


Updating from PyPI using PIP
============================

.. tab:: Linux/MacOS

   .. code-block:: bash

      pip install -U pyTooling

.. tab:: Windows

   .. code-block:: powershell

      pip3 install -U pyTooling


Uninstallation using PIP
========================

.. tab:: Linux/MacOS

   .. code-block:: bash

      pip uninstall pyTooling

.. tab:: Windows

   .. code-block:: powershell

      pip3 uninstall pyTooling


.. _installation-setup:

Using ``setup.py`` (legacy)
***************************

See sections above on how to use PIP.

Installation using ``setup.py``
===============================

.. code-block:: bash

   setup.py install


.. _installation-building:

Local Packaging and Installation via PIP
****************************************

For development and bug fixing it might be handy to create a local wheel package and also install it locally on the
development machine. The following instructions will create a local wheel package (``*.whl``) and then use PIP to
install it. As a user might have a pyTooling installation from PyPI, it's recommended to uninstall any previous
pyTooling packages. (This step is also needed if installing an updated local wheel file with same version number. PIP
will not detect a new version and thus not overwrite/reinstall the updated package contents.)

Ensure :ref:`packaging requirements <dependency-packaging>` are installed.

.. tab:: Linux/MacOS
   :new-set:

   .. code-block:: bash

      cd <pyTooling>

      # Package the code in a wheel (*.whl)
      python -m build --wheel

      # Uninstall the old package
      python -m pip uninstall -y pyTooling

      # Install from wheel
      python -m pip install ./dist/pyTooling-4.1.0-py3-none-any.whl

.. tab:: Windows

   .. code-block:: powershell

      cd <pyTooling>

      # Package the code in a wheel (*.whl)
      py -m build --wheel

      # Uninstall the old package
      py -m pip uninstall -y pyTooling

      # Install from wheel
      py -m pip install .\dist\pyTooling-4.1.0-py3-none-any.whl
