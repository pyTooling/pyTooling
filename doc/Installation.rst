.. _INSTALL:

Installation/Updates
####################

.. _INSTALL/pip:

Using PIP to Install from PyPI
******************************

The following instruction are using PIP (Package Installer for Python) as a package manager and PyPI (Python Package
Index) as a source of Python packages.


.. _INSTALL/pip/install:

Installing a Wheel Package from PyPI using PIP
==============================================

Users of pyTooling can select if the want to install a basic variant of pyTooling or an enhanced variant with support
for colored console/terminal outputs (``terminal``) and/or support for YAML configuration files (``yaml``). In these
cases additional dependencies might be installed. See :ref:`DEP` for more details.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: Normal Installation
            :sync: Normal

            .. code-block:: bash

               # Basic pyTooling package
               pip3 install pyTooling

         .. tab-item:: With Packaging Support
            :sync: Packaging

            .. code-block:: bash

               # With setuptools support for pyTooling.Packaging
               pip3 install pyTooling[packaging]

         .. tab-item:: With Colored Console/Terminal Support
            :sync: Terminal

            .. code-block:: bash

               # With color support for pyTooling.TerminalUI
               pip3 install pyTooling[terminal]

         .. tab-item:: With YAML Support for Configuration Files
            :sync: YAML

            .. code-block:: bash

               # With YAML support for pyTooling.Configuration.YAML
               pip3 install pyTooling[yaml]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: Normal Installation
            :sync: Normal

            .. code-block:: powershell

               # Basic pyTooling package
               pip install pyTooling

         .. tab-item:: With Packaging Support
            :sync: Packaging

            .. code-block:: powershell

               # With setuptools support for pyTooling.Packaging
               pip install pyTooling[packaging]

         .. tab-item:: With Colored Console/Terminal Support
            :sync: Terminal

            .. code-block:: powershell

               # With color support for pyTooling.TerminalUI
               pip install pyTooling[terminal]

         .. tab-item:: With YAML Support for Configuration Files
            :sync: YAML

            .. code-block:: powershell

               # With YAML support for pyTooling.Configuration.YAML
               pip install pyTooling[yaml]

Developers can install further dependencies for documentation generation (``doc``) or running unit tests (``test``) or
just all (``all``) dependencies.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
           :sync: Doc

            .. code-block:: bash

               # Install with dependencies to generate documentation
               pip3 install pyTooling[doc]

         .. tab-item:: With Unit Testing Dependencies
           :sync: Unit

            .. code-block:: bash

               # Install with dependencies to run unit tests
               pip3 install pyTooling[test]

         .. tab-item:: All Developer Dependencies
           :sync: All

            .. code-block:: bash

               # Install with all developer dependencies
               pip install pyTooling[all]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
           :sync: Doc

            .. code-block:: powershell

               # Install with dependencies to generate documentation
               pip install pyTooling[doc]

         .. tab-item:: With Unit Testing Dependencies
           :sync: Unit

            .. code-block:: powershell

               # Install with dependencies to run unit tests
               pip install pyTooling[test]

         .. tab-item:: All Developer Dependencies
           :sync: All

            .. code-block:: powershell

               # Install with all developer dependencies
               pip install pyTooling[all]


.. _INSTALL/pip/update:

Updating from PyPI using PIP
============================

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         pip install -U pyTooling

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U pyTooling


.. _INSTALL/pip/uninstall:

Uninstallation using PIP
========================

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         pip uninstall pyTooling

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 uninstall pyTooling


.. _INSTALL/setup:

Using ``setup.py`` (legacy)
***************************

See sections above on how to use PIP.

Installation using ``setup.py``
===============================

.. code-block:: bash

   setup.py install


.. _INSTALL/building:

Local Packaging and Installation via PIP
****************************************

For development and bug fixing it might be handy to create a local wheel package and also install it locally on the
development machine. The following instructions will create a local wheel package (``*.whl``) and then use PIP to
install it. As a user might have a pyTooling installation from PyPI, it's recommended to uninstall any previous
pyTooling packages. (This step is also needed if installing an updated local wheel file with same version number. PIP
will not detect a new version and thus not overwrite/reinstall the updated package contents.)

Ensure :ref:`packaging requirements <DEP/packaging>` are installed.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         cd <pyTooling>

         # Package the code in a wheel (*.whl)
         python -m build --wheel

         # Uninstall the old package
         python -m pip uninstall -y pyTooling

         # Install from wheel
         python -m pip install ./dist/pyTooling-4.1.0-py3-none-any.whl

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         cd <pyTooling>

         # Package the code in a wheel (*.whl)
         py -m build --wheel

         # Uninstall the old package
         py -m pip uninstall -y pyTooling

         # Install from wheel
         py -m pip install .\dist\pyTooling-4.1.0-py3-none-any.whl
