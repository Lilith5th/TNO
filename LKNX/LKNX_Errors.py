class Error(Exception):
    """Base class for other exceptions"""
    pass


class KNX_Address_Error(Error):
    """Raised when the input value is too small"""
    pass

class KNX_Address_Not_In_GAD_TABLE_Error(Error):
    """Raised when the input value is too small"""
    pass

class Converting_Value2DPT_Error(Error):
    """Raised when the input value is too small"""
    pass


class KNXTool_send_value_error(Error):
    """Raised when the input value is too small"""
    pass
