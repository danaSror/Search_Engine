from nltk.stem import snowball

from nltk.tokenize import word_tokenize



class Stemmer:
    def __init__(self):
        self.stemmer = snowball.SnowballStemmer("english")



    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)
