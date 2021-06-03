import re
import pandas as pd
import numpy as np
import cmudict
from sklearn.feature_extraction import DictVectorizer

def read_sonnet_file(filename, author, sonnets_list, curr_sonnet_idx):
    """Opens a txt file of all sonnets, reads it, adds them to a list of sonnets
    and returns the updated list and an index at which to start adding to the list

    filename: str
        string of filename
    author: str
        The author of all the sonnets in the file
    sonnet_list: list
        Each element of the list is the text of one sonnet
    curr_sonnet_idx: int
        index where function will start adding to the list
    Notes:
    -----
    Uses the formatting of the txt files, where before each sonnet is an empty line,
    the sonnet number, and another emtpy line. The file ends with 4 empty lines
    """
    f = open(filename, "r")
    lines = f.readlines() 
    f.close()
    
    line_idx = 0
    while line_idx < len(lines) - 3:
        line = lines[line_idx]
        if line == "\n": # new sonnet detected based on format
            sonnets_list.append({"text":"", "author": author, "sonnet_id": curr_sonnet_idx})
            line_idx += 3
            line = lines[line_idx]
            while line != "\n" and line_idx < len(lines):
                sonnets_list[curr_sonnet_idx]["text"] += line
                line_idx += 1
                line = lines[line_idx]
        curr_sonnet_idx += 1
    
    return sonnets_list, curr_sonnet_idx


def preprocess_sonnet(sonnet):
    """Preprocessing sonnet to remove capitalization, punctuation, whitespace
    and replace some contractions or uncommon words"""

    sonnet = sonnet.lower()
    
    #make apostrohes the same
    sonnet = sonnet.replace("’", "'")
    
    sonnet.replace("th'","the")
    
    for punctuation in [",", "?", "!", ":", ";", "."]:
        sonnet = sonnet.replace(punctuation, "")
    
    #replace -- and - with a space
    sonnet = sonnet.replace("--", " ")
    sonnet = sonnet.replace("-", " ")
        
    #only replace apostrophes at the beginning and end of words
    sonnet = sonnet.replace("' ", " ")
    sonnet = sonnet.replace("'\n", "\n")
    sonnet = sonnet.replace(" '", " ")
    
    #replace 'd with ed and th' with the
    sonnet = sonnet.replace("'d", "ed")
    sonnet = sonnet.replace("th'", "the ")

    # replace whitespace with single spaces
    sonnet = sonnet.replace("\t", " ")
    sonnet = sonnet.replace("\n", " ")
    sonnet = re.sub(" +", " ", sonnet)
    
    #replace the words not in cmu dictionary that have at least 10 occurances
    #[("beauty's", 34), ("heav'nly", 16), ('mayst', 13), ('didst', 12), ('nought', 11), ("heav'n", 11), ("o'er", 10), ('whereof', 10), ('beauteous', 9), ('canst', 9), ("stol'n", 9), ("virtue's", 9), ('vouchsafe', 8), ('sprites', 8), ("cupid's", 8)]
    sonnet = sonnet.replace("beauty's", "beauties")
    sonnet = sonnet.replace("heav'nly", "heavenly")
    sonnet = sonnet.replace("heav'n", "heaven")
    sonnet = sonnet.replace("whereof", "where of")
    sonnet = sonnet.replace("nought", "naught")
    sonnet = sonnet.replace("mayst", "may est")
    sonnet = sonnet.replace("didst", "did est")
    sonnet = sonnet.replace("o'er", "or")
    
    #sonnet = sonnet.replace("'s",  "s")
    
    return sonnet


def get_sonnet_phoneme_dict(processed_sonnet, cmu_dictionary, all_phonemes, with_lexical_stress=True, verbose=False):
    """sonnet_phoneme_dict:
        keys are phonemes, values are counts
    """
    sonnet_phoneme_dict = {phoneme: 0 for phoneme in all_phonemes}
    words = processed_sonnet.split()
    words_not_in_dict = []
    for word in words:
        if word in cmu_dictionary.keys():
            phonemes_for_word = cmu_dictionary[word][0]
            if not with_lexical_stress:
                phonemes_for_word = [re.sub(r'[0-9]+', '', p) for p in phonemes_for_word]
            for phoneme in phonemes_for_word:
                sonnet_phoneme_dict[phoneme] += 1
        else:
            words_not_in_dict.append(word)
            if verbose:
                print(word, " not in dict!")
    return(sonnet_phoneme_dict, words_not_in_dict)


