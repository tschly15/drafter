import time
import unittest
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class draftTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Edge()
    def tearDown(self):
        self.browser.quit()

    def est_if_this_is_the_draft_app(self):
        '''home page identifies itself as a draft app'''

        self.browser.get('http://localhost:5001')
        assert 'TEST' in self.browser.title.upper()

    def est_if_team_selection_buttons_are_present(self):
        '''
        user is provided a selection of buttons,
         who's value corresponds to the number of teams in the draft
        '''

        self.browser.get('http://localhost:5001')
        assert len(self.browser.find_elements_by_xpath('//label')) == 12

    def est_selecting_the_positions(self):
        '''
        ensure the positions selected in the drop down 
         correlate to available positions of the league
        '''
        self.browser.get('http://localhost:5001')
        input_box = self.browser.find_elements_by_xpath('//input[@value="Register"]')[0]

        #select the league settings (Enter yields defaults)
        input_box.send_keys(Keys.ENTER)
        time.sleep(.5)

        #confirm the league settings
        input_box = self.browser.find_elements_by_xpath('//button[@name="confirmed"]')[0]
        input_box.send_keys(Keys.ENTER)

    def est_adding_a_keeper(self):
        self.est_selecting_the_positions()
        time.sleep(8)

        #select the team the keeper belongs to
        #select the round the keeper belongs to
        #select the name of the keeper
        for selection in ('team','round','name'):
            options = self.browser.find_elements_by_xpath('//button[@name="user_selected"]')
            assert len(options) > 2

            random_choice = randint(0, len(options)-1)
            selection = options[random_choice]
            selection.send_keys(Keys.ENTER)
            time.sleep(1)

        #confirm the selected keepers 
        input_box = self.browser.find_elements_by_xpath('//button[@name="confirmed"]')[0]
        input_box.send_keys(Keys.ENTER)

    def test_drafting_when_selecting_a_specific_keeper(self):
        self.est_selecting_the_positions()
        time.sleep(8)

        #select the team the keeper belongs to
        #select the round the keeper belongs to
        #select the name of the keeper
        for choice in (4,1,9):
            selection = self.browser.find_elements_by_xpath('//button[@name="user_selected"]')[choice]
            selection.send_keys(Keys.ENTER)
            time.sleep(1)

        #confirm the selected keepers 
        input_box = self.browser.find_elements_by_xpath('//button[@name="confirmed"]')[0]
        input_box.send_keys(Keys.ENTER)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
