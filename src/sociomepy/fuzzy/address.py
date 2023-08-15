'''address.py defines fuzzy matches of two SociomeDataFrames
'''
import pandas as pd
from fuzzywuzzy import fuzz

class AddressMatcher(object):
    '''
    An address matcher identifies the best one-to-one assignment between two
    sociomedataframes using a fuzzy matching algorithm.
    '''

    def __init__(self, address_left, address_right):
        '''Constructor for an AddressMatcher object.
        '''
        self.address_left = address_left
        self.address_right = address_right


