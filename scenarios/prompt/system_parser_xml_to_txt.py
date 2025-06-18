"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_system_definition(xml_file):
    """List all the network components"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    system = root.find(".//System")
    subsystems = system.findall("Subsystem")

    print("Network components:")
    for subsystem in subsystems:
        subsystem_id = subsystem.attrib.get("id")
        label = subsystem.attrib.get("label")
        print(f"- {label} (ID: {subsystem_id})")


def parse_system_definition2(xml_file):
    """List all the network components, interfaces and ports"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # subsystems list
    subsystems = {}
    for subsystem in root.findall(".//System/Subsystem"):
        subsystems[subsystem.attrib["id"]] = subsystem.attrib.get("label", subsystem.attrib["id"])

    # network interfaces for each subsystem
    interfaces = defaultdict(list)
    for test in root.findall(".//Test"):
        test_class = test.find(".//Class")
        if test_class is not None and test_class.text == "Ethernet":
            subsystem = test.attrib.get("subsystemId")
            device = None
            status = None
            for param in test.findall(".//Param"):
                if param.attrib['name'] == 'device':
                    device = param.attrib['value']
                if param.attrib['name'] == 'linkStatus':
                    status = param.attrib['value']
            if subsystem and device:
                interfaces[subsystem].append((device, status))

    # descriptive output
    print("Network Components and Interfaces:\n")
    for subsystem_id, label in subsystems.items():
        print(f"{label} (ID: {subsystem_id}):")
        if subsystem_id in interfaces:
            for iface, status in interfaces[subsystem_id]:
                print(f"  - Interface {iface} expected status: {status}")
        else:
            print("  - No interfaces defined")
        print()


if __name__ == "__main__":
    parse_system_definition2("system_definition_SAMPLE_P01.xml")

