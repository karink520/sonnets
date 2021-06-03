import re


def read_sonnet_file(filename, author, sonnets_list, curr_sonnet_idx):
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