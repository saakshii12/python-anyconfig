#
# Copyright (C) 2012 - 2017 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name, protected-access
from __future__ import absolute_import
import os.path
import unittest

import anyconfig.backend.xml as TT
import anyconfig.backend.tests.ini
import anyconfig.tests.common
import anyconfig.compat

from anyconfig.tests.common import dicts_equal, to_bytes


XML_W_NS_S = """
<a xmlns="http://example.com/ns/config"
   xmlns:val="http://example.com/ns/config/val">
   <b>1</b>
   <val:c>C</val:c>
</a>
"""

CNF_0 = {'config': {'@attrs': {'name': 'foo'},
                    'a': '0',
                    'b': {'@attrs': {'id': 'b0'}, '@text': 'bbb'},
                    'c': None,
                    'sect0': {'d': 'x, y, z'},
                    'list1': [{'item': '0'}, {'item': '1'}, {'item': '2'}],
                    'list2': {'@attrs': {'id': 'list2'},
                              '@children': [{'item': 'i'},
                                            {'item': 'j'}]}}}
CNF_0_S = """\
<?xml version="1.0" encoding="UTF-8"?>
<config name='foo'>
  <a>0</a>
  <b id="b0">bbb</b>
  <c/>
  <sect0>
    <d>x, y, z</d>
  </sect0>
  <list1>
    <item>0</item>
    <item>1</item>
    <item>2</item>
  </list1>
  <list2 id="list2">
    <item>i</item>
    <item>j</item>
  </list2>
</config>
"""


