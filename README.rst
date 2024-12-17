===========================
CellMaps Annotate Hierarchy
===========================


.. image:: https://img.shields.io/pypi/v/cellmaps_annotate_hierarchy.svg
        :target: https://pypi.python.org/pypi/cellmaps_annotate_hierarchy

.. image:: https://img.shields.io/travis/idekerlab/cellmaps_annotate_hierarchy.svg
        :target: https://travis-ci.com/idekerlab/cellmaps_annotate_hierarchy

.. image:: https://readthedocs.org/projects/cellmaps-annotate-hierarchy/badge/?version=latest
..        :target: https://cellmaps-annotate-hierarchy.readthedocs.io/en/latest/?badge=latest
..     :alt: Documentation Status




Python Boilerplate contains all the boilerplate you need to create a Python package with command line


* Free software: MIT license
.. * Documentation: https://cellmaps-annotate-hierarchy.readthedocs.io.



Dependencies
------------

**Set up an environment**

.. code-block::

    conda create -n gpt_env python=3.11.5
    conda activate gpt_env
    pip install -r requirements.txt

NOTE: 12/17/2024: openai required an httpx version that cause error, we need to manually downgrade httpx to 0.27.2 for now. 

**Set up an environment variable to store GPT-4 API key**

.. code-block::

    conda activate gpt_env
    conda env config vars set OPENAI_API_KEY="<your api key>"
    conda deactivate  # reactivate 
    
    conda activate gpt_env
    echo $OPENAI_API_KEY # make sure the key setup 

    # in python 
    %python
    import os
    import openai
     
    openai.api_key = os.environ["OPENAI_API_KEY"]

From OpenAI website for the best practice for API key safety: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety 


Compatibility
-------------

* Python 3.11+

Usage
-----

**Example usage**


**Check Notebook**  `GPT4_pipeline_Demo <./cellmaps_annotate_hierarchy/GPT4_pipeline_Demo.ipynb>`_


**Command line usage**


.. code-block::

   cd ./cellmaps_annotate_hierarchy
   python .query_llm_for_analysis.py --config ./gpt4_config.json \
            --initialize \
            --input ./data/example_NeST_table_sub.tsv \
            --input_sep  ','\
            --set_index 'NEST ID' \
            --gene_column Genes\
            --gene_sep ',' \
            --start 0 \
            --end 27 \
            --output_file 'data/demo_commandline.tsv'




The instruction below is not ready for operation now (Sep 2023)
----------------------------------------------------------

Installation
--------------

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
