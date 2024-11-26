import struct
from Practices.device4.classes import *

class DataParser:
    def __init__(self, filename):
        self.filename = filename
        self.bedside_msg = None
        self.bedside_float = None
        self.parameters = []
        self.Parameter_RULES = [
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", 58)],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]"],
                    'value': ["HR"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", 34)],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]"],
                    'value': ["RR"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [
                        ("par_udp.parcode", "=", [77, 78, 79, 80, 177, 178, 179, 180]),
                        ("par_type", "=", [2, 3, 18])
                    ],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]", "par_udp.par_val[1]", "par_udp.par_val[2]"],
                    'value': ["MBP", "SYSBP", "DIABP"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [
                        ("par_udp.parcode", "=", [77, 78, 79, 80, 177, 178, 179, 180]),
                        ("par_type", "=", 6)
                    ],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]", "par_udp.par_val[1]"],
                    'value': ["MBP", "CPP"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", [77, 78, 79, 80, 177, 178, 179, 180])],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]"],
                    'value': ["MBP"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", [45, 208])],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]", "par_udp.par_val[1]"],
                    'value': ["SPO2", "PPR"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", [35, 184, 185, 186, 187])],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]", "par_udp.par_val[1]"],
                    'value': ["T1", "T2"]
                }
            ),
            Rule(
                if_clause={
                    'statements': [("par_udp.parcode", "=", [24, 124])],
                    'comparison': "="
                },
                then={
                    'variable': ["par_udp.par_val[0]", "par_udp.par_val[1]", "par_udp.par_val[2]"],
                    'value': ["MNIBP", "SYSIBP", "DIAIBP"]
                }
            )
        ]

    def read_bytes(self):
        with open(self.filename, 'rb') as f:
            return f.read()

    def parse_data(self):
        data = self.read_bytes()
        self.bedside_msg = self.parse_bedside_message(data[:60])
        self.bedside_float = self.parse_bedside_float(data[60:66])
        num_parameters = self.bedside_float.number_of_parameters
        param_start_idx = 66

        for i in range(num_parameters):
            param_end_idx = param_start_idx + 57
            param_data = data[param_start_idx:param_end_idx]
            param = self.parse_parameter(param_data)
            self.parameters.append(param)
            param_start_idx = param_end_idx

    def parse_bedside_message(self, data):
        fmt = '6B6B4h32B2h2h'
        unpacked_data = struct.unpack(fmt, data)
        bedside_msg = BedSideMessageDef()
        bedside_msg.dst_addr = unpacked_data[:6]
        bedside_msg.src_addr = unpacked_data[6:12]
        bedside_msg.func_code = unpacked_data[12]
        bedside_msg.sub_code = unpacked_data[13]
        bedside_msg.version = unpacked_data[14]
        bedside_msg.seq_num = unpacked_data[15]
        bedside_msg.req_res = unpacked_data[16]
        bedside_msg.proc_id = unpacked_data[17]
        bedside_msg.oln = unpacked_data[18:50]
        bedside_msg.return_status = unpacked_data[50]
        bedside_msg.data_count = unpacked_data[51]
        return bedside_msg

    def parse_bedside_float(self, data):
        fmt = '6B'  # 6*UTINY
        unpacked_data = struct.unpack(fmt, data)
        bedside_float = BedSideFloat()
        bedside_float.alarm_state = unpacked_data[0]
        bedside_float.alarm_level = unpacked_data[1]
        bedside_float.audio_alarm_level = unpacked_data[2]
        bedside_float.patient_admission = unpacked_data[3]
        bedside_float.number_of_parameters = unpacked_data[4]
        bedside_float.graph_status_msg = unpacked_data[5]
        return bedside_float

    def parse_parameter(self, data):
        param = Parameter()
        param.par_udp = self.parse_parameter_update(data[:10])
        param.ext_par_udp = self.parse_extended_parameter_update(data[10:24])
        param.setup_n_lin = self.parse_setup_and_limits(data[24:42])
        param.par_mssg_s = self.parse_parameter_messages(data[42:52])
        param.par_type = data[53]  # UTINY
        param.parcode = data[54]  # UTINY
        param.pos = data[55]  # UTINY
        return param

    def parse_parameter_update(self, data):
        fmt = 'BBH3h'
        unpacked_data = struct.unpack(fmt, data)
        par_udp = ParameterUpdate()
        par_udp.par_func_code = unpacked_data[0]  # UTINY
        par_udp.parcode = unpacked_data[1]  # UTINY
        par_udp.par_status = unpacked_data[2]  # UCOUNT
        par_udp.par_val = list(unpacked_data[3:])  # 3 * COUNT (signed 16-bit word)
        return par_udp

    def parse_extended_parameter_update(self, data):
        fmt = 'BB6h'
        unpacked_data = struct.unpack(fmt, data)
        ext_par_udp = ExtendedParameterUpdate()
        ext_par_udp.par_func_code = unpacked_data[0]  # UTINY
        ext_par_udp.par_code = unpacked_data[1]  # UTINY
        ext_par_udp.par_val = list(unpacked_data[2:])  # 6 * COUNT (signed 16-bit word)
        return ext_par_udp

    def parse_setup_and_limits(self, data):
        fmt = 'BB2B6hh'
        unpacked_data = struct.unpack(fmt, data)
        setup = SetupAndLimits()
        setup.par_func_code = unpacked_data[0]  # UTINY
        setup.parcode = unpacked_data[1]  # UTINY
        setup.flag = unpacked_data[2:4]  # 2 * UTINY
        setup.limit_values[0].lo_limit = unpacked_data[4]
        setup.limit_values[0].hi_limit = unpacked_data[5]
        setup.limit_values[1].lo_limit = unpacked_data[6]
        setup.limit_values[1].hi_limit = unpacked_data[7]
        setup.limit_values[2].lo_limit = unpacked_data[8]
        setup.limit_values[2].hi_limit = unpacked_data[9]
        setup.extra_limit = unpacked_data[10]
        return setup

    def parse_parameter_messages(self, data):
        fmt = 'BB'
        unpacked_data = struct.unpack(fmt, data[:2])
        param_msg = ParameterMessages()
        param_msg.par_func_code = unpacked_data[0]  # UTINY
        param_msg.parcode = unpacked_data[1]  # UTINY

        messages = []
        for i in range(3):
            msg_data = data[i+2:i+1+3]
            messages.append(self.parse_parameter_message(msg_data))
        param_msg.messages = messages
        
        param_msg.value = struct.unpack('H', data[-2:])[0]  # UCOUNT (2 bytes)

        return param_msg

    def parse_parameter_message(self, data):
        fmt = 'BB'
        unpacked_data = struct.unpack(fmt, data)
        param_msg = ParameterMessage()
        param_msg.attribute = unpacked_data[0]  # UTINY
        param_msg.msg_index = unpacked_data[1]
        return param_msg

    def print_parsed_data(self):
        print("=== Bedside Message ===")
        print(f"{'Field':<20} | {'Value'}")
        print("-" * 40)
        print(f"{'dst_addr':<20} | {self.bedside_msg.dst_addr}")
        print(f"{'src_addr':<20} | {self.bedside_msg.src_addr}")
        print(f"{'func_code':<20} | {self.bedside_msg.func_code}")
        print(f"{'sub_code':<20} | {self.bedside_msg.sub_code}")
        print(f"{'version':<20} | {self.bedside_msg.version}")
        print(f"{'seq_num':<20} | {self.bedside_msg.seq_num}")
        print(f"{'req_res':<20} | {self.bedside_msg.req_res}")
        print(f"{'proc_id':<20} | {self.bedside_msg.proc_id}")
        print(f"{'oln':<20} | {self.bedside_msg.oln}")
        print(f"{'return_status':<20} | {self.bedside_msg.return_status}")
        print(f"{'data_count':<20} | {self.bedside_msg.data_count}")
        print("\n")

        print("=== Bedside Float ===")
        print(f"{'Field':<20} | {'Value'}")
        print("-" * 40)
        print(f"{'alarm_state':<20} | {self.bedside_float.alarm_state}")
        print(f"{'alarm_level':<20} | {self.bedside_float.alarm_level}")
        print(f"{'audio_alarm_level':<20} | {self.bedside_float.audio_alarm_level}")
        print(f"{'patient_admission':<20} | {self.bedside_float.patient_admission}")
        print(f"{'number_of_parameters':<20} | {self.bedside_float.number_of_parameters}")
        print(f"{'graph_status_msg':<20} | {self.bedside_float.graph_status_msg}")
        print("\n")

        print("=== Parameters ===")
        for idx, param in enumerate(self.parameters, start=1):
            print(f"Parameter {idx}")
            print(f"{'Field':<20} | {'Value'}")
            print("-" * 40)
            print(f"{'par_udp':<20} | {param.par_udp.__dict__}")
            print(f"{'ext_par_udp':<20} | {param.ext_par_udp.__dict__}")
            limit = param.setup_n_lin.__dict__
            for key, value in limit.items():
                if isinstance(value, list) and all(isinstance(item, LimitValues) for item in value):
                    limit[key] = [item.__dict__ for item in value]
            print(f"{'setup_n_lin':<20} | {limit}")
            par_mssgs = param.par_mssg_s.__dict__
            for key, value in par_mssgs.items():
                if isinstance(value, list) and all(isinstance(item, ParameterMessage) for item in value):
                    par_mssgs[key] = [item.__dict__ for item in value]
            print(f"{'par_mssg_s':<20} | {par_mssgs}")
            print(f"{'par_type':<20} | {param.par_type}")
            print(f"{'parcode':<20} | {param.parcode}")
            print(f"{'pos':<20} | {param.pos}")
            print("\n")

    def update_parameters(self):
        for parameter in self.parameters:
            for rule in self.Parameter_RULES:
                if rule.evaluate_condition(parameter):
                    rule.apply(parameter)


# dataParser = DataParser('Docs/Python Practice/device_4.txt')
# dataParser.parse_data()

# dataParser.print_parsed_data()

# dataParser.update_parameters()

# dataParser.print_parsed_data()
