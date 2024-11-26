import ctypes
from classes import *

class BedSideMessageDef_C(ctypes.Structure):
    _fields_ = [
        ("dst_addr", ctypes.c_ubyte * 6),
        ("src_addr", ctypes.c_ubyte * 6),
        ("func_code", ctypes.c_int16),
        ("sub_code", ctypes.c_int16),
        ("version", ctypes.c_int16),
        ("seq_num", ctypes.c_int16),
        ("req_res", ctypes.c_int16),
        ("proc_id", ctypes.c_int16),
        ("oln", ctypes.c_ubyte * 32),
        ("return_status", ctypes.c_int16),
        ("data_count", ctypes.c_int16)
    ]

class BedSideFloat_C(ctypes.Structure):
    _fields_ = [
        ("alarm_state", ctypes.c_ubyte),
        ("alarm_level", ctypes.c_ubyte),
        ("audio_alarm_level", ctypes.c_ubyte),
        ("patient_admission", ctypes.c_ubyte),
        ("number_of_parameters", ctypes.c_ubyte),
        ("graph_status_msg", ctypes.c_ubyte)
    ]

class ParameterUpdate_C(ctypes.Structure):
    _fields_ = [
        ("par_func_code", ctypes.c_ubyte),
        ("parcode", ctypes.c_ubyte),
        ("par_status", ctypes.c_uint16),
        ("par_val", ctypes.c_int16 * 3)
    ]

class ExtendedParameterUpdate_C(ctypes.Structure):
    _fields_ = [
        ("par_func_code", ctypes.c_ubyte),
        ("par_code", ctypes.c_ubyte),
        ("par_val", ctypes.c_int16 * 6)
    ]

class LimitValues_C(ctypes.Structure):
    _fields_ = [
        ("lo_limit", ctypes.c_int16),
        ("hi_limit", ctypes.c_int16)
    ]

class SetupAndLimits_C(ctypes.Structure):
    _fields_ = [
        ("par_func_code", ctypes.c_ubyte),
        ("parcode", ctypes.c_ubyte),
        ("flag", ctypes.c_ubyte * 2),
        ("limit_values", LimitValues_C * 3),
        ("extra_limit", ctypes.c_int16)
    ]

class ParameterMessage_C(ctypes.Structure):
    _fields_ = [
        ("attribute", ctypes.c_ubyte),
        ("msg_index", ctypes.c_ubyte)
    ]

class ParameterMessages_C(ctypes.Structure):
    _fields_ = [
        ("par_func_code", ctypes.c_ubyte),
        ("parcode", ctypes.c_ubyte),
        ("messages", ParameterMessage_C * 3),
        ("value", ctypes.c_uint16)
    ]

