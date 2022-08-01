.. _installation:

Installation/Updates
####################

.. _installation-pip:

Using PIP
*********

Installation from PyPI using PIP
================================

.. code-block:: bash

   # Basic pyTooling package
   pip3 install pyTooling

   # With YAML support for pyTooling.Configuration.YAML
   pip3 install pyTooling[yaml]


Updating from PyPI using PIP
============================

.. code-block:: bash

   pip3 install -U pyTooling


Uninstallation using PIP
========================

.. code-block:: bash

   pip3 uninstall pyTooling


Installation from local directory using PIP
===========================================

.. code-block:: bash

   pip3 install .


.. _installation-setup:

Using ``setup.py`` (legacy)
***************************

See sections above on how to use PIP.

Installation using ``setup.py``
===============================

.. code-block:: bash

   setup.py install
