# ==================================================================================================================== #
#             _____           _ _               ____                 _                                                 #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ __ __ _ _ __ | |__                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |  _| '__/ _` | '_ \| '_ \                                             #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |_| | | | (_| | |_) | | | |                                            #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_|  \__,_| .__/|_| |_|                                            #
# |_|    |___/                          |___/                 |_|                                                      #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Unit tests for :mod:`pyTooling.Graph.GraphViz`: writing a graph in the DOT language.
"""
from pyTooling.Graph.GraphViz import GraphKind, HTMLLabel, RecordLabel, DefaultAttributes, Node, Edge, quote
from pyTooling.Testing        import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Quoting(Testcase):
	def test_Quote(self) -> None:
		for text, expected in (
			("plain",       '"plain"'),
			("",            '""'),
			('say "hi"',    '"say \\"hi\\""'),
			("a\\l",        '"a\\\\l"'),
			("two\nlines",  '"two\\nlines"'),
		):
			with self.subTest(text=text):
				self.assertEqual(expected, quote(text))

	def test_Text_Parameters(self) -> None:
		for function in (quote, HTMLLabel.Escape, RecordLabel.Escape):
			for text, exceptionType, message in (
				(None, ValueError, "Parameter 'text' is None."),
				(1,    TypeError,  "Parameter 'text' is not of type 'str'."),
			):
				with self.subTest(function=function.__qualname__, message=message):
					with self.assertRaises(exceptionType) as context:
						function(text)
					self.assertEqual(message, str(context.exception))

	def test_GraphKind(self) -> None:
		self.assertEqual("digraph", GraphKind.Directed.Keyword)
		self.assertEqual("->", GraphKind.Directed.EdgeOperator)
		self.assertEqual("graph", GraphKind.Undirected.Keyword)
		self.assertEqual("--", GraphKind.Undirected.EdgeOperator)


class Labels(Testcase):
	def test_HTMLLabel(self) -> None:
		label = HTMLLabel(f"<b>{HTMLLabel.Escape('a < b & c')}</b>")

		self.assertEqual("<b>a &lt; b &amp; c</b>", label.Markup)
		self.assertEqual("<<b>a &lt; b &amp; c</b>>", str(label))

	def test_HTMLLabel_Parameters(self) -> None:
		with self.assertRaises(ValueError) as context:
			HTMLLabel(None)
		self.assertEqual("Parameter 'markup' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			HTMLLabel(1)
		self.assertEqual("Parameter 'markup' is not of type 'str'.", str(context.exception))

	def test_RecordLabel(self) -> None:
		for label, expected in (
			(RecordLabel(["a", "b"]),                             '"a|b"'),
			(RecordLabel(("a", "b"), flipped=True),               '"{a|b}"'),
			(RecordLabel(["a", RecordLabel(["b", "c"])]),         '"a|{b|c}"'),
			(RecordLabel(["«T»", ["x", "y"], []], flipped=True),  '"{«T»|x\\ly\\l| }"'),
			(RecordLabel(['a|b {c} <d> "e" \\']),                 '"a\\|b \\{c\\} \\<d\\> \\"e\\" \\\\"'),
		):
			with self.subTest(expected=expected):
				self.assertEqual(expected, str(label))

	def test_RecordLabel_Fields(self) -> None:
		nested = RecordLabel(["b"])
		label = RecordLabel(("a", ["r"], nested), flipped=True)

		self.assertListEqual(["a", ["r"], nested], label.Fields)
		self.assertTrue(label.Flipped)

	def test_RecordLabel_Parameters(self) -> None:
		for fields, flipped, exceptionType, message in (
			(None,        False, ValueError, "Parameter 'fields' is None."),
			("ab",        False, TypeError,  "Parameter 'fields' is not a sequence ('list', 'tuple', ...)."),
			({"a"},       False, TypeError,  "Parameter 'fields' is not a sequence ('list', 'tuple', ...)."),
			([],          False, ValueError, "Parameter 'fields' is empty."),
			(["a", None], False, ValueError, "Parameter 'fields' contains None."),
			(["a", 1],    False, TypeError,  "Parameter 'fields' contains a field of an unsupported type."),
			(["a", [1]],  False, TypeError,  "Parameter 'fields' contains a field of an unsupported type."),
			(["a"],       None,  ValueError, "Parameter 'flipped' is None."),
			(["a"],       1,     TypeError,  "Parameter 'flipped' is not of type 'bool'."),
		):
			with self.subTest(message=message, fields=fields):
				with self.assertRaises(exceptionType) as context:
					RecordLabel(fields, flipped)
				self.assertEqual(message, str(context.exception))


class Attributes(Testcase):
	def test_DictionarySyntax(self) -> None:
		node = Node("n", attributes={"color": "red"})
		node["shape"] = "box"

		self.assertIn("shape", node)
		self.assertEqual("box", node["shape"])
		self.assertEqual(2, len(node))
		self.assertDictEqual({"color": "red", "shape": "box"}, node.Attributes)

		del node["color"]
		self.assertNotIn("color", node)
		with self.assertRaises(KeyError):
			_ = node["color"]

	def test_Values(self) -> None:
		node = Node("n", attributes={
			"s": "text", "i": 1, "f": 0.5, "t": True, "n": False, "h": HTMLLabel("<b>x</b>"), "r": RecordLabel(["a", "b"])
		})

		self.assertEqual(
			'"n" [s="text", i=1, f=0.5, t=true, n=false, h=<<b>x</b>>, r="a|b"];\n',
			node.ToStringLines(0)[0]
		)

	def test_Parameters(self) -> None:
		node = Node("n")
		for name, value, exceptionType, message in (
			(None, "x",  ValueError, "Parameter 'name' is None."),
			(1,    "x",  TypeError,  "Parameter 'name' is not of type 'str'."),
			("",   "x",  ValueError, "Parameter 'name' is empty."),
			("a",  None, ValueError, "Parameter 'value' is None."),
			("a",  [1],  TypeError,  "Parameter 'value' is not of a supported attribute type."),
		):
			with self.subTest(message=message, name=name):
				with self.assertRaises(exceptionType) as context:
					node[name] = value
				self.assertEqual(message, str(context.exception))

	def test_Mapping(self) -> None:
		with self.assertRaises(TypeError) as context:
			Node("n", attributes=[("color", "red")])
		self.assertEqual("Parameter 'attributes' is not a mapping ('dict', ...).", str(context.exception))

		for attributes, exceptionType, message in (
			({1: "x"},        TypeError,  "Parameter 'name' is not of type 'str'."),
			({"color": [1]},  TypeError,  "Parameter 'value' is not of a supported attribute type."),
			({"color": None}, ValueError, "Parameter 'value' is None."),
		):
			with self.subTest(message=message):
				with self.assertRaises(exceptionType) as context:
					Edge(Node("a"), Node("b"), attributes)
				self.assertEqual(message, str(context.exception))
				self.assertIn("of parameter 'attributes'.", context.exception.__notes__[-1])

	def test_DefaultAttributes(self) -> None:
		defaults = DefaultAttributes("node")
		self.assertListEqual([], defaults.ToStringLines())

		defaults["shape"] = "box"
		self.assertListEqual(['  node [shape="box"];\n'], defaults.ToStringLines())

	def test_DefaultAttributes_Parameters(self) -> None:
		for keyword, exceptionType, message in (
			(None,    ValueError, "Parameter 'keyword' is None."),
			(1,       TypeError,  "Parameter 'keyword' is not of type 'str'."),
			("graph", ValueError, "Parameter 'keyword' is neither 'node' nor 'edge'."),
		):
			with self.subTest(message=message):
				with self.assertRaises(exceptionType) as context:
					DefaultAttributes(keyword)
				self.assertEqual(message, str(context.exception))


class Elements(Testcase):
	def test_Node(self) -> None:
		node = Node("a b", "A")

		self.assertEqual("a b", node.Identifier)
		self.assertListEqual(['  "a b" [label="A"];\n'], node.ToStringLines())
		self.assertListEqual(['"plain";\n'], Node("plain").ToStringLines(0))
		record = Node("r", RecordLabel(["a", "b"]), {"shape": "record"})
		self.assertListEqual(['  "r" [shape="record", label="a|b"];\n'], record.ToStringLines())

	def test_Node_Parameters(self) -> None:
		for identifier, exceptionType, message in (
			(None, ValueError, "Parameter 'identifier' is None."),
			(1,    TypeError,  "Parameter 'identifier' is not of type 'str'."),
			("",   ValueError, "Parameter 'identifier' is empty."),
		):
			with self.subTest(message=message, identifier=identifier):
				with self.assertRaises(exceptionType) as context:
					Node(identifier)
				self.assertEqual(message, str(context.exception))

		with self.assertRaises(TypeError) as context:
			Node("a", 1)
		self.assertEqual("Parameter 'label' is not of type 'str', 'HTMLLabel' or 'RecordLabel'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			Node("a", "A", {"label": "B"})
		self.assertEqual("Parameters 'label' and 'attributes' both set a label.", str(context.exception))

	def test_Edge(self) -> None:
		a, b = Node("a"), Node("b")
		edge = Edge(a, b, {"label": "e"})

		self.assertIs(a, edge.Source)
		self.assertIs(b, edge.Target)
		self.assertListEqual(['  "a" -> "b" [label="e"];\n'], edge.ToStringLines())
		self.assertListEqual(['"a" -- "b" [label="e"];\n'], edge.ToStringLines(GraphKind.Undirected, 0))

	def test_Edge_Parameters(self) -> None:
		node = Node("a")
		for source, target, exceptionType, message in (
			(None, node, ValueError, "Parameter 'source' is None."),
			("a",  node, TypeError,  "Parameter 'source' is not of type 'Node'."),
			(node, None, ValueError, "Parameter 'target' is None."),
			(node, "b",  TypeError,  "Parameter 'target' is not of type 'Node'."),
		):
			with self.subTest(message=message):
				with self.assertRaises(exceptionType) as context:
					Edge(source, target)
				self.assertEqual(message, str(context.exception))
