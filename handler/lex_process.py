import json

import pronouncing


class prons_generator():
    # lexicon is a dict(key:[prons1, prons2, ... ]) struct
    def __init__(self, lexicon):
        self.d = lexicon
        self.phone_table = self.load_phone_table()
        #self.d = {key: lexicon[key][0] for key in lexicon}
        '''with open('lexicon.txt', 'r',encoding='utf-8') as f:
            self.l = [i.split() for i in f.readlines()]
            self.d = {i[0]: i[1:] for i in self.l}
            print(self.d)'''


    def 漢語拼音(self, s):
        '''l = [self.d.get(c, []) for c in s]
        f = lambda i: ''.join(i).strip() != ''
        return ' '.join(' '.join(i) for i in filter(f, l))'''

        # Get character's prons in input word
        l = []
        for c in s:
            phone = self.d.get(c, [])
            if phone:
                l.append(phone[0])
            else:
                return []

        return ' '.join(l)

    def english_pinyin(self, word):
        ''' Generate english word pinyin for lexicon.txt '''

        # Generate CMU dict's phone
        cmu_phones = pronouncing.phones_for_word(word)
        if not cmu_phones:
            return []

        # Transform
        xsampa_phones = self.cmu_to_xsampa(cmu_phones[0])

        return xsampa_phones


    def cmu_to_xsampa(self, cmu_phones):
        ''' Transform CMU dict's phone to X-SAMPA(with a little customize) phone '''

        xsampa_phones = []
        for cmu_phone in cmu_phones.split():
            xsampa_phone = self.phone_table[cmu_phone]
            xsampa_phones.append(xsampa_phone)
        return ' '.join(xsampa_phones)


    def load_phone_table(self):
        ''' Load phone table for transform '''

        dict_table = {}
        with open('phone_table.json', 'r', encoding='utf-8') as js:
            dict_table = json.load(js)
        return dict_table


class KaldiLexiconHandler():
    def __init__(self, LEX_PATH):
        self.lexicon = self.load_lexicon(LEX_PATH)
        self.generator = self.build_prons_generator()


    def load_lexicon(self, LEX_PATH):
        ''' Load lexicon.txt to lexicon(dict) '''
        lexicon = {}
        with open(LEX_PATH, 'r', encoding='utf-8') as lex:
            for line in lex:
                word, prons = line.replace('\n', '').split(' ', 1)
                if word not in lexicon:
                    lexicon[word] = [prons]
                else:
                    lexicon[word].append(prons)
        return lexicon


    def write_lexicon(self, w_lexicon, word, prons):
        ''' Write new word and prons to lexicon.txt '''
        with open(w_lexicon, 'a', encoding='utf-8') as lex:
            lex.write('{} {}\n'.format(word, prons))


    def add_lexicon(self, word, prons):
        ''' Add word to lexicon  '''
        if not self.isexisted(word):
            self.lexicon[word] = [prons]
        else:
            self.lexicon[word].append(prons)


    def isexisted(self, word):
        ''' Check word is existed or not'''
        if word in self.lexicon:
            return True
        else:
            return False


    def build_prons_generator(self):
        ''' Build prons generator '''
        generator = prons_generator(self.lexicon)
        return generator


    def generate_prons(self, word, lang):
        ''' Generate pinyin '''
        if lang == 'zh':
            prons = self.generator.漢語拼音(word)
        elif lang == 'en':
            prons = self.generator.english_pinyin(word)
        return prons
