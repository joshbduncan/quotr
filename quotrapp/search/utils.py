import re
import string
import Stemmer


STEMMER = Stemmer.Stemmer('english')
PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))
# top 25 most common words in English and "wikipedia":
# https://en.wikipedia.org/wiki/Most_common_words_in_English
STOPWORDS = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'wikipedia',
                 'then', 'i', 'an', 'or', 'it\'', 'their', 'what', 'if'])  # this line added by me


def tokenize(text):
    return text.split()


def lowercase_filter(tokens):
    return [token.lower() for token in tokens]


def stem_filter(tokens):
    return STEMMER.stemWords(tokens)


def punctuation_filter(tokens):
    return [PUNCTUATION.sub('', token) for token in tokens]


def stopword_filter(tokens):
    return [token for token in tokens if token not in STOPWORDS]


def analyze(text):
    tokens = tokenize(text)
    tokens = lowercase_filter(tokens)
    tokens = punctuation_filter(tokens)
    tokens = stopword_filter(tokens)
    tokens = stem_filter(tokens)

    return [token for token in tokens if token]


class Search:
    def __init__(self):
        self.index = {}

    # must pass in list of quote objects so on
    # add new quote put that singular quote object in a list
    def index_tokens(self, quotes: list):
        self.quotes = quotes
        for quote in self.quotes:
            tokens = analyze(quote.content)
            # add author name to tokens
            tokens.extend(analyze(quote.author.name))
            for token in tokens:
                if token not in self.index:
                    self.index[token] = set()
                self.index[token].add(quote.id)

    def remove_deleted_quote_tokens(self, quote):
        self.quote = quote
        tokens = analyze(self.quote.content)
        # add author name to tokens
        tokens.extend(analyze(quote.author.name))
        # remove tokens from index
        for token in tokens:
            if token in self.index:
                # if token only has one quote ref then delete it
                if token in self.index and len(self.index[token]) == 1:
                    del self.index[token]
                else:
                    # if token has multiple quote refs then just delete ref
                    self.index[token].remove(self.quote.id)

    def _results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]

    def search(self, query, search_type='OR'):

        if search_type not in ('AND', 'OR'):
            return []

        analyzed_query = analyze(query)
        matches = self._results(analyzed_query)

        if search_type == 'AND':
            # all tokens must be in the document
            results = set.intersection(*matches)

        if search_type == 'OR':
            results = set.union(*matches)

        return results
