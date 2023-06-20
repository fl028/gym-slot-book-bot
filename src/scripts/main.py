from googlecalendar import Gmail
from seleniumbot import Bot
from logger import Logger

if __name__ == '__main__':
    logger = Logger()

    mail = Gmail(logger)
    mail.GetEvents()
    event = mail.FilterRelevantEvent()

    if event != None:
        bot = Bot(logger)
        bot.book(event)
        bot.teardown()
    else:
        print("No bookings for tomorrow!")
    
