import schedule
import time
import datetime
from googlecalendar import Gmail
from seleniumbot import Bot
from logger import Logger

def CheckEventsAndPerformBooking(logger, mail):
    bot = Bot(logger)
    mail.GetEvents()
    event = mail.FilterRelevantEvent()
    if event is not None:
        bot.book(event)
        bot.teardown()
    else:
        logger.info("No bookings for tomorrow!")

if __name__ == '__main__':
    logger = Logger()
    mail = Gmail(logger)
    
    # Schedule the task to run at 17:00 every day
    schedule.every().day.at("17:00").do(CheckEventsAndPerformBooking, logger=logger, mail=mail)

    while True:
        schedule.run_pending()
        logger.debug("bot idle " + str(datetime.datetime.now()))
        time.sleep(30)
