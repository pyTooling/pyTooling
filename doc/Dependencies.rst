.. _dependency:

Dependencies
############

.. |img-pyMetaClasses-lib-status| image:: https://img.shields.io/librariesio/release/pypi/pyTooling
   :alt: Libraries.io status for latest release
   :height: 22
   :target: https://libraries.io/github/pyTooling/pyTooling
.. |img-pyMetaClasses-req-status| image:: https://img.shields.io/requires/github/pyTooling/pyTooling
   :alt: Requires.io
   :height: 22
   :target: https://requires.io/github/pyTooling/pyTooling/requirements/?branch=master

+------------------------------------------+------------------------------------------+
| `Libraries.io <https://libraries.io/>`_  | `Requires.io <https://requires.io/>`_    |
+==========================================+==========================================+
| |img-pyMetaClasses-lib-status|           | |img-pyMetaClasses-req-status|           |
+------------------------------------------+------------------------------------------+

.. _dependency-package:

pyTooling Package (Mandatory)
*****************************

.. rubric:: Manually Installing Package Requirements

Use the :file:`requirements.txt` file to install all dependencies via ``pip3``
or install the package directly from PyPI (see :ref:`INSTALL`).

.. code-block:: shell

   pip3 install -U -r requirements.txt


.. rubric:: Dependency List

*None*

.. #+-----------------------------------------------------+-------------+---------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | **Package**                                         | **Version** | **License**                                                         | **Dependencies**                                                                                                                |
    +=====================================================+=============+=====================================================================+=================================================================================================================================+
    | `pydecor <https://github.com/mplanchard/pydecor>`__ | ≥2.0.1      | `MIT <https://github.com/mplanchard/pydecor/blob/master/LICENSE>`__ | * `dill <https://github.com/uqfoundation/dill>`__ (`BSD 3-clause <https://github.com/uqfoundation/dill/blob/master/LICENSE>`__) |
    |                                                     |             |                                                                     | * `six <https://github.com/benjaminp/six>`__ (`MIT <https://github.com/benjaminp/six/blob/master/LICENSE>`__)                   |
    +-----------------------------------------------------+-------------+---------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+


.. _dependency-testing:

Unit Testing / Coverage (Optional)
**********************************

Additional Python packages needed for testing and code coverage collection.
These packages are only needed for developers or on a CI server, thus
sub-dependencies are not evaluated further.


.. rubric:: Manually Installing Test Requirements

Use the :file:`tests/requirements.txt` file to install all dependencies via
``pip3``. The file will recursively install the mandatory dependencies too.

.. code-block:: shell

   pip3 install -U -r tests/requirements.txt


.. rubric:: Dependency List

+-----------------------------------------------------------+-------------+----------------------------------------------------------------------------------------+----------------------+
| **Package**                                               | **Version** | **License**                                                                            | **Dependencies**     |
+===========================================================+=============+========================================================================================+======================+
| `pytest <https://github.com/pytest-dev/pytest>`__         | ≥6.2.4      | `MIT <https://github.com/pytest-dev/pytest/blob/master/LICENSE>`__                     | *Not yet evaluated.* |
+-----------------------------------------------------------+-------------+----------------------------------------------------------------------------------------+----------------------+
| `pytest-cov <https://github.com/pytest-dev/pytest-cov>`__ | ≥2.12.1     | `MIT <https://github.com/pytest-dev/pytest-cov/blob/master/LICENSE>`__                 | *Not yet evaluated.* |
+-----------------------------------------------------------+-------------+----------------------------------------------------------------------------------------+----------------------+
| `Coverage <https://github.com/nedbat/coveragepy>`__       | ≥5.5        | `Apache License, 2.0 <https://github.com/nedbat/coveragepy/blob/master/LICENSE.txt>`__ | *Not yet evaluated.* |
+-----------------------------------------------------------+-------------+----------------------------------------------------------------------------------------+----------------------+


.. _dependency-documentation:

Sphinx Documentation (Optional)
*******************************

Additional Python packages needed for documentation generation. These packages
are only needed for developers or on a CI server, thus sub-dependencies are not
evaluated further.


.. rubric:: Manually Installing Documentation Requirements

Use the :file:`doc/requirements.txt` file to install all dependencies via
``pip3``. The file will recursively install the mandatory dependencies too.

.. code-block:: shell

   pip3 install -U -r doc/requirements.txt


.. rubric:: Dependency List

+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
| **Package**                                                                                     | **Version**  | **License**                                                                                              | **Dependencies**     |
+=================================================================================================+==============+==========================================================================================================+======================+
| `Sphinx <https://github.com/sphinx-doc/sphinx>`__                                               | ≥4.1.1       | `BSD 3-Clause <https://github.com/sphinx-doc/sphinx/blob/master/LICENSE>`__                              | *Not yet evaluated.* |
+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
| `sphinx_btd_theme <https://github.com/buildthedocs/sphinx.theme>`__                             | ≥0.5.2       | `MIT <https://github.com/buildthedocs/sphinx.theme/blob/master/LICENSE>`__                               | *Not yet evaluated.* |
+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
| !! `sphinx_fontawesome <https://github.com/fraoustin/sphinx_fontawesome>`__                     | ≥0.0.6       | `GPL 2.0 <https://github.com/fraoustin/sphinx_fontawesome/blob/master/LICENSE>`__                        | *Not yet evaluated.* |
+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
| `sphinx_autodoc_typehints <https://github.com/agronholm/sphinx-autodoc-typehints>`__            | ≥1.12.0      | `MIT <https://github.com/agronholm/sphinx-autodoc-typehints/blob/master/LICENSE>`__                      | *Not yet evaluated.* |
+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
| `Pygments <https://github.com/pygments/pygments>`__                                             | ≥2.9.0       | `BSD 2-Clause <https://github.com/pygments/pygments/blob/master/LICENSE>`__                              | *Not yet evaluated.* |
+-------------------------------------------------------------------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+----------------------+
