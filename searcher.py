from parser_module import Parse
from ranker import Ranker
import utils


class Searcher:

    def __init__(self, inverted_index, config=None):
        """
        :param inverted_index: dictionary of inverted index
        """
        #self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.config = config

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        relevant_docs = {}
        for term in query[0]: # query[0] because of the adittinonal dict to the end of capital
            try:
                if term in self.inverted_index.keys():
                    posting_file_pointer = str(self.inverted_index[term][1])
                    posting_file = utils.load_pickle_as_dict(posting_file_pointer,self.config.get_out_path())
                    all_tuples_for_term = posting_file[term]
                    for tweet_tuple in all_tuples_for_term:
                        if term not in relevant_docs.keys():
                            relevant_docs[term] = []
                            relevant_docs[term].append(tweet_tuple) # insert tweet information & tweet score
                        else:
                            relevant_docs[term].append(tweet_tuple)
            except:
                #print('term {} not found in posting'.format(term))
                pass
        return relevant_docs