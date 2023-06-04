.. _TERM:

Terminal
########

A set of helpers to implement a text user interface (TUI) in a terminal.

Introduction
************

This package offers a :class:`pyTooling.TerminalUI.LineTerminal` implementation, derived from a basic
:class:`pyTooling.TerminalUI.Terminal` class. It eases the creation of simple terminal/console applications. It
includes colored outputs based on `colorama`.

List of base-classes
********************

* :class:`pyTooling.TerminalUI.Terminal`
* :class:`pyTooling.TerminalUI.LineTerminal`


Example
*******

.. code-block:: Python

   from pyTooling.TerminalUI import LineTerminal

   class Application(LineTerminal):
     def __init__(self):
       super().__init__(verbose=True, debug=True, quiet=False)

     def run(self):
       self.WriteQuiet("This is a quiet message.")
       self.WriteNormal("This is a normal message.")
       self.WriteInfo("This is an info message.")
       self.WriteDebug("This is a debug message.")
       self.WriteWarning("This is a warning message.")
       self.WriteError("This is an error message.")
       self.WriteFatal("This is a fatal message.")

   # entry point
   if __name__ == "__main__":
     Application.versionCheck((3,6,0))
     app = Application()
     app.run()
     app.exit()


Line
####

``Line`` represents a single line in a line-based terminal application. If a
line is visible, depends on the :class:`~pyTooling.TerminalUI.Severity`-level of a
``Line`` object.
