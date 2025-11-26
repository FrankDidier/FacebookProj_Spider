"""
Compatibility layer to use PySide6 as PySide2
This allows the code to work with PySide6 without changing all imports
"""
import sys

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    # Create aliases for PySide2 compatibility
    # Make PySide2 available as an alias to PySide6
    class PySide2Module:
        """Fake module to make PySide2 imports work"""
        QtCore = QtCore
        QtGui = QtGui
        QtWidgets = QtWidgets
        
        def __getattr__(self, name):
            # For any other attribute, try to get it from PySide6
            try:
                return getattr(sys.modules['PySide6'], name)
            except (KeyError, AttributeError):
                raise AttributeError(f"module 'PySide2' has no attribute '{name}'")
    
    # Create fake PySide2 module
    fake_pyside2 = PySide2Module()
    sys.modules['PySide2'] = fake_pyside2
    sys.modules['PySide2.QtCore'] = QtCore
    sys.modules['PySide2.QtGui'] = QtGui
    sys.modules['PySide2.QtWidgets'] = QtWidgets
except ImportError:
    # If PySide6 is not available, try PySide2
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
    except ImportError:
        raise ImportError("Neither PySide6 nor PySide2 is installed. Please install PySide6: pip install PySide6")

