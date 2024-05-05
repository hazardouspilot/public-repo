import numpy as np
from itertools import chain
import nltk

def tokenizeData(text):
    """
        This function tokenizes a raw text string.
    """
    #change text to lower case
    text_lower = text.lower()

    #regex expression provided in assignment spec
    exp = r'''(?x)                                  #flag to allow verbose regexps
        (?:[A-Za-z]\.)+                             #abbreviations
      | \w*[\$£]?(?:\d+(?:,\d+)?)+(?:\.\d+)?%?\w*   #numbers, currency and percentages, e.g. $12.40, 82%
      | [A-Za-z]+(?:[-'][A-Za-z]*)?                 #words with internal hyphen/s and/or apostrophe/s
    '''

    #set tokenizer using regex expression
    tokenizer = nltk.RegexpTokenizer(exp)

    #apply tokenizer to text
    tokenised_text = tokenizer.tokenize(text_lower)

    #return tokenized text
    return tokenised_text

def stats_print(tokenised_text):
    """
    Function to print stats of a list of tokenized text
    """
    #obtain list of words
    words = list(chain.from_iterable(tokenised_text))
    #obtain covabulary
    vocab = set(words)
    #calc lexical diversity
    lexical_diversity = len(vocab)/len(words)                     
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Total number of tokens: {len(words)}")
    print(f"Lexical diversity: {lexical_diversity}")
    print(f"Total number of articles: {len(tokenised_text)}")
    #compile list of text lengths
    lens = [len(text) for text in tokenised_text]                 
    print(f"Average document length: {np.mean(lens)}")
    print(f"Maximum document length: {np.max(lens)}")
    print(f"Minimum document length: {np.min(lens)}")
    print(f"Standard deviation of document length: {np.std(lens)}")

def removeWords(text, list_words_to_remove):
    """
    Function to remove a list of words from a list of words
    """
    return [w for w in text if w not in list_words_to_remove]

def removeShortWords(text, n=1):
    """
    Function to remove words <= "n" length from list of words "text"
    """
    return [w for w in text if len(w) > n]