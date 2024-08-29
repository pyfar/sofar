.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given. The following helps you to start
contributing specifically to sofar. Please also consider the
`general contributing guidelines`_ for example regarding the style
of code and documentation and some helpful hints.

Types of Contributions
----------------------

Report Bugs or Suggest Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best place for this is https://github.com/pyfar/sofar/issues.

Fix Bugs or Implement Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look through https://github.com/pyfar/sofar/issues for bugs or feature request
and contact us or comment if you are interested in implementing.

Write Documentation
~~~~~~~~~~~~~~~~~~~

sofar could always use more documentation, whether as part of the
official sofar docs, in docstrings, or even on the web in blog posts,
articles, and such.

Get Started!
------------

Ready to contribute? Here's how to set up `sofar` for local development using the command-line interface. Note that several alternative user interfaces exist, e.g., the Git GUI, `GitHub Desktop <https://desktop.github.com/>`_, extensions in `Visual Studio Code <https://code.visualstudio.com/>`_ ...

1. `Fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo/>`_ the `sofar` repo on GitHub.
2. Clone your fork locally and cd into the sofar directory::

    $ git clone --recursive https://github.com/YOUR_USERNAME/sofar.git
    $ cd sofar

3. Note that some graphical Git interfaces can not do the recursive clone. If the folder sofar/sofa_conventions is empty try::

    $ git submodule update --init

4. Install your local copy into a virtualenv. Assuming you have Anaconda or Miniconda installed, this is how you set up your fork for local development::

    $ conda create --name sofar python
    $ conda activate sofar
    $ conda install pip
    $ pip install -e .
    $ pip install -r requirements_dev.txt

5. Create a branch for local development. Indicate the intention of your branch in its respective name (i.e. `feature/branch-name` or `bugfix/branch-name`)::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass ruff and the
   tests::

    $ ruff check
    $ pytest

   ruff must pass without any warnings for `./sofar` and `./tests` using the default or a stricter configuration. Ruff ignores a couple of PEP Errors (see `./pyproject.toml`). If necessary, adjust your linting configuration in your IDE accordingly.

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request on the develop branch through the GitHub website.


Submodules
~~~~~~~~~~

To update the submodule containing the conventions and verification rules run

.. code-block:: bash

    $ git submodule update --init --recursive
    $ git submodule update --recursive --remote

and then commit the changes

.. _general contributing guidelines: https://pyfar-gallery.readthedocs.io/en/latest/contribute/index.html