class Test_00(unittest.TestCase):

    def test_10__namespaces_from_file(self):
        ref = {"http://example.com/ns/config": '',
               "http://example.com/ns/config/val": "val"}
        xmlfile = anyconfig.compat.StringIO(XML_W_NS_S)
        self.assertTrue(dicts_equal(TT._namespaces_from_file(xmlfile), ref))

    def test_20__process_elem_text__whitespaces(self):
        (elem, dic, subdic) = (TT.ET.XML("<a> </a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic)
        self.assertTrue(not dic)
        self.assertTrue(not subdic)

    def test_22__process_elem_text__wo_attrs_and_children(self):
        (elem, dic, subdic) = (TT.ET.XML("<a>A</a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic, text="#text")
        self.assertTrue(dicts_equal(dic, {"a": 'A'}))
        self.assertTrue(not subdic)

    def test_22__process_elem_text__wo_attrs_and_children_parse(self):
        (elem, dic, subdic) = (TT.ET.XML("<a>A</a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic, text="#text",
                              ac_parse_value=True)
        self.assertTrue(dicts_equal(dic, {"a": 'A'}))
        self.assertTrue(not subdic)

        (elem, dic, subdic) = (TT.ET.XML("<a>1</a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic, text="#text",
                              ac_parse_value=True)
        self.assertTrue(dicts_equal(dic, {"a": 1}))
        self.assertTrue(not subdic)

    def test_24__process_elem_text__w_attrs(self):
        (elem, dic, subdic) = (TT.ET.XML("<a id='1'>A</a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic, text="#text")
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"#text": 'A'}))

    def test_24__process_elem_text__w_children(self):
        (elem, dic, subdic) = (TT.ET.XML("<a>A<b/></a>"), {}, {})
        TT._process_elem_text(elem, dic, subdic, text="#text")
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"#text": 'A'}))

    def test_30__process_elem_attrs__wo_text_and_children(self):
        (elem, dic, subdic) = (TT.ET.XML("<a id='A'/>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic)
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"@attrs": {"id": 'A'}}))

    def test_32__process_elem_attrs__w_text(self):
        (elem, dic, subdic) = (TT.ET.XML("<a id='A'>AAA</a>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic)
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"@attrs": {"id": 'A'}}))

    def test_34__process_elem_attrs__merge_attrs(self):
        (elem, dic, subdic) = (TT.ET.XML("<a id='A'/>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic, merge_attrs=True)
        self.assertTrue(dicts_equal(dic, {"a": {"id": 'A'}}))
        self.assertTrue(not subdic)

    def test_36__process_elem_attrs__wo_text_and_children_parse(self):
        (elem, dic, subdic) = (TT.ET.XML("<a id='1'/>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic, ac_parse_value=True)
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"@attrs": {"id": 1}}))

        (elem, dic, subdic) = (TT.ET.XML("<a id='A'/>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic, ac_parse_value=True)
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"@attrs": {"id": 'A'}}))

        (elem, dic, subdic) = (TT.ET.XML("<a id='true'/>"), {}, {})
        TT._process_elem_attrs(elem, dic, subdic, ac_parse_value=True)
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, {"@attrs": {"id": True}}))

    def test_40__process_children_elems__root(self):
        (elem, dic, subdic) = (TT.ET.XML("<list><i>A</i><i>B</i></list>"), {},
                               {})
        TT._process_children_elems(elem, dic, subdic)
        self.assertTrue(dicts_equal(dic, {"list": [{"i": "A"}, {"i": "B"}]}))
        self.assertTrue(not subdic)

    def test_42__process_children_elems__w_attr(self):
        (elem, dic) = (TT.ET.XML("<list id='xyz'><i>A</i><i>B</i></list>"), {})
        subdic = {"id": "xyz"}
        ref = subdic.copy()
        ref.update({"#children": [{"i": "A"}, {"i": "B"}]})

        TT._process_children_elems(elem, dic, subdic, children="#children")
        self.assertTrue(not dic)
        self.assertTrue(dicts_equal(subdic, ref), subdic)

    def test_44__process_children_elems__w_children_have_unique_keys(self):
        (elem, dic, subdic) = (TT.ET.XML("<a><x>X</x><y>Y</y></a>"), {}, {})
        TT._process_children_elems(elem, dic, subdic)
        self.assertTrue(dicts_equal(dic, {"a": {"x": "X", "y": "Y"}}))
        self.assertTrue(not subdic)

    def test_46__process_children_elems__w_merge_attrs(self):
        elem = TT.ET.XML("<a z='Z'><x>X</x><y>Y</y></a>")
        dic = {"a": {"@attrs": {"z": "Z"}}}
        subdic = dic["a"]["@attrs"]
        TT._process_children_elems(elem, dic, subdic, merge_attrs=True)
        self.assertTrue(dicts_equal(dic, {"a": {"x": "X", "y": "Y",
                                                "z": "Z"}}), dic)


def _xml_to_container(snippet, **opts):
    return TT.elem_to_container(TT.ET.XML(snippet), to_container=dict, **opts)


class Test_10(unittest.TestCase):

    def test_10_elem_to_container__None(self):
        self.assertEqual(TT.elem_to_container(None), dict())

    def test_10_root_to_container__None(self):
        self.assertEqual(TT.root_to_container(None), dict())

    def test_12_elem_to_container__empty(self):
        self.assertEqual(_xml_to_container("<a/>"), dict(a=None))

    def test_20_elem_to_container__attrs(self):
        ref = dict(a={"@attrs": dict(x='1', y='y')})
        self.assertEqual(_xml_to_container("<a x='1' y='y'/>"), ref)

    def test_30_elem_to_container__child(self):
        ref = dict(a=dict(b="b"))
        self.assertEqual(_xml_to_container("<a><b>b</b></a>"), ref)

    def test_32_elem_to_container__children__same_keys(self):
        ref = {'a': [{'b': '1'}, {'b': '2'}]}
        self.assertEqual(_xml_to_container("<a><b>1</b><b>2</b></a>"), ref)

    def test_34_elem_to_container__children(self):
        ref = {'a': {'b': 'b', 'c': 'c'}}
        self.assertEqual(_xml_to_container("<a><b>b</b><c>c</c></a>"), ref)

    def test_36_elem_to_container__children__same_keys_w_text(self):
        ref = {'a': {'@text': 'aaa', '@children': [{'b': '1'}, {'b': '2'}]}}
        self.assertEqual(_xml_to_container("<a>aaa<b>1</b><b>2</b></a>"), ref)

    def test_40_elem_to_container__text(self):
        self.assertEqual(_xml_to_container("<a>A</a>"), {'a': 'A'})

    def test_42_elem_to_container__text_attrs(self):
        ref = dict(a={"@attrs": {'x': 'X'}, "@text": "A"})
        self.assertEqual(_xml_to_container("<a x='X'>A</a>"), ref)

    def test_50_root_to_container__text_attrs_tags(self):
        ref = dict(a={"_attrs": {'x': 'X'}, "_text": "A"})
        tags = dict(attrs="_attrs", text="_text")
        self.assertEqual(TT.root_to_container(TT.ET.XML("<a x='X'>A</a>"),
                                              dict, {}, tags=tags),
                         ref)


