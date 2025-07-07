#! /usr/bin/env python

import logging
import pandas as pd
import json
import os


logger = logging.getLogger(__name__)


class CellmapsannotatehierarchyRunner(object):
    """
    Class to run algorithm
    """
    def __init__(self, exitcode, input_file=None, annotation_type='biological process', config_file=None):
        """
        Constructor

        :param exitcode: value to return via :py:meth:`.CellmapsannotatehierarchyRunner.run` method
        :type int:
        :param input_file: path to input file (CSV/TSV), defaults to 'input.tsv'
        :type str:
        :param annotation_type: type of annotation to use, defaults to 'biological process'
        :type str:
        :param config_file: path to config file, defaults to '../gpt4_config.json'
        :type str:
        """
        self._exitcode = exitcode
        self.input_file = input_file or './data/example_NeST_table_sub.tsv'  
        self.annotation_type = annotation_type
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), '../gpt4_config.json')
        logger.debug('In constructor')

    def run(self):
        """
        Runs CellMaps Annotate Hierarchy


        :return:
        """
        logger.debug('In run method')
        # Read config
        with open(self.config_file) as f:
            config = json.load(f)
        model = config.get('MODEL', 'gpt-4-1106-preview')
        # Read dataframe
        if self.input_file.endswith('.csv'):
            df = pd.read_csv(self.input_file)
        else:
            df = pd.read_csv(self.input_file, sep='\t')
        # Iterate through dataframe and print model/annotation_type for each row (placeholder)
        for idx, row in df.iterrows():
            print(f"Row {idx}: Model={model}, AnnotationType={self.annotation_type}")
        return 0
