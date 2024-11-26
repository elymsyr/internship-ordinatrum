class Parameter:
    def __init__(self): # 57
        self.par_udp = None  # ParameterUpdate 10 BBH3h
        self.ext_par_udp = None  # ExtendedParameterUpdate 14 BB3h
        self.setup_n_lin = None  # SetupAndLimits 18 BB2B6hh
        self.par_mssg_s = None  # ParameterMessages 2 BB
        self.more_setup = None  # MoreSetup 10 BB4h
        self.par_type = None  # UTINY 
        self.parcode = None  # UTINY
        self.pos = None  # UTINY

class ParameterUpdate:
    def __init__(self):
        self.par_func_code = None  # UTINY
        self.parcode = None  # UTINY
        self.par_status = None  # UCOUNT
        self.par_val = [None, None, None]  # 3 * COUNT (signed 16-bit word)

class ExtendedParameterUpdate:
    def __init__(self):
        self.par_func_code = None  # UTINY
        self.par_code = None  # UTINY
        self.par_val = [None, None, None, None, None, None]  # 6 * COUNT (signed 16-bit word)

class LimitValues: # 4 hh
    def __init__(self):
        self.lo_limit = None  # COUNT (signed 16-bit word)
        self.hi_limit = None  # COUNT (signed 16-bit word)

class SetupAndLimits:
    def __init__(self):
        self.par_func_code = None  # UTINY
        self.parcode = None  # UTINY
        self.flag = [None, None]  # 2 * UTINY
        self.limit_values = [LimitValues() for _ in range(3)]  # 3 * LimitValues
        self.extra_limit = None  # COUNT (signed 16-bit word)

class ParameterMessage:
    def __init__(self):
        self.attribute = None  # UTINY
        self.msg_index = None  # UTINY

class ParameterMessages:
    def __init__(self):
        self.par_func_code = None  # UTINY
        self.parcode = None  # UTINY
        self.messages = [ParameterMessage() for _ in range(3)]  # 3 * ParameterMessage
        self.value = None  # UCOUNT

class MoreSetup:
    def __init__(self):
        self.par_func_code = None  # UTINY
        self.parcode = None  # UTINY
        self.val = [None, None, None, None]  # 4 * COUNT (signed 16-bit word)

class BedSideMessageDef:
    def __init__(self):
        self.dst_addr = [None] * 6  # 6 * UTINY
        self.src_addr = [None] * 6  # 6 * UTINY
        self.func_code = None  # COUNT (signed 16-bit word)
        self.sub_code = None  # COUNT (signed 16-bit word)
        self.version = None  # COUNT (signed 16-bit word)
        self.seq_num = None  # COUNT (signed 16-bit word)
        self.req_res = None  # COUNT (signed 16-bit word)
        self.proc_id = None  # COUNT (signed 16-bit word)
        self.oln = [None] * 32  # 32 * UTINY
        self.return_status = None  # COUNT (signed 16-bit word)
        self.data_count = None  # COUNT (signed 16-bit word)

class BedSideFloat:
    def __init__(self):
        self.alarm_state = None  # UTINY
        self.alarm_level = None  # UTINY
        self.audio_alarm_level = None  # UTINY
        self.patient_admission = None  # UTINY
        self.number_of_parameters = None  # UTINY
        self.graph_status_msg = None  # UTINY

class RTCCPY:
    def __init__(self):
        self.secpy_rt = None  # UTINY
        self.micpy_rt = None  # UTINY
        self.hrcpy_rt = None  # UTINY
        self.dwcpy_rt = None  # UTINY
        self.dacpy_rt = None  # UTINY
        self.mocpy_rt = None  # UTINY
        self.yrcpy_rt = None  # UCOUNT

class Rule:
    def __init__(self, if_clause: dict, then: dict, conjunction: str = "AND"):
        """
        Represents a rule with conditional logic.
        :param if_clause: Dictionary with 'statements' (list of conditions) and 'comparison' operator.
        :param then: Dictionary with 'variable' (list of variable names) and 'value' (corresponding values).
        :param conjunction: Logic to apply between if_clause statements ('AND' or 'OR').
        """
        self.conjunction = conjunction
        self.if_clause = if_clause  # E.g., {'statements': [(var, op, val)]}
        self.then = then  # E.g., {'variable': ['parameters.par_udp.par_val[0]', 'parameters.par_udp.par_val[1]'], 'value': ['HR', 'RR']}

    def evaluate_condition(self, obj):
        """
        Evaluates the if_clause conditions on the given object.
        :param obj: Object to evaluate conditions against.
        :return: Boolean result of the evaluation.
        """
        results = []
        for variable_name, comparison, value in self.if_clause['statements']:
            variable_value = self.get_variable(obj, variable_name)
            try:
                if comparison == "=":
                    results.append(variable_value == value)
                elif comparison == "in":
                    results.append(variable_value in value)
                elif comparison == ">":
                    results.append(variable_value > value)
                elif comparison == "<":
                    results.append(variable_value < value)
                elif comparison == ">=":
                    results.append(variable_value >= value)
                elif comparison == "<=":
                    results.append(variable_value <= value)
                else:
                    raise ValueError(f"Unsupported comparison: {comparison}")
            except: results.append(False)
            if self.conjunction == "AND" and all(results) == False: return False
            elif any(results) == True: return True
        return all(results) if self.conjunction == "AND" else any(results)

    def apply(self, obj):
        """
        Applies the 'then' actions by updating the specified variables in the object.
        :param obj: Object to update.
        """
        for variable_name, value in zip(self.then['variable'], self.then['value']):
            self.set_variable(obj, variable_name, value)

    @staticmethod
    def get_variable(obj, variable_name):
        """
        Retrieves the value of a variable dynamically.
        :param obj: Object containing the variable.
        :param variable_name: Dot-separated path to the variable (e.g., 'par_udp.par_val[0]').
        :return: The value of the variable.
        """
        parts = variable_name.split(".")
        current = obj
        for part in parts:
            if "[" in part:
                attr_name, index = part[:-1].split("[")
                current = getattr(current, attr_name)[int(index)]
            else:
                current = getattr(current, part)
        return current

    @staticmethod
    def set_variable(obj, variable_name, value):
        """
        Sets the value of a variable dynamically.
        :param obj: Object containing the variable.
        :param variable_name: Dot-separated path to the variable (e.g., 'par_udp.par_val[0]').
        :param value: Value to set.
        """
        parts = variable_name.split(".")
        current = obj
        for part in parts[:-1]:
            if "[" in part:
                attr_name, index = part[:-1].split("[")
                current = getattr(current, attr_name)[int(index)]
            else:
                current = getattr(current, part)
        if "[" in parts[-1]:
            attr_name, index = parts[-1][:-1].split("[")
            getattr(current, attr_name)[int(index)] = value
        else:
            setattr(current, parts[-1], value)