def tree_to_string(tree):
    return TT.ET.tostring(tree.getroot())


class Test_20(unittest.TestCase):

    def test_00_container_to_etree__None(self):
        self.assertTrue(TT.container_to_etree(None) is None)

    def test_10_container_to_etree__text_attrs(self):
        ref = to_bytes('<a x="X" y="Y">A</a>')
        obj = dict(a={"@attrs": {'x': 'X', 'y': 'Y'}, "@text": "A"})
        res = TT.container_to_etree(obj)
        self.assertEqual(tree_to_string(res), ref)

    def test_12_container_to_etree__text_attrs_tags(self):
        ref = to_bytes('<a x="X" y="Y">A</a>')
        obj = dict(a={"_attrs": {'x': 'X', 'y': 'Y'}, "_text": "A"})
        tags = dict(attrs="_attrs", text="_text")
        res = TT.container_to_etree(obj, tags=tags)
        self.assertEqual(tree_to_string(res), ref)

    def test_20_container_to_etree__child(self):
        ref = to_bytes("<a><b>b</b></a>")
        obj = dict(a=dict(b="b"))
        res = TT.container_to_etree(obj)
        self.assertEqual(tree_to_string(res), ref)

    def test_22_container_to_etree__children(self):
        ref = to_bytes("<a><b>b</b><c>c</c></a>")
        obj = {'a': {'@children': [{'b': 'b'}, {'c': 'c'}]}}
        res = TT.container_to_etree(obj)
        self.assertEqual(tree_to_string(res), ref)


class Test10(anyconfig.backend.tests.ini.Test10):

    cnf = CNF_0
    cnf_s = CNF_0_S.encode("utf-8")
    load_options = dump_options = dict(ac_parse_value=False)

    def setUp(self):
        self.psr = TT.Parser()


class Test20(anyconfig.backend.tests.ini.Test20):

    psr_cls = TT.Parser
    cnf = CNF_0
    cnf_s = CNF_0_S
    cnf_fn = "conf0.xml"

    def setUp(self):
        self.psr = self.psr_cls()
        self.workdir = anyconfig.tests.common.setup_workdir()
        self.cpath = os.path.join(self.workdir, self.cnf_fn)
        with self.psr.wopen(self.cpath) as out:
            if anyconfig.compat.IS_PYTHON_3:
                out.write(self.cnf_s.encode("utf-8"))
            else:
                out.write(self.cnf_s)

    def test_12_load__w_options(self):
        cnf = self.psr.load(self.cpath, ac_parse_value=False)
        self._assert_dicts_equal(cnf)

    def test_22_dump__w_special_option(self):
        self.psr.dump(self.cnf, self.cpath, ac_parse_value=False)
        cnf = self.psr.load(self.cpath)
        self._assert_dicts_equal(cnf)

# vim:sw=4:ts=4:et:
