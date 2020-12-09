import bisect
import math

import numpy as np
from numpy.linalg import norm
import utils


class Ranker:
    def __init__(self):
       pass


    @staticmethod
    def rank_relevant_doc(relevant_doc):
        """
        This function calculate score for Wij - whigt of term i in doc j according to Inner product module .
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        renk_doc_dict = {} # dict lookes like : {"term" : Wij }
        for term in relevant_doc:
            for tweet_tuple in relevant_doc[term]:
                fij = tweet_tuple[4]                               # - The number of times term i shows in tweet j
                tweet_len = int(tweet_tuple[1])                    # - The number of terms shows in the current tweet
                dfi = len(relevant_doc[term])                      # - The number of tweets/docs which term i show in all the corpus
                wij = (fij/tweet_len) * math.log10(1000000/dfi)    # - The score for term i in doc j
                if tweet_tuple[0] not in renk_doc_dict:
                    renk_doc_dict[tweet_tuple[0]] = wij
                else:
                    renk_doc_dict[tweet_tuple[0]] += wij # sim(dij,query) = sum(wij*wiq) , in this case wiq = 1


        return sorted(renk_doc_dict.items(), key=lambda item: int(item[1]*100), reverse=True)


    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=2000):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]



