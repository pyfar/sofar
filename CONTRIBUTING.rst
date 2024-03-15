.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs and Submit Feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best way to report bugs of send feedback is to open an issue at https://github.com/pyfar/sofar/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Fix Bugs or Implement Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" or
"enhancement" is open to whoever wants to implement it. It might be good to
contact us first, to see if anyone is already working on it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

sofar could always use more documentation, whether as part of the
official sofar docs, in docstrings, or even on the web in blog posts,
articles, and such.

Get Started!
------------

Ready to contribute? Here's how to set up `sofar` for local development.

1. Fork the `sofar` repo on GitHub.
2. Clone your fork locally and cd into the sofar directory::

    $ git clone --recursive https://github.com/pyfar/sofar.git
    $ cd sofar/

3. Note that some graphical Git interfaces can not do the recursive clone. If the folder sofar/sofa_conventions is empty try

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

6. When you're done making changes, check that your changes pass flake8 and the
   tests::

    $ flake8 sofar tests
    $ pytest

   flake8 test must pass without any warnings for `./sofar` and `./tests` using the default or a stricter configuration. Flake8 ignores `E123/E133, E226` and `E241/E242` by default. If necessary adjust the your flake8 and linting configuration in your IDE accordingly.

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
3. The pull request should work for Python 3.7 and 3.8. Check
   https://travis-ci.com/pyfar/sofar/pull_requests
   and make sure that the tests pass for all supported Python versions.


Testing Guidelines
-----------------------
Sofar uses test-driven development based on `three steps <https://martinfowler.com/bliki/TestDrivenDevelopment.html>`_ and `continuous integration <https://en.wikipedia.org/wiki/Continuous_integration>`_ to test and monitor the code.
In the following, you'll find a guideline. Note: these instructions are not generally applicable outside of sofar.

- The main tool used for testing is `pytest <https://docs.pytest.org/en/stable/index.html>`_.
- All tests are located in the *tests/* folder.
- Make sure that all important parts of sofar are covered by the tests. This can be checked using *coverage* (see below).
- In case of sofar, mainly **state verification** is applied in the tests. This means that the outcome of a function is compared to a desired value (``assert ...``). For more information, it is refered to `Martin Fowler's article <https://martinfowler.com/articles/mocksArentStubs.html.>`_.

Tips
~~~~~~~~~~~
Pytest provides several, sophisticated functionalities which could reduce the effort of implementing tests.

- Similar tests executing the same code with different variables can be `parametrized <https://docs.pytest.org/en/stable/example/parametrize.html>`_.
- Feel free to add more recommendations on useful pytest functionalities here. Consider, that a trade-off between easy implemention and good readability of the tests needs to be found.

You can create an html report on the test `coverage <https://coverage.readthedocs.io/en/coverage-5.5/>`_ by calling

    $ pytest --cov=. --cov-report=html


Writing the Documentation
-------------------------

Sofar follows the `numpy style guide <https://numpydoc.readthedocs.io/en/stable/format.html>`_ for the docstring. A docstring has to consist at least of

- A short and/or extended summary,
- the Parameters section, and
- the Returns section

Optional fields that are often used are

- References,
- Examples, and
- Notes

Here are a few tips to make things run smoothly

- Use the tags ``:py:func:``, ``:py:mod:``, and ``:py:class:`` to reference sofar functions, modules, and classes: For example ``:py:func:`~sofar.write_sofa``` for a link that displays only the function name.
- Code snippets and values as well as external modules, classes, functions are marked by double ticks \`\` to appear in mono spaced font, e.g., ``x=3`` or ``sofar.Signal``.
- Parameters, returns, and attributes are marked by single ticks \` to appear as emphasized text, e.g., *unit*.
- Use ``[#]_`` and ``.. [#]`` to get automatically numbered footnotes.
- Do not use footnotes in the short summary. Only use footnotes in the extended summary if there is a short summary. Otherwise, it messes with the auto-footnotes.

See the `Sphinx homepage <https://www.sphinx-doc.org>`_ for more information.

Building the Documentation
--------------------------

You can build the documentation of your branch using Sphinx by executing the make script inside the docs folder.

.. code-block:: console

    $ cd docs/
    $ make html

After Sphinx finishes you can open the generated html using any browser

.. code-block:: console

    $ docs/_build/index.html

Note that some warnings are only shown the first time you build the
documentation. To show the warnings again use

.. code-block:: console

    $ make clean

before building the documentation.


Submodules
~~~~~~~~~~

To update the submodule containing the conventions and verification rules run

$ git submodule update --init --recursive
$ git submodule update --recursive --remote

and then commit the changes


Deploying
~~~~~~~~~

A reminder for the maintainers on how to deploy.

- Commit all changes to develop
- Update HISTORY.rst in develop
- Check if new contributors should be added to AUTHORS.rst
- Merge develop into main

Switch to main and run::

$ bumpversion patch --verbose # possible: major / minor / patch

Bumpversion will update all version strings, create and commit tags by default

$ git push --follow-tags

Continuous integration will then deploy to PyPI if tests pass.

- Merge main back into develop

