""":mod:`pyside_program_config` --
Command-line argument parsing combined with the power of QSettings.
"""

import metadata
__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright

from program_config import (ProgramConfig,
                            RequiredKeyError,
                            DuplicateKeyError)
