import xml.etree.ElementTree as ET

class PacketParser:
    def __init__(self):
        self.ventilation_mode_start = 48
        self.ventilation_mode_length = 1        
        self.ventilation_modes = {
            'v': 'VCV',
            'p': 'PCV',
            'g': 'PCV-VG',
            'G': 'BiLevel-VG',
            's': 'SIMV-VC',
            'i': 'SIMV-PC',
            'S': 'SIMV-PCVG',
            'B': 'BiLevel',
            'c': 'CPAP/PSV',
            'n': 'NIV',
            'N': 'nCPAP',
            'V': 'VG-PS'
        }
        self.vtu_fields = {
            'ExpiratoryTidalVolTVexp': (4, 4, 1),
            'TotalExpMinuteVolMVexp': (8, 4, 0.01),
            'RespiratoryRateTotal': (12, 3, 1),
            'FiO2': (15, 3, 1),
            'InspiratoryTime': (199, 3, 0.1),
            'ExpiratoryTime': (202, 3, 0.1),
        }
        self.classes = ['setting', 'monitor', 'alarm']
    
    def split_by_newlines(self, data: str):
        """
        Split the entire data by '\n\n\n' to separate individual packages.
        Returns a list of packages (each as a string).
        """

        return [packet.strip() for packet in data.split('\n\n\n') if packet.strip()]

    def split_by_pipe(self, package: str):
        """
        Split a package by '|' to separate fields.
        Returns a list of fields (each as a string).
        """
        return [field.strip() for field in package.split('|') if field.strip()]

    def split_by_colon(self, field: str):
        """
        Split a field by ':' to separate the field name (alan_ismi) from the field value (alan_değeri).
        Returns a tuple (alan_ismi, alan_değeri).
        """
        if ':' in field:
            alan_ismi, alan_degeri = field.split(':', 1)
            return alan_ismi.strip(), alan_degeri.strip()
        return None

    def read_from_file(self, file_path: str):
        """
        Reads the content of the given text file.
        Returns the data as a string.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
            return data.strip().replace('', '')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""

    def parse_device_1(self, file_path: str):
        """
        Main function that uses the other functions to parse the entire data.
        It returns a list of dictionaries, where each dictionary represents a parsed package.
        """
        parsed_packages = []
        
        data = self.read_from_file(file_path=file_path)
        packages = self.split_by_newlines(data=data)
        
        for package in packages:
            fields = self.split_by_pipe(package)
            
            parsed_data = {}
            for field in fields:
                result = self.split_by_colon(field)
                if result:
                    alan_ismi, alan_degeri = result
                    parsed_data[alan_ismi] = alan_degeri
            
            parsed_packages.append(parsed_data)
        
        return parsed_packages

    def find_subpackages(self, data: list[str]):
        splitted_subs = []
        for packages in data:
            parsed_subs = []
            package = [package.strip() for package in packages.split("\n")]
            main_package = package.pop(0)

            if main_package.startswith(":VTu"): main_package = self.parse_vtu_packet(main_package)
            elif main_package.startswith(":VTv"): main_package = self.parse_vtv_packet(main_package)
            else: main_package = {"error": "Unknown"}
            for subpackage in package:
                if subpackage.startswith(":VTu"):
                    parsed = self.parse_vtu_packet(subpackage)
                    parsed_subs.append(parsed)
                elif subpackage.startswith(":VTv"):
                    parsed = self.parse_vtv_packet(subpackage)
                    parsed_subs.append(parsed)
                else: parsed_subs.append({"error": "Unknown"})
            splitted_subs.append({"main_package": main_package, "subpackages": parsed_subs})
        return splitted_subs

    def parse_vtv_packet(self, packet: str):
        ventilation_mode_code = packet[self.ventilation_mode_start:self.ventilation_mode_start + self.ventilation_mode_length]
        ventilation_mode = self.ventilation_modes.get(ventilation_mode_code, 'Unknown')
        

        return {
            'VentilationMode': ventilation_mode
        }

    def parse_vtu_packet(self, packet: str):
        parsed_data = {}
        
        for field_name, (start, length, multiplier) in self.vtu_fields.items():
            raw_value = packet[start:start + length].strip()
            if raw_value.isdigit():
                value = int(raw_value) * multiplier
            else:
                value = None
            parsed_data[field_name] = value
        
        return parsed_data

    def parse_device_2(self, file_path: str):
        parsed_packages = []
        
        data = self.read_from_file(file_path=file_path)
        packages = self.split_by_newlines(data=data)
        return self.find_subpackages(packages)

    def convert_scale(self, scale: str):
        if scale is not None and scale.startswith('E+'): 
            scale.replace('E+', '')
        try: return(int(scale)*10)
        except: return 0

    def find_profile_n_data(self, splitted_packages: list[str]):
        profile: str = None
        for order, pack in enumerate(splitted_packages):
            if pack.startswith('<profile'):
                profile = splitted_packages.pop(order)
        parsed_profile = self.parse_profile(profile)
        parsed_data = [self.parse_data(data) for data in splitted_packages]
        class_seperated_units = self.seperated_by_classes(parsed_profile['units'], 'unit')
        class_seperated_datas = self.seperated_by_classes(parsed_data, 'data')
        parsed_profile['units'] = class_seperated_units
        return parsed_profile, class_seperated_datas

    def parse_profile(self, profile_xml: str):
        """
        Parse the profile XML, extract units, and return them as a list of unit information.
        """
        root = ET.fromstring(profile_xml)
        units = []

        for unit in root.findall(".//unit"):
            unit_data = {
                "class": unit.get("class"),
                "ID": unit.get("ID"),
                "type": unit.get("type"),
                "scale": self.convert_scale(unit.get("scale", "1")),
                "label": unit.get("label"),
                "range": unit.get("range")
            }

            if unit_data['type'] == 'ENUM':
                enums = []
                for enum in unit.findall(".//enum"):
                    enum_value = enum.get("value")
                    enum_label = enum.get("label")
                    enums.append({
                        "value": enum_value,
                        "label": enum_label,
                    })
                unit_data["enums"] = enums
            units.append(unit_data)

        profile = {
            "model": root.get("model"),
            "profileVersion": root.get("profileVersion"),
            "voxpVersion": root.get("voxpVersion"),
            "textEncoding": root.get("textEncoding"),
            "units": units
        }

        return profile

    def parse_data(self, xml: str):
        """
        Parse the <data> XML element, extract its attributes, and handle its content.
        """
        root = ET.fromstring(xml)
        
        data_info = {
            "class": root.get("class"),
            "crc": root.get("crc"),
            "msgID": root.get("msgID"),
        }
        
        hex_data = root.text.strip()
        
        return {
            "data_info": data_info,
            "hex_data": hex_data,
            "hex_data": hex_data,
        }

    def decode_content(self, data_type: str, data: str, scale: float = None, enums: dict = None):
        """
        Decode the byte data based on the given data_type and return the result.
        
        Parameters:
            data_type (str): The type of data to decode. One of:
                            WORD, UWORD, INT, BOOL, ENUM, UINT, TEXT
            data (str): A long string of HEX numbers (e.g., "0A1B2C3D").
            scale (float): Divide data by scale to decode.
        """
        def hex_to_int(hex_str, signed=False):
            """Helper to convert HEX string to integer."""
            byte_length = len(hex_str) // 2
            value = int(hex_str, 16)
            if signed and value >= 2**(byte_length * 8 - 1):
                value -= 2**(byte_length * 8)
            return value
        def int_to_hex(value, byte_length):
            """Convert an integer value back to a hex string."""
            return f"{value & (2**(byte_length * 8) - 1):0{byte_length * 2}X}"

        hex_chunk = ""
        if data_type == "WORD":
            hex_chunk = data[:4]
            decoded = hex_to_int(hex_chunk, signed=True)
            remaining_data = data[4:]
        elif data_type == "UWORD":
            hex_chunk = data[:4]
            decoded = hex_to_int(hex_chunk, signed=False)
            remaining_data = data[4:]
        elif data_type == "INT":
            hex_chunk = data[:8]
            decoded = hex_to_int(hex_chunk, signed=True)
            remaining_data = data[8:]
        elif data_type == "UINT":
            hex_chunk = data[:8]
            decoded = hex_to_int(hex_chunk, signed=False)
            remaining_data = data[8:]
        elif data_type == "BOOL":
            hex_chunk = data[:2]
            decoded = bool(hex_to_int(hex_chunk))
            remaining_data = data[2:]
        elif data_type == "ENUM":
            hex_chunk = data[:2]
            decoded = hex_to_int(hex_chunk, signed=False)
            remaining_data = data[2:]
            enums = [hex_to_int(enum['value']) for enum in enums]
        elif data_type == "TEXT":
            decoded = ""
            for i in range(0, len(data), 2):
                char = chr(int(data[i:i+2], 16))
                if char == "\x00":
                    break
                decoded += char
            remaining_data = data[len(decoded) * 2 + 2:]
        else:
            raise ValueError(f"Unsupported data_type: {data_type}")

        if scale is not None and isinstance(decoded, (int, float)) and scale not in [0, 1]:
            decoded /= scale

        return {"decoded": decoded, "hex_chunk": hex_chunk, "data_type": data_type, "enums": enums}, remaining_data

    def seperated_by_classes(self, data: dict, data_class: str):
        seperated_classes: dict = {}
        for class_name in self.classes:
            seperated_classes[class_name] = []
        for row in data:
            if data_class == 'unit':
                if row['class'] in self.classes:
                    seperated_classes[row['class']].append(row)
            elif data_class == 'data':
                if row['data_info']['class'] in self.classes:
                    seperated_classes[row['data_info']['class']].append(row)
        return seperated_classes

    def overall_data_by_class(self, datas: dict):
        overall_data: dict = {}
        for class_name in self.classes:
            overall_data[class_name] = ""
        for class_name in self.classes:
            overall_data[class_name] = ("".join([data['hex_data'] for data in datas[class_name]]))
        return overall_data

    def parse_device_3(self, file_path: str):
        self.setting = {}
        self.monitor = {}
        self.alarm = {}

        data = self.read_from_file(file_path=file_path)
        packages = self.split_by_newlines(data=data)
        profile, datas = self.find_profile_n_data(packages)
        units = profile['units']
        overall_data = self.overall_data_by_class(datas)

        for class_name in self.classes:
            _units = units[class_name]
            _data = overall_data[class_name]
            for unit in _units:
                decoded, _data = self.decode_content(data_type=unit['type'], data=_data, scale=unit['scale'], enums=unit['enums'] if 'enums' in unit.keys() else None)
                if class_name == 'setting': self.setting[unit['ID']] = decoded
                elif class_name == 'monitor': self.monitor[unit['ID']] = decoded
                elif class_name == 'alarm': self.alarm[unit['ID']] = decoded

# parser = PacketParser()
# parser.parse_device_3(file_path='Docs/Python Practice/device_3.txt')
# values = {"setting": parser.setting, "monitor": parser.monitor, "alarm": parser.alarm}
# for key, value in values.items():
#     print(f"{key}")
#     for subkey, decoded in value.items():
#         print(f"  ", f"{subkey}{"".join([" " for _ in range(35 - len(subkey))])} \
#             {decoded['decoded']}{"".join([" " for _ in range(10 - len(str(decoded['decoded'])))]) if 10 - len(str(decoded['decoded'])) > 0 else " "}{decoded['hex_chunk']}{"".join([" " for _ in range(10 - len(str(decoded['hex_chunk'])))]) if 10 - len(str(decoded['hex_chunk'])) > 0 else " "}{decoded['data_type']}{"".join([" " for _ in range(10 - len(str(decoded['data_type'])))]) if 10 - len(str(decoded['data_type'])) > 0 else " "}{decoded['enums'] if decoded['enums'] is not None else ""}{("True" if decoded['decoded'] == 0.1 else "False") if decoded['data_type'] == 'BOOL' else ""}".strip())

# parser = PacketParser()
# parsed_data = parser.parse_device_1(file_path='Docs/Python Practice/device_1.txt')
# for i, package in enumerate(parsed_data, 1):
#     print(f"Package {i}: {package}")


# parser = PacketParser()
# parsed_data = parser.parse_device_2(file_path='Docs/Python Practice/device_2.txt')
# for i, packages in enumerate(parsed_data, 1):
#     print(f"Package {i}:")
#     for key, value in packages.items():
#         if isinstance(value, str):
#             print(f"  {key}:\n    {value}")
#         elif isinstance(value, dict):
#             print(f"  {key}")
#             for subkey, subvalue in value.items():
#                 print(f"    {subkey}: {subvalue}")
#         else: 
#             print(f"  {key}:")
#             for subpackage in value:
#                 if isinstance(subpackage, dict):
#                     for key, value in subpackage.items():
#                         print(f"    {key}: {value}")

