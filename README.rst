===========================
CellMaps Annotate Hierarchy
===========================


.. image:: https://img.shields.io/pypi/v/cellmaps_annotate_hierarchy.svg
        :target: https://pypi.python.org/pypi/cellmaps_annotate_hierarchy

.. image:: https://img.shields.io/travis/idekerlab/cellmaps_annotate_hierarchy.svg
        :target: https://travis-ci.com/idekerlab/cellmaps_annotate_hierarchy

.. image:: https://readthedocs.org/projects/cellmaps-annotate-hierarchy/badge/?version=latest
        :target: https://cellmaps-annotate-hierarchy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python Boilerplate contains all the boilerplate you need to create a Python package with command line


* Free software: MIT license
* Documentation: https://cellmaps-annotate-hierarchy.readthedocs.io.



Dependencies
------------

* TODO add

Compatibility
-------------

* Python 3.3+

Installation
------------

.. code-block::

   git clone https://github.com/idekerlab/cellmaps_annotate_hierarchy
   cd cellmaps_annotate_hierarchy
   make dist
   pip install dist/cellmaps_annotate_hierarchycmd*whl


Run **make** command with no arguments to see other build/deploy options including creation of Docker image 

.. code-block::

   make

Output:

.. code-block::

   clean                remove all build, test, coverage and Python artifacts
   clean-build          remove build artifacts
   clean-pyc            remove Python file artifacts
   clean-test           remove test and coverage artifacts
   lint                 check style with flake8
   test                 run tests quickly with the default Python
   test-all             run tests on every Python version with tox
   coverage             check code coverage quickly with the default Python
   docs                 generate Sphinx HTML documentation, including API docs
   servedocs            compile the docs watching for changes
   testrelease          package and upload a TEST release
   release              package and upload a release
   dist                 builds source and wheel package
   install              install the package to the active Python's site-packages
   dockerbuild          build docker image and store in local repository
   dockerpush           push image to dockerhub

For developers
-------------------------------------------

To deploy development versions of this package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below are steps to make changes to this code base, deploy, and then run
against those changes.

#. Make changes

   Modify code in this repo as desired

#. Build and deploy

.. code-block::

    # From base directory of this repo cellmaps_annotate_hierarchy
    pip uninstall cellmaps_annotate_hierarchy -y ; make clean dist; pip install dist/cellmaps_annotate_hierarchy*whl



Needed files
------------

**TODO:** Add description of needed files


Usage
-----

For information invoke :code:`cellmaps_annotate_hierarchycmd.py -h`

**Example usage**

**TODO:** Add information about example usage

.. code-block::

   cellmaps_annotate_hierarchycmd.py # TODO Add other needed arguments here


Via Docker
~~~~~~~~~~~~~~~~~~~~~~

**Example usage**

**TODO:** Add information about example usage


.. code-block::

   docker run -v `pwd`:`pwd` -w `pwd` idekerlab/cellmaps_annotate_hierarchy:0.1.0 cellmaps_annotate_hierarchycmd.py # TODO Add other needed arguments here


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _NDEx: http://www.ndexbio.org
