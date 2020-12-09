import utils
from collections import Counter, OrderedDict


class Indexer:
    def __init__(self, config):
        """

        :param config:
        """
        self.inverted_idx = {}

        self.posting_list = []
        self.pointers_posting_dict = {}

        self.number_of_posting_file = 0
        self.least_pos_at_postings = OrderedDict()

        self.global_dict = {}
        self.entities_dict = Counter()
        self.config = config

    def add_new_doc(self, document):
        """
        This function add new doc to the inverted index and creating postings files
        :param document:
        :return:
        """
        # ------------------------ entitys & names ---------------------------
        for entity in document.entities_set:
            self.entities_dict[entity] += 1
        doc_capitals = document.capital_dict
        for word in doc_capitals:
            if word not in self.global_dict:
                self.global_dict[word] = doc_capitals[word]
            else:
                if not doc_capitals[word]:
                    self.global_dict[word] = False
        # ---------------------------------------------------------------------

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                if term in self.inverted_idx:
                    if term not in self.pointers_posting_dict:
                        self.pointers_posting_dict[term] = None

                    self.inverted_idx[term][0] += 1

                else:
                    self.inverted_idx[term] = [1, str(self.number_of_posting_file)]
                    self.pointers_posting_dict[term] = None
                fij = len(document_dictionary[term]) # term freq in the doc
                doc_tuple = (document.tweet_id, document.doc_length,document.max_tf,document.unique_terms_in_doc,fij)

                # if there're no documents for the current term, insert the first document
                if self.pointers_posting_dict[term] is None:
                    self.posting_list.append((term, [doc_tuple]))
                    self.pointers_posting_dict[term] = len(self.posting_list) - 1
                else:
                    tuple_idx = self.pointers_posting_dict[term]
                    self.posting_list[tuple_idx][1].append(doc_tuple)

                # check if pointers_posting_dict is full
                if len(self.posting_list) == 250000:
                    self.save_postings()

            except:
                #print('problem with the following key {}'.format(term))
                pass

    def save_postings(self):
        """
        save posting file to disk
        :return:
        """
        object_to_save = sorted(self.posting_list, key=lambda x: x[0])
        posting_file_name = str(self.number_of_posting_file)
        self.least_pos_at_postings[posting_file_name] = \
            utils.save_list_as_pickle(object_to_save, posting_file_name,self.config.get_out_path())
        self.number_of_posting_file += 1
        del self.pointers_posting_dict
        self.pointers_posting_dict = {}
        del self.posting_list
        self.posting_list = []




