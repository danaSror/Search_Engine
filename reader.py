import os
import pandas as pd
from tqdm import tqdm


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")

        return df.values.tolist()

    def read_all_parquet(self):
        """
        reads all the parquet file
        :param
        :return: list which contain another list of tweets
        """
        parquet_list = []
        with os.scandir(self.corpus_path) as entries1:
            for entry1 in entries1:
                if not entry1.name == ".DS_Store":
                    file_path = self.corpus_path+"\\" +entry1.name
                    if not entry1.name.endswith(".parquet"):
                        with os.scandir(file_path) as entries2:
                            for entry2 in entries2:
                                if not entry2.name == ".DS_Store":
                                    file_path = entry1.name + "\\" + entry2.name
                                    list = self.read_file(file_name=file_path)
                                    parquet_list.append(list)
                    else:
                        parquet_list.append(self.read_file(file_name=file_path))

        return parquet_list

