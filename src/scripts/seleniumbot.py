# basic imports
import time
import os
import json
from datetime import datetime, timedelta

# selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class Bot:
    def __init__(self,Logger):
        self.Logger = Logger
        self._get_config()
        self._get_driver()
        self.Logger.info("Gym slot book bot instantiated!")

    def _get_config(self):
        self.root_directory = os.path.dirname(os.path.abspath(__file__)).split("src")[0]

        # constants
        file_path_constants = os.path.join( self.root_directory , 'src','data','constants.json')
        with open(file_path_constants, 'r', encoding='utf-8') as file:
            json_data_constants = file.read()
        self.constants_data_dict = json.loads(json_data_constants)

        # accounts
        file_path_accounts = os.path.join( self.root_directory , 'src','data','accounts.json')
        with open(file_path_accounts, 'r', encoding='utf-8') as file:
            json_data_accounts = file.read()
        self.accounts_data_dict = json.loads(json_data_accounts)

        self.Logger.info("Config is done!")

    def _get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        service = Service(executable_path=self.constants_data_dict["chromedriver_exe_path"])
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.Logger.info("Driver is ready!")

    def book(self, booking_date):
        for account in self.accounts_data_dict:
            self.Logger.info("Account: " + account)
            self._get_course_table(account)
            self._filter_course_table()
            self._perform_booking(booking_date)
            self._logout()

    def _get_course_table(self,account_name):
        try:
            # first page
            self.driver.get(self.constants_data_dict["elements_url"]);
            time.sleep(1) 
            email_input_search = self.driver.find_element(By.ID, self.constants_data_dict["html_elements"]["email_login_input_id"])
            email_input_search.send_keys(self.accounts_data_dict[account_name]["Username"])
            time.sleep(1)
            password_input_search = self.driver.find_element(By.ID, self.constants_data_dict["html_elements"]["password_login_input_id"])
            password_input_search.send_keys(self.accounts_data_dict[account_name]["Password"])
            time.sleep(1) 
            button_search = self.driver.find_element(By.CSS_SELECTOR, self.constants_data_dict["html_elements"]["button_login_css_selector"])
            button_search.click()
            time.sleep(1)

            # second page
            select_studio_search = self.driver.find_element(By.NAME, self.constants_data_dict["html_elements"]["studio_selector_name"])
            select_studio = Select(select_studio_search)
            time.sleep(1)
            select_studio.select_by_visible_text(self.constants_data_dict["html_elements"]["studio_selection_text"])
            time.sleep(1) 

            # table
            self.book_button = None
            self.slot_table_dict = {}
            table_search = self.driver.find_element(By.CLASS_NAME, self.constants_data_dict["html_elements"]["studio_course_plan_table_class"])
            table_search_rows = table_search.find_elements(By.CLASS_NAME, "ct-tr")
            self.Logger.info("Found rows: " + str(len(table_search_rows)))

            for row_index in range(len(table_search_rows)):
                #print("Process row nr: " + str(row_index))
                self.slot_table_dict[str(row_index)] = {}

                columns = table_search_rows[row_index].find_elements(By.CLASS_NAME, "ct-td")

                for column_index in range(len(columns)):
                    #print("Process column nr: " + str(column_index))
                    self.slot_table_dict[str(row_index)][self.constants_data_dict["TableColumns"][column_index]] = columns[column_index].text

                    if columns[column_index].text == "PLATZ RESERVIEREN":
                        self.book_button = columns[column_index].find_element(By.CLASS_NAME, "button")

                    
            time.sleep(1) 
        except Exception as e:
            self.Logger.warning("Error while booking: "  + str(e))
    
    def _convert_to_date_time(self, date_string):
        date_string = date_string.split(',')[1]
        date_string = date_string.replace(" ", "")
        date_format = "%d.%m.%Y"
        date_object = datetime.strptime(date_string, date_format)
        return date_object

    def _filter_course_table(self):
        self.bookable_date = None

        for row_index in range(len(self.slot_table_dict)):
            for column_name in self.slot_table_dict[str(row_index)]:
                if self.slot_table_dict[str(row_index)]["Action"] == "PLATZ RESERVIEREN":
                    self.bookable_date = self._convert_to_date_time(self.slot_table_dict[str(row_index)]["Date"])

        self.Logger.info("Bookable date: " + str(self.bookable_date))
    
    def _perform_booking(self,booking_date):

        if self.bookable_date == None:
            self.Logger.warning("Booking not possible!")
            return
        
        if booking_date.date() == self.bookable_date.date():
            self.Logger.info("Booking is possible!")
            self.book_button.click()
            self.Logger.info("Booking is done!")

        time.sleep(1)

    def _logout(self):
        time.sleep(1)
        logout_button = self.driver.find_element(By.CLASS_NAME, "button")
        logout_button.click()
        self.Logger.info("Logout!")
        time.sleep(1)

    def teardown(self):
        time.sleep(1)
        self.driver.quit()
        self.Logger.info("Teardown!")
        
