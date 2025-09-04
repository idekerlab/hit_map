=======
HIT-MAP
=======


|a| |b| |c|

.. |a| image:: https://img.shields.io/pypi/v/hit_map.svg
        :target: https://pypi.python.org/pypi/hit_map

.. |b| image:: https://app.travis-ci.com/idekerlab/hit_map.svg
        :target: https://app.travis-ci.com/idekerlab/hit_map

.. |c| image:: https://readthedocs.org/projects/hit-map/badge/?version=latest
        :target: https://hit-map.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




High-throuput generation and integration of multiscale proteomic dataa


* Free software: MIT license
* Documentation: https://hit-map.readthedocs.io.
* Source code: https://github.com/idekerlab/hit_map



Dependencies
------------

* `cellmaps_utils <https://pypi.org/project/cellmaps-utils>`__
* `deconwolf <https://github.com/elgw/deconwolf.git>`__

Compatibility
-------------

* Python 3.8+

Installation
------------

.. code-block::

   git clone https://github.com/idekerlab/hit_map
   cd hit_map
   pip install -r requirements_dev.txt
   make install


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

Usage
-----

For information invoke :code:`hit_mapcmd.py -h`

**Example usage**

**TODO:** Add information about example usage

.. code-block::

   hit_mapcmd.py # TODO Add other needed arguments here

For developers
-------------------------------------------

.. note::

    Commands below assume ``pip install -r requirements_dev.txt`` has been run

Run tests
~~~~~~~~~~

To run unit tests:

.. code-block::

    make test

To run tests in multiple python environments defined by ``tox.ini``:

.. code-block::

    make test-all

Continuous integration / Continuous development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``.travis.yml`` file is included in this
repo to easily enable continous integration / continuous development
via `Travis <https://travis-ci.com>`__

The configuration leverages `coverage <https://pypi.org/project/coverage/>`__
and `coveralls <https://coveralls.io>`__ to log
code coverage


Make documentation
~~~~~~~~~~~~~~~~~~~~

Documentation for this code is stored under ``docs/`` and can
be easily configured for display on `Read the Docs <https://readthedocs.io>`__
once the repo is linked from within `Read the Docs <https://readthedocs.io>`__
via github account

Command below requires additional packages that can be installed
with this command:

.. code-block::

    pip install -r docs/requirements.txt

Running the command below creates html documentation under
``docs/_build/html`` that is displayed to the user via
"default" browser

.. code-block::

    make docs


To deploy development versions of this package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below are steps to make changes to this code base, deploy, and then run
against those changes.

#. Make changes

   Modify code in this repo as desired

#. Build and deploy

.. code-block::

    # From base directory of this repo hit_map
    pip uninstall hit_map -y ; make clean dist; pip install dist/hit_map*whl



Needed files
------------

**TODO:** Add description of needed files


Via Docker
~~~~~~~~~~~~~~~~~~~~~~

**Example usage**

**TODO:** Add information about example usage


.. code-block::

   Coming soon ...

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _NDEx: http://www.ndexbio.org
