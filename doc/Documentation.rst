.. _DOC:

Overview
########

The :mod:`pyTooling.Documentation` package provides helper functions to work with **doc-strings** - the text a Python
entity documents itself with.

.. _DOC/splitDocString:

splitDocString
##############

.. grid:: 2

   .. grid-item::
      :columns: 6

      :func:`~pyTooling.Documentation.splitDocString` dedents a doc-string with :func:`inspect.cleandoc` and returns
      its **summary** - the first paragraph - and its **body** - whatever follows the first blank line.

      A doc-string of ``None`` yields two empty strings, and a single-paragraph doc-string yields an empty body, so a
      caller needs no special case for either.

      It is a function rather than a decorator, because the same split serves three unrelated purposes:
      :deco:`~pyTooling.Decorators.InheritDocString` expresses its merge strategies in it,
      :func:`~pyTooling.Packaging.extractVersionInformation` reads a package's short description with it, and
      :deco:`~pyTooling.Testing.testcase` reads a testcase's summary with it.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyTooling.Documentation import splitDocString

         summary, body = splitDocString(MyClass.__doc__)

.. _DOC/SummaryLength:

How long a summary may be
=========================

.. grid:: 2

   .. grid-item::
      :columns: 6

      A summary is a single sentence, so it is length-limited. The default of
      :data:`~pyTooling.Documentation.MAXIMUM_SUMMARY_LENGTH` characters leaves room for a sentence of the
      usual 120 columns plus an embedded link or other markup. A longer first paragraph is a body that lost its
      summary, and a :exc:`~pyTooling.Documentation.DocumentationError` says so.

      Pass :pycode:`0` where the limit doesn't apply - which is what
      :deco:`~pyTooling.Decorators.InheritDocString` does, because a base-class' doc-string belongs to whoever wrote
      it and rejecting it would turn a documentation style issue into an :exc:`ImportError` in a package that merely
      derives from that class.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyTooling.Documentation import splitDocString

         # Rejects a first paragraph longer than 200 characters.
         summary, body = splitDocString(docString)

         # Accepts any length.
         summary, body = splitDocString(docString, maxSummaryLength=0)

         # Any other bound.
         summary, body = splitDocString(docString, maxSummaryLength=80)
