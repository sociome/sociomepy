'''Copyright (C) University of Chicago - All Rights Reserved

matching.py contains the main architecture for matching geographical
entities in different sociomedataframes.

* Major Update Log
09/15/2022 - Main Architecture Designed
'''
import pandas as pd
from fuzzywuzzy import fuzz


def add_exact_condition(self, left_attr, right_attr, left_xform=(lambda x: x), right_xform=(lambda x: x)):
    '''Adds attributes that have to be exactly matched.

            Parameters:
                    left_attr (str): attribute on the left side
                    right_attr (str): attribute on the right side
                    left_xform (lambda): transformations to apply the left side
                    right_xform (lambda): transformations to apply to the right side
   '''

    self.blocker_left.append(left_attr)
    self.blocker_right.append(right_attr)

    self.left[left_attr] = self.left[left_attr].apply(left_xform)
    self.right[right_attr] = self.right[right_attr].apply(right_xform)


def add_address_match(self, left_attrs, right_attrs):
    '''Adds a fuzzy matching based on addresses

         Parameters:
                     left_attrs (List[str]): attributes on the left side
                    right_attrs (List[str]): attributes on the right side
    '''
    self.address_left = left_attrs
    self.address_right = right_attrs
    self.address_match = True


def match(self):
    left_groups = self.left.groupby(self.blocker_left)
    right_groups = self.right.groupby(self.blocker_right)

    matches = []

    for group in left_groups.groups:

        print(group)

        try:
            block_left = left_groups.get_group(group)
            block_right = right_groups.get_group(group)
        except:
            continue

        for indexL, rowL in block_left.iterrows():

            Lmatches = []

            for indexR, rowR in block_right.iterrows():

                if self.address_match:
                    s1 = ' '.join([str(rowL[attr]) for attr in self.address_left]).lower()
                    s2 = ' '.join([str(rowR[attr]) for attr in self.address_right]).lower()
                    score = fuzz.token_set_ratio(s1.lower(), s2.lower())

                    print(score, s1, s2)

                    Lmatches.append((score, rowR))
                else:
                    raise ValueError("No Address Matching Set")

            Lmatches.sort()
            matches.append(pd.concat([rowL, Lmatches[-1][1]]))

    return pd.DataFrame(matches)