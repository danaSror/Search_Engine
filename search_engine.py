from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import pandas as pd
from posting_merge import PostingsMerge
from tqdm import tqdm

def run_engine(config):
    """

    :param config:
    :return:
    """
    number_of_documents = 0

    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(config.toStem)
    indexer = Indexer(config)
    paruet_list = r.read_all_parquet()
    for list in paruet_list:
        #for i in tqdm(range(0,len(list))): # for every doc
        for i in range(0, len(list)):  # for every doc
            # parse the document
            parsed_document = p.parse_doc(list[i])
            if parsed_document is None:
                continue
            number_of_documents += 1

            # index the document data
            indexer.add_new_doc(parsed_document)

    #print('Finished parsing and indexing. Starting to export files')

    indexer.save_postings()     # saves the remaining posting file .
    PostingsMerge(indexer).chunks_merging()
    utils.save_dict_as_pickle(indexer.inverted_idx, "inverted_idx", config.get_out_path())

def load_index(out_path=''):
    """
    load inverted index
    :param out_path:
    :return:
    """
    #print('Load inverted index and document dictionary')
    inverted_index = utils.load_pickle_as_dict("inverted_idx", out_path)
    #print('Done')
    return inverted_index


def search_and_rank_query(query, inverted_index, k, config=None):
    """
    This function search for relevant docs according to the query and rank them
    :param query:
    :param inverted_index:
    :param k:
    :param config:
    :return:
    """
    p = Parse(config.toStem)
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index, config)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    if queries is not None:
        config = ConfigClass(corpus_path, output_path, stemming)
        run_engine(config)
        query_list = utils.load_queries_list(queries)
        inverted_index = load_index(output_path)
        for idx in range(1, len(query_list)+1):
            print("query {}:".format(idx))
            for doc_tuple in search_and_rank_query(query_list[idx-1], inverted_index, k=num_docs_to_retrieve, config=config):
                print('\ttweet id: {} | score : {} '
                      .format(doc_tuple[0] , doc_tuple[1]))



