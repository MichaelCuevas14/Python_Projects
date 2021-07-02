from pip._vendor.distlib.compat import raw_input
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import time
from datetime import date

my_email = raw_input("Email: ")
my_password = input("Password: ")
my_cvv = input("Credit card cvv: ")

print("Please Wait")

browser = webdriver.Firefox()
browser.set_page_load_timeout(60)
browser.get(
    'https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149')
time.sleep(5)

all_buttons = browser.find_elements_by_tag_name("button")
all_buttons = [i.text for i in all_buttons]


date = date.today()
is_available = ""


class Bot:

    def start(self):
        if "Sold Out" in all_buttons:
            print("item not in stock")
            is_available = False
            while is_available is False:
                browser.refresh()
                self.start()

        if "Add to Cart" in all_buttons:
            Add_to_cart_button = browser.find_element_by_xpath(
                '/html/body/div[3]/main/div[2]/div/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div/button')
            print("item is in stock")
            is_available = True

            try:
                Add_to_cart_button.click()
            except Exception as e:
                time.sleep(2)
                Add_to_cart_button.click()
                print("2nd add to cart attempt")

            time.sleep(2)
            Go_to_cart_button = browser.find_element_by_xpath(
                '/html/body/div[8]/div/div[1]/div/div/div/div/div[1]/div[3]/a')
            try:

                Go_to_cart_button.click()

            except Exception as e:
                Add_to_cart_button.click()
                Go_to_cart_button.click()

            time.sleep(5)

            try:  # checks there is a pop up and closes it prior to continuing
                Pop_up_button = browser.find_element_by_xpath(
                    '/html/body/div[1]/main/div/div[2]/div[1]/div/div[1]/div[1]/section[2]/div/div/div[4]/div/div[3]/div['
                    '1]/div/div/div/div/button')
                Pop_up_button.click()
            except Exception as e:
                print("No pop up")


            Checkout_button = browser.find_element_by_xpath(
                '/html/body/div[1]/main/div/div[2]/div[1]/div/div[1]/div[1]/section[2]/div/div/div[4]/div/div[1]/button')
            Checkout_button.click()
            time.sleep(3)
            email = browser.find_element_by_id("fld-e")  #fills out login info
            password = browser.find_element_by_id("fld-p1")
            email.send_keys(my_email)
            password.send_keys(my_password)
            password.send_keys(Keys.RETURN)  #Enter Login info
            time.sleep(10)
            Payment_info_button = browser.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/main/div[2]/div[2]/form/section/div/div[2]/div/div/button')
            Payment_info_button.click()
            cvv = browser.find_element_by_id("credit-card-cvv")
            cvv.send_keys(my_cvv)
            Place_order = browser.find_element_by_xpath(
                "/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/main/div[2]/div["
                "3]/div/section/div[3]/div[2]/button")
            Place_order.click()

        with open("ps5_availability.csv", "a") as csvfile:
            write = csv.writer(csvfile)
            write.writerow([date, is_available])

        browser.close()


bot = Bot()
bot.start()
