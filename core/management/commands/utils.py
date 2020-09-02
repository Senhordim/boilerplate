import logging
import sys


class Utils(object):
    @staticmethod
    def show_message(text: str, error: bool = False):
        __log = logging.getLogger('logger')
        __log.setLevel(logging.INFO)
        """Method do show message in console"""
        """Method for displaying friendly messages on the flow of script execution on the terminal.

        Arguments:
            message {str} -- Message to be displayed on the terminal
            error {bool} -- Attribute that determines whether the message is an error,
                            being an error message the execution of the program is ended
        """
        try:
            if error:
                __log.error(f"\n{'!=' * len(text)}\nERROR: {text.upper()}\n")
                sys.exit()
            else:
                __log.warning(text)
        except Exception as error:
            logging.error(error)
