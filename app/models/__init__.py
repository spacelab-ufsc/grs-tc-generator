# app/models/__init__.py
from .satellite import Satellite
from .operator import Operator
from .telecommand import Telecommand
from .execution_log import ExecutionLog

# Isso permite importar todos os modelos de uma vez
__all__ = ['Satellite', 'Operator', 'Telecommand', 'ExecutionLog']