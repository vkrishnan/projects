from robot import version as robot_version
from robot.libraries.BuiltIn import BuiltIn
from RoboGalaxyLibrary.utilitylib import logging as logger
from version import get_version
from library.windows_library import WMILibrary
from library.spp_utility import Utility
from library.spp_common import Common
from library.spp_parser import SppParser
from library.SeleniumApi import SeleniumApi
from RoboGalaxyLibrary.utilitylib import logging as logger

__version__ = get_version()

class SppLibrary(WMILibrary,
                Utility,
                Common,
                SppParser,
                SeleniumApi):
    """ SppLibrary is an HP internal test library for the Robot Framework
     Prior to running test cases using RoboGalaxyLibrary, RoboGalaxyLibrary must be
     imported into your Robot test suite (see `importing` section).

    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        logger._log_to_console_and_log_file("########################################################")
        logger._log_to_console_and_log_file("Developed by HP SPP Automation Team")


        for base in SppLibrary.__bases__:
            base.__init__(self)