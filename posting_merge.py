import utils
import numpy as np

class PostingsMerge:
    def __init__(self, indexer):
        self.indexer = indexer
        self.merged_postings = []
        self.data_read_so_far = 0

    def chunks_merging(self):
        """
        This function merge between posting file
        it doing this by iteration, every chunks we make the merge
        :return:
        """
        chunk_size = 250000 // self.indexer.number_of_posting_file + 1
        chunks_postings = []
        chunks_indexes = np.zeros(shape=(len(self.indexer.least_pos_at_postings )), dtype=np.int32)
        #   scan posting file and read chunk from each one and add theme
        for posting_pointer in self.indexer.least_pos_at_postings:
            loadChunk, offset = utils.load_pickle_as_list(posting_pointer, self.indexer.config.get_out_path(), self.indexer.least_pos_at_postings[posting_pointer],
                                             chunk_size)
            self.indexer.least_pos_at_postings[posting_pointer] = offset
            chunks_postings.append(loadChunk)


        temp_merge_list = []
        there_is_still_posting_to_read = True

        while there_is_still_posting_to_read:
            finish_read_currrent_chunk = -1
            while finish_read_currrent_chunk == -1:
                term_to_enter = self.find_term(chunks_postings, chunks_indexes)
                tuples_to_merge = []
                indexes_of_the_indexes_to_increase = []

                # find all the tuples that should be merged
                for idx, term_idx_in_chunk in enumerate(chunks_indexes):
                    if term_idx_in_chunk < len(chunks_postings[idx]) and \
                            chunks_postings[idx][term_idx_in_chunk][0] == term_to_enter:
                        tuples_to_merge.append(chunks_postings[idx][term_idx_in_chunk])
                        indexes_of_the_indexes_to_increase.append(idx)

                merged_tuple = self.merge_all_tuple_for_term(tuples_to_merge)
                appended_term = merged_tuple[0]

                should_append = True
                # if the term freq is 1 => then delet this term
                if appended_term in self.indexer.inverted_idx and self.indexer.inverted_idx[appended_term][0] == 1:
                    self.indexer.inverted_idx.pop(appended_term, None)
                    should_append = False

                should_append, merged_tuple = self.handle_names_and_entites(should_append, appended_term,merged_tuple)

                if should_append:
                    self.data_read_so_far += len(merged_tuple[1])
                    temp_merge_list.append(merged_tuple)
                    self.indexer.inverted_idx[merged_tuple[0]][1] = str(self.indexer.number_of_posting_file)

                # increase the indices that the tuple at the specific location have been inserted to the new posting
                for idx in indexes_of_the_indexes_to_increase:
                    chunks_indexes[idx] += 1

                finish_read_currrent_chunk = self.test_if_finish_read_currrent_chunk(chunks_postings, chunks_indexes)

                if self.data_read_so_far >= 400000:
                    self.merging_temp_chunks(temp_merge_list)
                    self.data_read_so_far = 0
                    self.indexer.number_of_posting_file += 1
                    del temp_merge_list
                    temp_merge_list = []

                # ---------------------------------------------------------------------- end small while

            # loads new chunks into the save_chunks list in the relevant indices.
            for index in finish_read_currrent_chunk:
                loadChunk, offset = utils.load_pickle_as_list(str(index), self.indexer.config.get_out_path(),
                                                 self.indexer.least_pos_at_postings[str(index)], chunk_size)
                chunks_postings[index] = loadChunk
                chunks_indexes[index] = 0
                self.indexer.least_pos_at_postings[str(index)] = offset

            # checks whether all postings are done.
            there_is_still_posting_to_read = False
            for chunk in chunks_postings:
                if len(chunk) > 0:
                    there_is_still_posting_to_read = True
                    break
        # ------------------------------------------------------------------------------- end big while

        # save of the last posting file.
        if len(temp_merge_list) > 0:
            self.merging_temp_chunks(temp_merge_list)
            del temp_merge_list
           # temp_merge_list.clear()
        for i in range(0,len(self.merged_postings)):
            print(str(self.merged_postings[idx]))

    def merging_temp_chunks(self,temp_merge_list):
        """
        After merging the chunks , save the posting to disk
        :param temp_merge_list:
        :return:
        """
        self.merged_postings.append(str(self.indexer.number_of_posting_file))
        utils.save_list_as_pickle(temp_merge_list, str(self.indexer.number_of_posting_file),self.indexer.config.get_out_path())

    def find_term(self, chunks_postings, chunks_indexes):
        """
        find the next term which need to ce appended
        :param chunks_postings:
        :param chunks_indexes:
        :return:
        """
        term = None
        for idx, chunk in enumerate(chunks_postings):
            if len(chunk) > 0:
                term = chunks_postings[idx][chunks_indexes[idx]][0]
        for idx in range(len(chunks_postings)):
            if chunks_indexes[idx] < len(chunks_postings[idx]) and \
                    chunks_postings[idx][chunks_indexes[idx]][0] < term:
                term = chunks_postings[idx][chunks_indexes[idx]][0]
        return term

    def test_if_finish_read_currrent_chunk(self, chunks_postings, chunks_indexes):
        """
        This function checke whether we finish read data from chunk or not
        :param chunks_postings:
        :param chunks_indexes:
        :return:
        """
        list = []
        for i in range(len(chunks_postings)):
            if chunks_indexes[i] >= len(chunks_postings[i]):
                list.append(i)
        if len(list) == 0:
            return -1
        return list

    def merge_all_tuple_for_term(self, tuples_to_merge):
        """
        Merge all tuples for term
        :param tuples_to_merge:
        :return:
        """
        # if there is not tuple to merge, only one tuple
        if len(tuples_to_merge) == 1:
            return tuples_to_merge[0]
        merging_tuple = (tuples_to_merge[0][0], [])
        for tuple in tuples_to_merge:
            merging_tuple[1].extend(tuple[1])
        merging_tuple[1].sort(key=lambda x: x[0])
        return merging_tuple

    def handle_names_and_entites(self,should_append,appended_term,merged_tuple):
        """
        This function checke if the term is actually an entity or not,
        before adding it to inverted index and before write this to disk
        :param should_append:
        :param appended_term:
        :param merged_tuple:
        :return:
        """
        if appended_term in self.indexer.entities_dict and self.indexer.entities_dict[appended_term] < 2:
            should_append = False
            self.indexer.inverted_idx.pop(appended_term, None)
            # if the term with capital letter so insert the term to indexer with upper first char
        try:
            if appended_term in self.indexer.global_dict and self.indexer.global_dict[appended_term]:
                merged_tuple = (appended_term.upper(), merged_tuple[1])
                temp_val = self.indexer.inverted_idx[appended_term]
                self.indexer.inverted_idx.pop(appended_term, None)  # get ouh the lower word
                self.indexer.inverted_idx[appended_term.upper()] = temp_val  # insert the word upper
        except:
            pass
        return should_append,merged_tuple
