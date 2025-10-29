class Logger:
    def __init__(self):
        self._Proc = None

    def bind(self, Proc):
        self._Proc = Proc

    def _log(self, log_level: any, log_message: any, log_segment= None):
        self._Proc.log(log_level, log_message, log_segment)

    def info(self, log_message):
        self._log(2, log_message=log_message)
    
    def warn(self, log_message):
        self._log(3, log_message=log_message)

    def error(self, log_message):
        self._log(4, log_message=log_message)

logger = Logger()