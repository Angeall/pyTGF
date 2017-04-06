import unittest

import pandas as pd

from pytgf.data.decode.action_sequence_decoder import ActionSequenceDecoder

__author__ = "Anthony Rouneau"


class TestActionSequenceDecoder(unittest.TestCase):
    def test_correct_output(self):
        data1 = [[0, 2, 0, 3, 1],
                 [1, 3, 5, 1, 0],
                 [1, 5, 3, 4, 0],  # Only winning sequence for player 0
                 [0, 3, 2, 4, 4],
                 [0, 5, 0, 5, 1],
                 [0, 2, 1, 3, 2]]
        data2 = [[0, 4, 5],
                 [1, 3, 1],
                 [1, 2, 4],
                 [0, 1, 2],
                 [1, 4, 3],
                 [0, 3, 1]]
        dataset = pd.DataFrame(data1)
        dataset = dataset.append(pd.DataFrame(data2), ignore_index=True)
        decoder = ActionSequenceDecoder(1, ".", 0, 2)
        result = decoder._parseDataFrame(dataset)

        self.assertEqual(result[0], [[5, 3], [3, 2], [4, 4], [0, 4]])
        self.assertEqual(result[1], [[2, 1], [4, 2]])
        self.assertEqual(result[2], [[4, 3], [3, 1]])