import unittest
from selenium import webdriver

class draftTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Edge()
    def tearDown(self):
        self.browser.quit()

    def test_if_this_is_the_draft_app(self):
        '''home page identifies itself as a draft app'''

        self.browser.get('http://localhost:5001')
        assert 'TEST' in self.browser.title.upper()

    def test_if_team_selection_buttons_are_present(self):
        '''
        user is provided a selection of buttons,
         who's value corresponds to the number of teams in the draft
        '''

        self.browser.get('http://localhost:5001')
        assert len(self.browser.find_elements_by_xpath('//label')) == 12


if __name__ == '__main__':
    unittest.main(warnings='ignore')