def get_cmu_simvecs_embedding():
    embedding = dict()
    for line in open("cmudict-0.7b-simvecs.txt", encoding="latin1"):
        word, vals_raw = line.split("  ")
        word = word.lower().strip("(012)")
        vals = np.array([float(x) for x in vals_raw.split(" ")])
        embedding[word.lower()] = vals #50-dim vector
    return embedding

    
def sonnet_to_mean_word_vector(preprocessed_sonnet, embedding):
    """Calculate the mean of the embedded word vectors for a given sonnet"""
    words = preprocessed_sonnet.split()
    words_not_in_dict = [w for w in words if w not in embedding.keys()]
    words = [w for w in words if w in embedding.keys()] # filter to only include words in the dict
    return np.array([embedding[w] for w in words]).mean(axis=0), words_not_in_dict

    
def create_cmu_mean_simvecs_embedding_df(preprocessed_sonnets_list):
    embedding = get_cmu_simvecs_embedding()

    cmu_embeddings2 = []
    all_words_not_in_dict= []
    for preprocessed_sonnet in preprocessed_sonnets_list:
        embedded_sonnet, words_not_in_dict = sonnet_to_mean_word_vector(preprocessed_sonnet, embedding)
        cmu_embeddings2.append(embedded_sonnet)
        all_words_not_in_dict.extend(words_not_in_dict)
   
    cmu_embeddings_as_mtx = np.array(cmu_embeddings2)
    df_embeddings = pd.DataFrame(cmu_embeddings_as_mtx)

    return(df_embeddings, cmu_embeddings_as_mtx, all_words_not_in_dict)
    

def create_phoneme_embedding_df(preprocessed_sonnets_list, with_lexical_stress):

    cmu_dictionary = cmudict.dict() # Compatible with NLTK

    all_phonemes = []
    for phoneme_lists in cmu_dictionary.values():
        all_phonemes.extend(phoneme_lists[0])
    if not with_lexical_stress:
        all_phonemes = [re.sub(r'[0-9]+', '', p) for p in all_phonemes]
    all_phonemes=set(all_phonemes)

    all_sonnets_phoneme_dicts = []
    all_words_not_in_dict = []

    for processed_sonnet in preprocessed_sonnets_list:
        sonnet_phoneme_dict, words_not_in_dict = get_sonnet_phoneme_dict(processed_sonnet, cmu_dictionary, all_phonemes, with_lexical_stress=with_lexical_stress, verbose=False)
        all_sonnets_phoneme_dicts.append(sonnet_phoneme_dict)
        all_words_not_in_dict.extend(words_not_in_dict)

    vectorizer = DictVectorizer(sparse=False)
    phoneme_count_mtx = vectorizer.fit_transform(all_sonnets_phoneme_dicts)

    # calculate TF-IDF for phoneme counts
    normalized_phoneme_count_mtx = phoneme_count_mtx / phoneme_count_mtx.sum(axis=0)

    # drop those where all elts are na (i.e. no counts were observed for that phoneme)
    phoneme_names = np.array(list(sonnet_phoneme_dict.keys()))
    phoneme_names_trimmed = phoneme_names[~np.all(np.isnan(normalized_phoneme_count_mtx), axis=0)]
    normalized_phoneme_count_mtx = normalized_phoneme_count_mtx[:,~np.all(np.isnan(normalized_phoneme_count_mtx), axis=0)]

    df_counts = pd.DataFrame(normalized_phoneme_count_mtx, columns = phoneme_names_trimmed)
    
    return df_counts, normalized_phoneme_count_mtx, all_words_not_in_dict