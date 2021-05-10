from unittest.mock import patch
import requests
import re
import unittest

import xml.etree.ElementTree as ET


def get_row(table: str, text="Data") -> int:
    """
    Checks the first row of column
    to get where to look for date
    """
    # Jezeli nie znajdziemy tagu "th" ktory oznacza header to wychodziny
    if not get_childrens(table[0], 'th'):
        raise IOError("Missing th tags in first row. Cannot Proceed")

    cell_number = 0
    for th in table[0]:
        # Jezeli text bez bialych znakow rowna sie temu czego szukamy zwracamy numer celli
        if th.text.strip() == text:
            return cell_number
        cell_number += 1

    raise IOError("Date column not found")


def get_childrens(node: ET, tag: str = None) -> list:
    """
    Get all childrens of node
    """
    return list(node.iter(tag))


def get_name(cell: ET) -> str:
    """
    Get name of user from 'a' tag
    """
    a = get_childrens(cell, 'a')
    # Szukamy tagu ktory w wikipedii jest odnosnikiem do nazwy uczestnika
    if not a:
        raise IOError("a tag not found")
    # Jezeli nie znajdziemy to wychodzimy. w innym przypadku zwracamy text nody.
    return a[0].text


def check_date(row: list, date_cell_no: int, regexp=r"^1[0-9]{3}") -> bool:
    """
    Check if year is below 2000
    """
    # Sprawdzanie czy data jest ponizej 2000 poprzez prosty regex
    if re.match(regexp, row[date_cell_no].text):
        return True

    return False


def get_page_html(url: str) -> str:
    """
    Get HTML code of webpage
    """
    r = requests.get(url)
    # Sprawdzenie odpowiedzi, jezeli 300+ to konczymy dzialanie programu
    r.raise_for_status()
    return r


def get_table(url: str,
              xpath: str = ".//table[@class='wikitable sortable']/tbody") -> ET:
    """
    Get webpage html content as ElementTree
    """
    html = get_page_html(url)
    root = ET.fromstring(html.text)
    table = root.findall(xpath)[0]
    return table

    # This method will be used by the mock to replace requests.get


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, text):
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    with open("test_file.txt") as f:
        return MockResponse({"key1": "value1"}, 200, f.read())


class TestChessMaster(unittest.TestCase):

    def test_get_row_found(self):
        table = """
        <table>
            <tr>
                <th>Data</th>
                <th>Miejsce</th>
            </tr>
        </table>
        """
        xml = ET.fromstring(table)
        self.assertEqual(get_row(xml, "Data"), 0)

    def test_get_row_no_th(self):
        table = """
        <table>
            <tr>
                <td>Data</td>
                <td>Miejsce</td>
            </tr>
        </table>
        """
        xml = ET.fromstring(table)
        with self.assertRaises(IOError) as e:
            get_row(xml)

        self.assertEqual(
            "Missing th tags in first row. Cannot Proceed", str(e.exception)
        )

    def test_get_row_no_row(self):
        table = """
        <table>
            <tr>
                <th>Data</th>
                <th>Miejsce</th>
            </tr>
        </table>
        """
        xml = ET.fromstring(table)
        with self.assertRaises(IOError) as e:
            get_row(xml, "test")

        self.assertEqual(
            "Date column not found", str(e.exception)
        )

    def test_get_childrens(self):
        table = """
        <table>
            <tr>
                <th>Data</th>
                <th>Miejsce</th>
            </tr>
        </table>
        """
        xml = ET.fromstring(table)
        self.assertEqual(
            list(xml.iter()), get_childrens(xml)
        )

    def test_get_name(self):
        table = """
         <table>
            <tr>
                <th>Miejsce</th>
                <th>Imię i nazwisko</th>
                <th>Data</th>
            </tr>
            <tr>
                <th>2</th>
                <th><a>Garri Kasparow</a></th>
                <th>1999.07.01</th>
            </tr>
        </table>
        """
        xml = ET.fromstring(table)
        self.assertEqual(get_name(xml), "Garri Kasparow")

    def test_get_name_no_name(self):
        table = """
            <table>
               <tr>
                   <th>Miejsce</th>
                   <th>Imię i nazwisko</th>
                   <th>Data</th>
               </tr>
               <tr>
                   <th>2</th>
                   <th>Garri Kasparow</th>
                   <th>1999.07.01</th>
               </tr>
           </table>
           """
        xml = ET.fromstring(table)
        with self.assertRaises(IOError) as e:
            get_name(xml)

        self.assertEqual(
            "a tag not found", str(e.exception)
        )

    def test_regexp_true(self):
        x = '1994.05.19'
        regexp = r"^1[0-9]{3}"
        self.assertTrue(re.match(regexp, x))

    def test_regexp_false(self):
        x = '2004.05.19'
        regexp = r"^1[0-9]{3}"
        self.assertFalse(re.match(regexp, x))

