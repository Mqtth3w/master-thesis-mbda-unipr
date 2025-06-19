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
        #print(f"{label} (ID: {subsystem_id}):")
        print(f"{subsystem_id}:")
        if subsystem_id in interfaces:
            for iface, status in interfaces[subsystem_id]:
                print(f"  - Interface {iface} expected status: {status}")
        else:
            print("  - No interfaces defined")
        print()


def parse_system_definition3(xml_file):
    """List all the network components, interfaces and ports"""
    import xml.etree.ElementTree as ET
    from collections import defaultdict
    
    # Mappatura stato numerico -> testuale
    status_mapping = {
        '1': 'up',
        '2': 'down',
        '3': 'testing',
        '4': 'unknown',
        '5': 'dormant',
        '6': 'notPresent',
        '7': 'lowerLayerDown'
    }
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # subsystems list
    subsystems = {}
    for subsystem in root.findall(".//System/Subsystem"):
        subsystems[subsystem.attrib["id"]] = subsystem.attrib.get("label", subsystem.attrib["id"])

    # network interfaces for each subsystem
    interfaces = defaultdict(list)
    processed_switches = set()  # Per evitare switch duplicati
    
    for test in root.findall(".//Test"):
        test_class = test.find(".//Class")
        subsystem = test.attrib.get("subsystemId")
        
        if test_class is not None:
            # Handle Ethernet interfaces (for non-switch devices)
            if test_class.text == "Ethernet":
                device = None
                status = None
                for param in test.findall(".//Param"):
                    if param.attrib['name'] == 'device':
                        device = param.attrib['value']
                    if param.attrib['name'] == 'linkStatus':
                        status = param.attrib['value'].lower()  # Converti in minuscolo
                if subsystem and device and status:
                    interfaces[subsystem].append((device, status))
            
            # Handle Switch ports (for switch devices)
            elif (test_class.text == "SnmpMultiGet" 
                  and subsystem 
                  and subsystem.startswith("SWITCH")
                  and subsystem not in processed_switches):
                
                port_status = {}
                found_port_params = False
                
                for param in test.findall(".//Param"):
                    name = param.attrib['name']
                    if 'Status|up(' in name:
                        found_port_params = True
                        # Estrai direttamente il nome porta (es. "P1") dal campo name
                        parts = name.split('|')
                        if len(parts) >= 2:
                            port_name = parts[1].split()[0]  # Prendi "P1" da "P1 Status..."
                            status_code = param.attrib['value']
                            # Converti stato numerico in testuale
                            status = status_mapping.get(status_code, 'unknown')
                            port_status[port_name] = status
                
                # Processa solo se sono presenti parametri di porta
                if found_port_params:
                    # Aggiungi tutte le 24 porte
                    for port_num in range(1, 25):
                        port_key = f"P{port_num}"
                        status = port_status.get(port_key, "unknown")
                        interfaces[subsystem].append((port_key, status))
                    
                    # Segna lo switch come processato
                    processed_switches.add(subsystem)

    # descriptive output
    print("Network Components and Interfaces:\n")
    for subsystem_id, label in subsystems.items():
        #print(f"{label} (ID: {subsystem_id}):")
        print(f"{subsystem_id}:")
        if subsystem_id in interfaces:
            for iface, status in interfaces[subsystem_id]:
                print(f"  - Interface/Port {iface} expected status: {status}")
        else:
            print("  - No interfaces/ports defined")
        print()


def parse_system_definition4(xml_file):
    """List all the network components, interfaces and ports"""
    import xml.etree.ElementTree as ET
    from collections import defaultdict
    
    # Mappatura stato numerico -> testuale
    status_mapping = {
        '1': 'up',
        '2': 'down',
        '3': 'testing',
        '4': 'unknown',
        '5': 'dormant',
        '6': 'notPresent',
        '7': 'lowerLayerDown'
    }
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # subsystems list
    subsystems = {}
    for subsystem in root.findall(".//System/Subsystem"):
        subsystems[subsystem.attrib["id"]] = subsystem.attrib.get("label", subsystem.attrib["id"])

    # network interfaces for each subsystem
    interfaces = defaultdict(list)
    processed_switches = set()  # Per evitare switch duplicati
    
    for test in root.findall(".//Test"):
        test_class = test.find(".//Class")
        subsystem = test.attrib.get("subsystemId")
        
        if test_class is not None:
            # Handle Ethernet interfaces (for non-switch devices)
            if test_class.text == "Ethernet":
                device = None
                status = None
                for param in test.findall(".//Param"):
                    if param.attrib['name'] == 'device':
                        device = param.attrib['value']
                    if param.attrib['name'] == 'linkStatus':
                        status = param.attrib['value'].lower()  # Converti in minuscolo
                if subsystem and device and status:
                    interfaces[subsystem].append(("Interface", device, status))
            
            # Handle Switch ports (for switch devices)
            elif (test_class.text == "SnmpMultiGet" 
                  and subsystem 
                  and subsystem.startswith("SWITCH")
                  and subsystem not in processed_switches):
                
                port_status = {}
                found_port_params = False
                
                for param in test.findall(".//Param"):
                    name = param.attrib['name']
                    if 'Status|up(' in name:
                        found_port_params = True
                        # Estrai direttamente il nome porta (es. "P1") dal campo name
                        parts = name.split('|')
                        if len(parts) >= 2:
                            port_name = parts[1].split()[0]  # Prendi "P1" da "P1 Status..."
                            status_code = param.attrib['value']
                            # Converti stato numerico in testuale
                            status = status_mapping.get(status_code, 'unknown')
                            port_status[port_name] = status
                
                # Processa solo se sono presenti parametri di porta
                if found_port_params:
                    # Aggiungi tutte le 24 porte
                    for port_num in range(1, 25):
                        port_key = f"P{port_num}"
                        status = port_status.get(port_key, "unknown")
                        interfaces[subsystem].append(("Port", port_key, status))
                    
                    # Segna lo switch come processato
                    processed_switches.add(subsystem)

    # descriptive output
    print("Network Components and Interfaces:\n")
    for subsystem_id, label in subsystems.items():
        print(f"{subsystem_id}:")
        if subsystem_id in interfaces:
            for iface_type, iface_name, status in interfaces[subsystem_id]:
                print(f"  - {iface_type} {iface_name} expected status: {status}")
        else:
            print("  - No interfaces/ports defined")
        print()


if __name__ == "__main__":
    parse_system_definition4("../system_definition_SAMPLE_P01.xml")

