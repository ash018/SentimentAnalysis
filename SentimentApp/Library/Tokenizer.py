import nltk.data
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer


class Tokenizer:
    def sentence_tokenizer(self, text):
        return sent_tokenize(text)

    def sentence_tokenizer_efficient(self, text):
        tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
        result = tokenizer.tokenize(text)
        return result

    def word_tokenizer(self, text):
        return word_tokenize(text)

    def porter_stem(self, word):
        stemmer = PorterStemmer()
        result = stemmer.stem(word)
        return  result

    def snowball_stem(self, word):
        stemmer = SnowballStemmer('english')
        result = stemmer.stem(word)
        return result

