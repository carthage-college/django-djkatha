# import datetime
# from datetime import date
# from datetime import datetime, timedelta
import time
import smtplib
from time import strftime
import logging
from logging.handlers import SMTPHandler

from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# django settings for script
from django.conf import settings

DEBUG = settings.INFORMIX_DEBUG

# set up command-line options
desc = """
    Upload ADP data to CX
"""


# create logger
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)



def fn_write_error(msg):
    # create error file handler and set level to error
    handler = logging.FileHandler(
        '{0}Raisers_edge_error.log'.format(settings.LOG_FILEPATH))
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.error(msg)
    handler.close()
    logger.removeHandler(handler)
    fn_clear_logger()
    return "Error logged"



def fn_send_mail(to, frum, body, subject):
    """
    Stock sendmail in core does not have reply to or split of to emails
    --email to addresses may come as list
    """

    server = smtplib.SMTP('localhost')
    try:
        msg = MIMEText(body)
        msg['To'] = to
        msg['From'] = frum
        msg['Subject'] = subject
        txt = msg.as_string()

        # print("ready to send")
        # show communication with the server
        # if debug:
        #     server.set_debuglevel(True)
        # print(msg['To'])
        # print(msg['From'])
        server.sendmail(frum, to.split(','), txt)

    finally:
        server.quit()
        # print("Done")
        pass






def fn_clear_logger():
    logging.shutdown()
    return("Clear Logger")
