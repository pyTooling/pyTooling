.. _DEP:

Dependencies
############

.. |img-pyTooling-lib-status| image:: https://img.shields.io/librariesio/release/pypi/pyTooling
   :alt: Libraries.io status for latest release
   :height: 22
   :target: https://libraries.io/github/pyTooling/pyTooling
.. |img-pyTooling-vul-status| image:: https://img.shields.io/snyk/vulnerabilities/github/pyTooling/pyTooling
   :alt: Snyk Vulnerabilities for GitHub Repo
   :height: 22
   :target: https://img.shields.io/snyk/vulnerabilities/github/pyTooling/pyTooling

+------------------------------------------+------------------------------------------+
| `Libraries.io <https://libraries.io/>`_  | Vulnerabilities Summary                  |
+==========================================+==========================================+
| |img-pyTooling-lib-status|               | |img-pyTooling-vul-status|               |
+------------------------------------------+------------------------------------------+

.. _DEP/package:

pyTooling Package (Mandatory)
*****************************

.. rubric:: Manually Installing Package Requirements

Use the :file:`requirements.txt` file to install all dependencies via ``pip3`` or install the package directly from
PyPI (see :ref:`INSTALL`).

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r requirements.txt


.. rubric:: Dependency List

When installed as ``pyTooling``:

.. dependency-table:: ../requirements.txt
   :caption: Mandatory dependencies of the pyTooling package.
   :licenses: dependencies.yml


When installed as ``pyTooling[packaging]``:

.. dependency-table:: pyTooling[packaging]
   :caption: Dependencies added by the ``packaging`` extra.
   :licenses: dependencies.yml

When installed as ``pyTooling[terminal]``:

.. dependency-table:: pyTooling[terminal]
   :caption: Dependencies added by the ``terminal`` extra.
   :licenses: dependencies.yml


When installed as ``pyTooling[yaml]``:

.. dependency-table:: pyTooling[yaml]
   :caption: Dependencies added by the ``yaml`` extra.
   :licenses: dependencies.yml


.. _DEP/testing:

Unit Testing (Optional)
***********************

Unit Testing / Coverage / Type Checking (Optional)
==================================================

Additional Python packages needed for testing, code coverage collection and static type checking. These packages are
only needed for developers or on a CI server.


.. rubric:: Manually Installing Test Requirements

Use the :file:`tests/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively install
the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U -r tests/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U -r tests\requirements.txt

.. rubric:: Dependency List - Unit Testing

.. dependency-table:: ../tests/unit/requirements.txt
   :caption: Dependencies for unit testing, coverage and type checking.
   :licenses: dependencies.yml

Unit Testing with Benchmarking (Optional)
=========================================

Further Python packages are needed for benchmarking. These packages are only needed for developers or on a CI server,


.. rubric:: Manually Installing Benchmarking Requirements

Use the :file:`tests/benchmark/requirements.txt` file to install all dependencies via ``pip3``. The file will
recursively install the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U -r tests/benchmark/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U -r tests\benchmark\requirements.txt

.. rubric:: Dependency List - With Benchmark Testing

.. dependency-table:: ../tests/benchmark/requirements.txt
   :caption: Dependencies for benchmark testing.
   :licenses: dependencies.yml

Unit Testing with Performance Testing (Optional)
================================================

Further Python packages are needed for performance testing (comparison). These packages are only needed for developers
or on a CI server, 

.. rubric:: Manually Installing Benchmarking Requirements

Use the :file:`tests/performance/requirements.txt` file to install all dependencies via ``pip3``. The file will
recursively install the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U -r tests/performance/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U -r tests\performance\requirements.txt

.. rubric:: Dependency List - With Performance Testing

.. dependency-table:: ../tests/performance/requirements.txt
   :caption: Dependencies for performance testing.
   :licenses: dependencies.yml



.. _DEP/documentation:

Sphinx Documentation (Optional)
*******************************

Additional Python packages needed for documentation generation. These packages are only needed for developers or on a
CI server, 


.. rubric:: Manually Installing Documentation Requirements

Use the :file:`doc/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively install
the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U -r doc/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U -r doc\requirements.txt


.. rubric:: Dependency List

.. dependency-table:: requirements.txt
   :caption: Dependencies for building this documentation.
   :licenses: dependencies.yml

.. _DEP/packaging:

Packaging (Optional)
********************

Additional Python packages needed for installation package generation. These packages are only needed for developers or
on a CI server, 


.. rubric:: Manually Installing Packaging Requirements

Install the ``packaging`` extra with ``pip3``, which installs the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U pyTooling[packaging]

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U pyTooling[packaging]


.. rubric:: Dependency List

.. dependency-table:: pyTooling[packaging]
   :caption: Dependencies for generating an installation package.
   :licenses: dependencies.yml


.. _DEP/publishing:

Publishing (CI-Server only)
***************************

Additional Python packages needed for publishing the generated installation package to e.g, PyPI or any equivalent
services. These packages are only needed for maintainers or on a CI server.


.. rubric:: Manually Installing Publishing Requirements

Use the :file:`dist/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively
install the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip install -U -r dist/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U -r dist\requirements.txt


.. rubric:: Dependency List

.. dependency-table:: ../dist/requirements.txt
   :caption: Dependencies for publishing the package.
   :licenses: dependencies.yml
