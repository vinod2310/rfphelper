from nltk.corpus import wordnet

def get_synonyms(word):
    return wordnet.synsets("word")
