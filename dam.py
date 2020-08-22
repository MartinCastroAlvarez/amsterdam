import os
import typing

import spacy
import slugify
import numpy as np
import wikipedia

# SPACY
# @ref: https://spacy.io/usage/models
# @usage: python3 -m spacy download en_core_web_sm
english = spacy.load('en_core_web_sm')

# WIKIPEDIA
# @ref: https://pypi.org/project/wikipedia/
wikipedia.set_lang("fr")


def get_document(term: str) -> str:
    """
    GET DOC FROM WIKIPEDIA AS TEXT
    @ref: https://pypi.org/project/wikipedia/
    """
    assert isinstance(term, str) and term, term
    cache_key: str = os.path.join(os.sep, 'tmp', slugify.slugify(term))
    if os.path.isfile(cache_key):
        with open(cache_key, 'r') as file_handler:
            return file_handler.read()
    documents: list = wikipedia.search(term)
    for page_id in documents:
        text: str = wikipedia.page(page_id).content\
            .replace("\n", " ")\
            .replace("=", " ")
        text = ' '.join(text.split())
        with open(cache_key, 'w') as file_handler:
            file_handler.write(text)
        return text
    raise RuntimeError('Not Found:', term)


def get_tokens(text: str) -> str:
    """
    TOKENIZER
    @ref: https://stackoverflow.com/questions/38763007
    """
    assert isinstance(text, str) and text, text
    return [
        token.lemma_.lower()
        for token in english(text)
        if not token.is_stop
        and not token.is_punct
    ]


def get_index(tokens: list) -> str:
    """
    WORD INDEX
    """
    assert tokens and isinstance(tokens, list), tokens
    word2id: dict = {}
    id2word: dict = {}
    corpus: list = []
    token_id: int = 0
    for token in sorted(tokens):
        if token not in word2id:
            word2id[token] = token_id
            id2word[token_id] = token
            token_id += 1
    return word2id, id2word


def get_vocab_size(word2id: dict) -> int:
    """
    VOCAB SIZE COUNTER
    """
    assert isinstance(word2id, dict) and word2id, word2id
    return len(word2id)


def get_corpus_size(tokens: list) -> int:
    """
    CORPUS SIZE COUNTER
    """
    assert isinstance(tokens, list) and tokens, tokens
    return len(tokens)


def get_one_hot(tokens: list, word2id: dict) -> np.array:
    """
    ONE HOT ENCODING
    """
    assert tokens and isinstance(tokens, list), tokens
    assert word2id and isinstance(word2id, dict), word2id
    one_hot_vector: np.array = np.zeros(len(word2id))
    for token in tokens:
        assert token in word2id, token
        token_id: int = word2id[token]
        one_hot_vector[token_id] = 1
    return one_hot_vector


def generate_training_data(corpus,window_size,vocab_size,word_to_index,length_of_corpus,sample=None):
    training_data =  []
    training_sample_words =  []
    for i,word in enumerate(corpus):
        index_target_word = i
        target_word = word
        context_words = []
        #when target word is the first word
        if i == 0:
            # trgt_word_index:(0), ctxt_word_index:(1,2)
            context_words = [corpus[x] for x in range(i + 1 , window_size + 1)]
        #when target word is the last word
        elif i == len(corpus)-1:
            # trgt_word_index:(9), ctxt_word_index:(8,7), length_of_corpus = 10
            context_words = [corpus[x] for x in range(length_of_corpus - 2 ,length_of_corpus -2 - window_size  , -1 )]
        #When target word is the middle word
        else:
            #Before the middle target word
            before_target_word_index = index_target_word - 1
            for x in range(before_target_word_index, before_target_word_index - window_size , -1):
                if x >=0:
                    context_words.extend([corpus[x]])
            #After the middle target word
            after_target_word_index = index_target_word + 1
            for x in range(after_target_word_index, after_target_word_index + window_size):
                if x < len(corpus):
                    context_words.extend([corpus[x]])
        trgt_word_vector,ctxt_word_vector = get_one_hot_vectors(target_word,context_words,vocab_size,word_to_index)
        training_data.append([trgt_word_vector,ctxt_word_vector])
        if sample is not None:
            training_sample_words.append([target_word,context_words])
    return training_data,training_sample_words


document: str = get_document('Dragon Ball')
tokens: list = get_tokens(document)
word2id, id2word = get_index(tokens)
vocab_size: int = get_vocab_size(word2id)
corpus_size: int = get_corpus_size(tokens)
print("TOKENS", "\n", str(tokens)[:100])
print("WORD2ID", "\n", str(word2id)[:100])
print("ID2WORD", "\n", str(id2word)[:100])
print("VOCAB", vocab_size)
print("CORPUS", corpus_size)
assert np.sum(get_one_hot(['goku', 'vegeta'], word2id)) == 2
x = generate_training_data(corpus_size,3,vocab_size,word2id,corpus_size,sample=10):
print(x)
import sys; sys.exit(1)

text: str = "Best way to success is through hard work and persistence"
