from nltk.corpus import stopwords
from stemmer import Stemmer
from nltk.tokenize import word_tokenize
from document import Document
from WordsToNumber import WordsToNumber
import re


class Parse:

    def __init__(self,stemming=None):
        """
        constructor for this class
        :param stemming:
        """
        self.stop_words = stopwords.words('english')
        self.stemmer = None
        if stemming:
            self.stemmer = Stemmer()
        self.corona_list = ["SARS", "sars", "Severe Acute Respiratory Syndrome", "severe acute respiratory syndrome",
                       "SARS-CoV",
                       "SARS CoV", "sars-cov", "sars cov", "coronavirus", "corona virus", "COVID", "covid", "Covid",
                       "COVID-19",
                       "covid-19", "#coronavirus", "COVID__19", "#COVID", "#COVID-19", "#covid19", "#SARS"]

    def get_list_without_stopwords(self,list):
        """

        :param list:
        :return: list without stopwords
        """
        list_without_stopwords = []
        stop_words = stopwords.words('english')
        for w in list:
            if not w.lower() in stop_words:
                list_without_stopwords.append(w)
        return list_without_stopwords

    def check_If_Upper_More_Then_Lower(self,text):
        """
        This function check  the ratio of lower and upper case in a string
        :param text:
        :return: true ro false
        """
        if len(text) > 0:
            count = 0
            i = 0
            while i < len(text):
                if text[i].islower():
                    count = count + 1
                i = i + 1
        len1 = len(text)
        if len1 > 0:
            return count / len(text) < 0.5
        else:
            return False

    def upperToLowerAfterDot(self,list, index, new_tokens):
        """
        Convert word that appear after dot or : in text
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        if len(list) > index + 1:  # term term . &
            if len(list) > index + 2:
                if list[index + 1].isalpha() and not list[index + 2].isupper():
                    new_tokens.append(list[index + 1].lower())
                    list[index + 1] = ""

    def Hashtags(self,list, index, new_tokens):
        """
        This function get "@" and concat this term to the next term
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        if len(list) >= index + 1:
            word = list[index + 1]
            list[index + 1] = ""
            if "_" in word:
                words = word.rsplit("_")
            else:
                word = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), word, 1)
                words = re.findall('[A-Z][^A-Z]*', word)
            new_word = ""
            i = 0
            while i < len(words):
                new_tokens.append(words[i].lower())
                new_word = new_word + words[i].lower()
                i += 1
            new_tokens.append("#" + new_word)

    def tags(self,list, index, new_tokens):
        """
        This function separate the string on each time appear upper letter in
        the string to each time appears "_" to different terms
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        new_word = "@" + list[index + 1]
        new_tokens.append(new_word)
        new_tokens.append(list[index + 1].lower())
        list[index + 1] = ''

    def extractUrl(self,list, index):
        """
        Thos function separate the url to terms
        :param list:
        :param index:
        :return:
        """
        word = list[index]
        tokenize_list_url = re.compile(r'[\:/?=\-&]+', re.UNICODE).split(word)
        if len(tokenize_list_url) > 1:
            url = tokenize_list_url[1]
            if 'www.' in url:
                url2 = url.replace('www.', '')
                tokenize_list_url.append(url2)
        list.extend(tokenize_list_url)

    def handel_percent(self,list, index, new_tokens):
        """
        This function convert "percentage" or "percent" to % and
        concat the term which appears before the %
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        if not list[index - 1].isalpha():
            num = list[index - 1]
            new_word = num + "%"
            if index-1 < len(list):
                if  list[index-1] in new_tokens:
                    new_tokens.remove(list[index - 1])
            new_tokens.append(new_word)

    def convertNumbersUnits(self,list, index, new_tokens):
        """
        This function convert the units of number
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        numeric_list = WordsToNumber().getNumericWords()
        if index + 1 < len(list) and list[index + 1].lower() in numeric_list:
            num = float(list[index])
            numericNum = float(WordsToNumber().execute(list[index + 1]))
            new_Num = str(num * numericNum)
            new_word = WordsToNumber().handle_number(new_Num)
            list[index] = ''
            list[index + 1] = ''
            new_tokens.append(new_word)
        elif float(list[index]) >= 1000:
            new_word = WordsToNumber().handle_number(str(list[index]))
            list[index] = ''
            new_tokens.append(new_word)
        elif self.isFraction(list, index + 1):
            if "." not in list[index]:
                new_word = list[index] + " " + list[index + 1]
                list[index + 1] = ''
            else:
                new_word = list[index]
            new_tokens.append(new_word)
        else:
            new_tokens.append(list[index])

    def combainCapitalTerms(self,text_tokens):
        """
        This function concat two or more term which appears with capital letters one after one
        :param text_tokens:
        :return:
        """
        for index, word in enumerate(text_tokens):
            if len(word) > 0:
                if word[0].isupper():
                    try:
                        list_ca = self.capitalettersTerms(text_tokens, index)
                        text_tokens = text_tokens + list_ca
                    except:
                        print("Could not connect terms")
            if index == 3:
                break
        return text_tokens

    def capitalettersTerms(self,list, index):
        result = []
        i = 0
        word = list[index]
        if word[0].isupper():
            new_word = word
            i = index
            if i + 1 < len(list):
                i = i + 1
                loop = 1
                while list[i][0].isupper() and index + 1 == i and loop > 5:
                    loop += 1
                    new_word = new_word + " " + list[i]
                    index += 1
                    if i + 1 < len(list):
                        i += 1
                if not new_word in list:
                    result.insert(index, new_word)
            else:
                if list[index][0].isupper() and not new_word in list:
                    result.insert(index, list[index])
        else:
            i += 1
        return result

    def remove_emoji(self,string):
        """
        This function remove emoji from text
        :param string:
        :return:
        """
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # chinese char
                                   u"\U00002702-\U000027B0"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\U00010000-\U0010ffff"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u200d"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\ufe0f"  # dingbats
                                   u"\u3030"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    def isFraction(self,list, index):
        """
        This function checke whether the word is a fraction or not
        :param list:
        :param index:
        :return:
        """
        word = list[index]
        if "/" in word:
            word = word.replace("/", "")
            if word.isnumeric():
                return True
            else:
                return False
        elif "." in word:
            word = word.replace(".", "")
            if word.isnumeric():
                return True
            else:
                return False

    def isNumber(self,list, index):
        """
        This function checke whether the word is a number or not
        :param list:
        :param index:
        :return:
        """
        word = list[index]
        if "," in word:
            word = word.replace(",", "")
            if word.isnumeric():
                list[index] = word
                return True
            else:
                return False
        elif "." in word and word.count(".")==1:
            word = word.replace(".", "")
            if word.isnumeric():
                return True
        else:
            return str(list[index]).isnumeric()

    def handle_dashes(self,list, index, new_tokens):
        """
        This function separate the term by "-"
        :param list:
        :param index:
        :param new_tokens:
        :return:
        """
        dash_idx = list[index].find('-')
        if self.stemmer is None:
            new_tokens.append(list[index].lower())
            new_tokens.append(list[index][:dash_idx].lower())
            new_tokens.append(list[index][dash_idx + 1:].lower())
        else:
            new_tokens.append(self.stemmer.stem_term(list[index].lower()))
            new_tokens.append(self.stemmer.stem_term(list[index][:dash_idx].lower()))
            new_tokens.append(self.stemmer.stem_term(list[index][dash_idx + 1:].lower()))
        if list[index] in self.corona_list:
            new_tokens.append("corona")

    def parse_sentence(self,text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        new_capital_words = set()
        temp_entitie = ''
        will_merge = 0
        capital_dict = {}
        entities_set = set()

        #text = self.remove_emoji(text)     ****************************************
        #if self.cheak_If_Upper_More_Then_Lower(text): ************************
        #    text = text.lower()                      ******************************

        text_tokens = word_tokenize(text)
        try:
            url = ""
            if "http" in text:
                url = re.search("(?P<url>https?://[^\s]+)", text).group("url")
                if len(url) > 0:
                    text = text.replace(url, "")
                    text_tokens = word_tokenize(text)
        except:
            pass

        #text_tokens = self.get_list_without_stopwords(text_tokens) *******************************
        new_tokens = []
        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        for index, word in enumerate(text_tokens):
            if word == "" or word == " " or word.lower() in self.stop_words or word.lower().endswith("'s") or (len(word) == 1 and ord(word))> 126:
                continue
            # ------------------------------------------------------------------------ upper to lower
            elif word == "." or word == ":":
                self.upperToLowerAfterDot(text_tokens, index, new_tokens)
            #  -------------------------------------------------------------------------- HashTAG
            elif word == "#" and index <= len(text_tokens)-2:
                self.Hashtags(text_tokens, index, new_tokens)
            #   ----------------------------------------------------------------------------  Tags
            elif word == "@" and index <= len(text_tokens)-2:
                self.tags(text_tokens, index, new_tokens)
            #   ------------------------------------------------------------------------  percent %
            elif word == "percent" or word == "percentage" or word == '%':
                self.handel_percent(text_tokens, index, new_tokens)
            #   -------------------------------------------------------------------------- Dollars $ "the number is 80 $ and nata $"
            elif word == "$":
                new_tokens.append("dollars")
            #   ------------------------------------------------------------------------- 3 miliom ex
            elif not word.isalpha():
                if self.isNumber(text_tokens, index) or word.isnumeric():
                    try:
                        self.convertNumbersUnits(text_tokens, index, new_tokens)
                    except:
                        pass
                # ---------------------------------------------------------------- split the word by the dashes
                elif '-' in word and len(word) > 1:
                    self.handle_dashes(text_tokens, index, new_tokens)
            # -------------------------------------------------------------
            elif word in self.corona_list:
                new_tokens.extend([word,"corona"])
            # ------------------------------------------------- Otherwise, if it's just a normal word add it
            elif word.isalpha() or word.isnumeric():
                if self.stemmer is not None:
                    word = self.stemmer.stem_term(word)
                new_tokens.append(word)
            # ------------------------------------------------- chaning two or more upper words to one term
            if len(word) > 0 and word[0].isupper():
                # chunks entities together.
                temp_entitie += word + " "
                will_merge += 1
            else:
                # add entity to the global counter and to the current words set
                if temp_entitie != '':
                    n = temp_entitie[:-1]  # delete the space " " apter the capital term
                    entities_set.add(n)
                    if will_merge > 1:
                        new_capital_words.add(temp_entitie)
                    temp_entitie = ''
                    will_merge = 0

            if len(word) > 0 and word[0].isupper():
                if word not in capital_dict:
                    capital_dict[word.lower()] = True
            else:
                capital_dict[word.lower()] = False


        if len(url) > 0:
            list = []
            list.append(url)
            self.extractUrl(list, 0)
            new_tokens.extend(list)

        return new_tokens, capital_dict, entities_set

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        retweet_quoted_text = doc_as_list[11]

        if quote_text is not None:
            full_text = full_text + " " + quote_text
        if retweet_quoted_text is not None:
            full_text = full_text + " " + retweet_quoted_text
        #if retweet_text is not None:
        #    full_text = full_text + " " + retweet_text


        # clean latin letters
        full_text = re.sub(re.compile(pattern=r'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\u2019]'),
                           u'', full_text)
        term_dict = {}
        tokenized_text ,capital_dict,entities_set = self.parse_sentence(full_text)


        doc_length = len(tokenized_text)  # after text operations.


        max_tf = 0
        for idx, term in enumerate(tokenized_text):
            if term not in term_dict.keys():
                term_dict[term] = [idx]
            else:
                term_dict[term].append(idx)
                max_tf = max(len(term_dict[term]), max_tf)

        unique_terms_in_doc = len(term_dict)
        are_rt = 0
        if full_text.find("rt") == 0 or full_text.find("RT") == 0:
            are_rt = 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length,max_tf, unique_terms_in_doc, are_rt, capital_dict, entities_set)
        return document

