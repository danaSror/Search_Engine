import pickle
import os

# ---------------------------- list ----------------------------
def save_list_as_pickle(obj, name, path):
    """
    This function save an object as a pickle.
    :param path:
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(os.path.join(path, name) + '.pkl', 'wb') as pickle_file:
        next_clear_position_to_write = pickle_file.tell()
        for pair in obj:
            pickle.dump(pair, pickle_file, pickle.HIGHEST_PROTOCOL)
        return next_clear_position_to_write

def load_pickle_as_list(name, path, offset, chunk_length=0):
    """
    This function will load a pickle file
    :param path:
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    list = []
    with open(os.path.join(path, name) + '.pkl', 'rb') as pickle_file:
        pickle_file.seek(offset)
        if chunk_length == 0:
            while True:
                try:
                    list.append(pickle.load(pickle_file))
                except:
                    return list
        for i in range(chunk_length):
            try:
                list.append(pickle.load(pickle_file))
            except:
                next_clear_position_to_write = pickle_file.tell()
                return list, next_clear_position_to_write

        next_clear_position_to_write = pickle_file.tell()
        return list, next_clear_position_to_write
# --------------------------------------------------------------

# ---------------------------- dict ----------------------------
def load_pickle_as_dict(name, path):
    """
    This function will load a pickle file
    :param path:
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    dict = {}
    with open(os.path.join(path, name) + '.pkl', 'rb') as pickle_file:
        while True:
            try:
                 pair = pickle.load(pickle_file)
                 dict[pair[0]] = pair[1]
            except:
                return dict

def save_dict_as_pickle(obj, name, path):
    """
    This function save an object as a pickle.
    :param path:
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(os.path.join(path, name) + '.pkl', 'wb') as pickle_file:
        #to_be_told = pickle_file.tell()
        for pair in obj.items():
            pickle.dump(pair, pickle_file, pickle.HIGHEST_PROTOCOL)
# --------------------------------------------------------------

def load_queries_list(queries):
    if type(queries) is list:
        return queries

    queries_list = []
    with open(queries, 'r', encoding='utf-8') as queries_file_txt:
        for line in queries_file_txt:
            if line != '\n':
                for i in range(0,4):
                    if line[0].isnumeric():
                        line = line.replace(line[0], "")
                    elif line[0] == ".":
                        line = line.replace(line[0], "")

                queries_list.append(line)

    return queries_list

def load_inverted_index():
    return None

def load_inverted_index(path):
    new_dict = {}
    with open(os.path.join(path, 'inverted_idx') + '.pkl', 'rb') as f:
        while True:
            try:
                 pair = pickle.load(f)
                 new_dict[pair[0]] = pair[1][0]
            except:
                return new_dict