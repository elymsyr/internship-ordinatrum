from ctypes_classes import *
from classes import *

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
        msg = BedSideMessageDef_C.from_buffer_copy(data)
        bedside_msg = BedSideMessageDef()
        bedside_msg.dst_addr = list(msg.dst_addr)
        bedside_msg.src_addr = list(msg.src_addr)
        bedside_msg.func_code = msg.func_code
        bedside_msg.sub_code = msg.sub_code
        bedside_msg.version = msg.version
        bedside_msg.seq_num = msg.seq_num
        bedside_msg.req_res = msg.req_res
        bedside_msg.proc_id = msg.proc_id
        bedside_msg.oln = list(msg.oln)
        bedside_msg.return_status = msg.return_status
        bedside_msg.data_count = msg.data_count
        return bedside_msg

    def parse_bedside_float(self, data):
        bfloat = BedSideFloat_C.from_buffer_copy(data)
        bedside_float = BedSideFloat()
        bedside_float.alarm_state = bfloat.alarm_state
        bedside_float.alarm_level = bfloat.alarm_level
        bedside_float.audio_alarm_level = bfloat.audio_alarm_level
        bedside_float.patient_admission = bfloat.patient_admission
        bedside_float.number_of_parameters = bfloat.number_of_parameters
        bedside_float.graph_status_msg = bfloat.graph_status_msg
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
        p_udp = ParameterUpdate_C.from_buffer_copy(data)
        par_udp = ParameterUpdate()
        par_udp.par_func_code = p_udp.par_func_code
        par_udp.parcode = p_udp.parcode
        par_udp.par_status = p_udp.par_status
        par_udp.par_val = list(p_udp.par_val)
        return par_udp

    def parse_extended_parameter_update(self, data):
        ext_p_udp = ExtendedParameterUpdate_C.from_buffer_copy(data)
        ext_par_udp = ExtendedParameterUpdate()
        ext_par_udp.par_func_code = ext_p_udp.par_func_code
        ext_par_udp.par_code = ext_p_udp.par_code
        ext_par_udp.par_val = list(ext_p_udp.par_val)
        return ext_par_udp

    def parse_setup_and_limits(self, data):
        setup = SetupAndLimits_C.from_buffer_copy(data)
        setup_n_lin = SetupAndLimits()
        setup_n_lin.par_func_code = setup.par_func_code
        setup_n_lin.parcode = setup.parcode
        setup_n_lin.flag = list(setup.flag)
        limit = [LimitValues_C(lo_limit=l.lo_limit, hi_limit=l.hi_limit) for l in setup.limit_values]
        setup_n_lin.limit_values = [{'lo_limit': l.lo_limit, 'hi_limit': l.hi_limit} for l in limit]
        setup_n_lin.extra_limit = setup.extra_limit
        return setup_n_lin

    def parse_parameter_messages(self, data):
        p_mssgs = ParameterMessages_C.from_buffer_copy(data[:10])
        param_msg = ParameterMessages()
        param_msg.par_func_code = p_mssgs.par_func_code
        param_msg.parcode = p_mssgs.parcode
        param_msg.messages = [self.parse_parameter_message(data[i+2:i+1+3]) for i in range(3)]
        param_msg.value = int.from_bytes(data[-2:], byteorder='little')
        return param_msg

    def parse_parameter_message(self, data):
        msg = ParameterMessage_C.from_buffer_copy(data)
        param_msg = ParameterMessage()
        param_msg.attribute = msg.attribute
        param_msg.msg_index = msg.msg_index
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


dataParser = DataParser('Python_Practice/device_4.txt')
dataParser.parse_data()

dataParser.print_parsed_data()

dataParser.update_parameters()

dataParser.print_parsed_data()
