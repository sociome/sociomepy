'''geometry.py defines geometric matches of two SociomeDataFrames
'''

from ..data import SociomeDataFrame

class GeometricMatcher(object):
    '''GeometricMatcher uses latitude and longitude conditions to integrate SociomeDataFrames
    '''

    def __init__(self, distance_thresh=1e-4):
        '''Constructs a GeometricMatcher. There is a distance threshold to reject obvious non-matches
        and it uses a threshold of 4 decimal places.
        '''

        self.distance_thresh = distance_thresh

    def match(self, sdf1, sdf2):
        data = sdf1.data.sjoin_nearest(sdf2.data, max_distance=self.distance_thresh, how='inner')
        s = SociomeDataFrame()
        s.data = data
        s.subdivisions = sdf1.subdivisions + sdf2.subdivisions
        return s



