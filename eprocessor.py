import nltk
import tkinter as tk
from random import random
import string


class TasksCollections:

    def __init__(self):
        self._make_art_collection()
        self._make_nn_collection()
        self._make_pronouns_collection()
        self._make_times_collection()
        self.norm = "Norm"

    def _make_art_collection(self):
        self.art1 = "<Art1>"
        self.rule_art_collection = set([self.art1])

    def _make_nn_collection(self):
        self.nn_plural_special_vocabular = set(["men", "geese", "women",
                                                "children", "feet", "mice",
                                                "oxen", "Englishmen", "Frenchmen"])

        self.nn_plural_special_answers = {"men": "man", "geese": "goose", "women": "woman",
                                                "children": "child", "feet": "foot", "mice": "mouse",
                                                "oxen": "ox", "Englishmen": "Englishman", "Frenchmen": "Frenchman"}

        self.nn1 = "<NN1>" #для окончания множественного числа
        self.nn2 = "<NN2>" #для специальных форм множественного числа
        self.rule_nouns_collection = set([self.nn1, self.nn2])

    def _make_pronouns_collection(self):
        self.pron1 = "<PRON1>"
        self.pron1_vocab = ["some", "any", "no"]

        self.pron2 = "<PRON2>"
        self.pron2_vocab = [x + "thing" for x in self.pron1_vocab]

        self.pron3 = "<PRON3>"
        self.pron3_vocab = [x + "body" for x in self.pron1_vocab]

        self.pron4 = "<PRON4>"
        self.pron4_vocab = [x + "where" for x in self.pron1_vocab]

        self.pron5 = "<PRON5>"
        self.pron5_vocab = ["much", "many", "little", "few"]

        self.pron_option_vocab = {
            self.pron1 : self.pron1_vocab,
            self.pron2 : self.pron2_vocab,
            self.pron3 : self.pron3_vocab,
            self.pron4 : self.pron4_vocab,
            self.pron5 : self.pron5_vocab,
        }

        self.rule_pron_collection = set([self.pron1, self.pron2, self.pron3, self.pron4,
                                         self.pron5])
        self.pron_special_vocab = set(self.pron1_vocab + self.pron2_vocab +
                                      self.pron3_vocab + self.pron4_vocab +
                                      self.pron5_vocab)

    def _make_times_collection(self):
        self.times1 = "<TIME1>"
        self.times1_vocab = ["is", "am", "are"]

        self.times2 = "<TIME2>"
        self.times2_vocab = ["was", "were"]

        self.times3 = "<TIME3>"
        self.times3_vocab = ["shall", "will"]

        self.times4 = "<TIME4>"
        self.times4_vocab = ["do", "does", "did"]

        self.times5 = "<TIME5>"
        self.times5_vocab = ["have", "has", "had"]

        self.times_option_vocab = {
            self.times1: self.times1_vocab,
            self.times2: self.times2_vocab,
            self.times3: self.times3_vocab,
            self.times4: self.times4_vocab,
            self.times5: self.times5_vocab,
        }

        self.rule_times_collection = set([self.times1, self.times2, self.times3, self.times4,
                                         self.times5])
        self.times_special_vocab = set(self.times1_vocab + self.times2_vocab +
                                      self.times3_vocab + self.times4_vocab +
                                      self.times5_vocab)


class ArticleProcessor(TasksCollections):

    def __init__(self):
        self.look_for = ['a', 'the', 'at', 'an']

    def process_tagged_sent(self, tagged_sent):
        super().__init__()

        after_rule_one = self._rule_one(tagged_sent)
        after_rule_two = self._rule_two(after_rule_one)
        after_rule_three = self._rule_three(after_rule_two)
        after_rule_four = self._rule_four(after_rule_three)

        return after_rule_four

    def _rule_one(self, tagged_sent):
        answer = []
        for word in tagged_sent:
            if word[1] == 'DT' and (word[0] in self.look_for):
                answer.append((word[0], self.art1))
            elif word == ('``', '``'):
                answer.append(("''", "''"))
            else:
                answer.append(word)

        return answer

    def _rule_two(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)
        for i in range(tagged_sent_len):

            prew_word = None if i == 0 else tagged_sent[i - 1]
            word = tagged_sent[i]
            next_word = None if i == tagged_sent_len - 1 else tagged_sent[i + 1]

            if (word[1] in ['JJ', 'JJS'] and word[0] != '—') and next_word and (next_word[1] in ["NN", "NNP", "NNS", "NNPS"]):
                if prew_word and prew_word[1] != "DT" and (prew_word[1] not in self.rule_art_collection):
                    answer.append(("", self.art1))

            answer.append(word)

        return answer

    def _rule_three(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)
        for i in range(tagged_sent_len):

            prew_word = None if i == 0 else tagged_sent[i - 1]
            word = tagged_sent[i]

            if word[0] == "front" and prew_word and prew_word[0] == "in":
                answer.append(("", self.art1))
            answer.append(word)

        return answer

    def _rule_four(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)

        for i in range(tagged_sent_len):

            prew_word = None if i == 0 else tagged_sent[i - 1]
            word = tagged_sent[i]
            next_word = None if i == tagged_sent_len - 1 else tagged_sent[i + 1]

            if (word[1] in ["NNS", "NNPS"] or (word[1] in ["NN", "NNP"] and next_word and next_word[1] == '’')) \
                    and (not prew_word or (prew_word[1] not in ["JJ", "JJS"])):
                if prew_word and prew_word[1] != "DT" and (prew_word[1] not in self.rule_art_collection):
                    answer.append(("", self.art1))

            answer.append(word)

        return answer

class NounsProcessor(TasksCollections):

    def __init__(self):
        super().__init__()

    def process_tagged_sent(self, tagged_sent):

        after_rule_one = self._rule_one(tagged_sent)

        return after_rule_one


    def _rule_one(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)

        for i in range(tagged_sent_len):
            word = tagged_sent[i]

            if word[1] in ["NNS", "NNPS"]:
                if len(word[0]) > 2:
                    t_word = word[0]
                    if t_word[-2:] == "es":
                        answer.append([t_word, self.nn1, t_word[:-2]])
                    elif t_word[-1] == 's':
                        answer.append((t_word, self.nn1, t_word[:-1]))
                    elif t_word in self.nn_plural_special_answers.keys():
                        answer.append((t_word, self.nn2, self.nn_plural_special_answers[t_word]))
                    else:
                        answer.append(word)
            else:
                answer.append(word)

        return answer


class PronounsProcessor(TasksCollections):
    def __init__(self):
        super().__init__()

    def process_tagged_sent(self, tagged_sent):
        after_rule_one = self._rule_one(tagged_sent)

        return after_rule_one

    def _rule_one(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)

        for i in range(tagged_sent_len):
            word = tagged_sent[i]

            if word[0] in self.pron_special_vocab:

                if word[1] == "DT":
                    answer.append((word[0], self.pron1))
                elif word[0] in self.pron2_vocab:
                    answer.append((word[0], self.pron2))
                elif word[0] in self.pron3_vocab:
                    answer.append((word[0], self.pron3))
                elif word[0] in self.pron4_vocab:
                    answer.append((word[0], self.pron4))
                elif word[0] in self.pron5_vocab:
                    answer.append((word[0], self.pron5))
                else:
                    answer.append(word)
            else:
                answer.append(word)
        return answer


class TimesProcessor(TasksCollections):
    def __init__(self):
        super().__init__()

    def process_tagged_sent(self, tagged_sent):
        after_rule_one = self._rule_one(tagged_sent)

        return after_rule_one

    def _rule_one(self, tagged_sent):
        answer = []
        tagged_sent_len = len(tagged_sent)

        for i in range(tagged_sent_len):
            word = tagged_sent[i]

            if word[0] in self.times_special_vocab:

                if word[0] in self.times1_vocab:
                    answer.append((word[0], self.times1))
                elif word[0] in self.times2_vocab:
                    answer.append((word[0], self.times2))
                elif word[0] in self.times3_vocab:
                    answer.append((word[0], self.times3))
                elif word[0] in self.times4_vocab:
                    answer.append((word[0], self.times4))
                elif word[0] in self.times5_vocab:
                    answer.append((word[0], self.times5))
                else:
                    answer.append(word)
            else:
                answer.append(word)
        return answer

class EngProcessor(TasksCollections):

    def __init__(self):
        super().__init__()
        self._article_pocessor = ArticleProcessor()
        self._noun_processor = NounsProcessor()
        self._pron_processor = PronounsProcessor()
        self._times_processor = TimesProcessor()

    def process_text(self, text):
        sent_text = nltk.sent_tokenize(text)
        raw_answer = []

        for sent in sent_text:
            tagged = nltk.pos_tag(nltk.word_tokenize(sent))

            after_article_processor = self._article_pocessor.process_tagged_sent(tagged)
            after_noun_processor = self._noun_processor.process_tagged_sent(after_article_processor)
            after_pron_processor = self._pron_processor.process_tagged_sent(after_noun_processor)
            after_times_processor = self._times_processor.process_tagged_sent(after_pron_processor)

            raw_answer_part = after_times_processor
            raw_answer = raw_answer + raw_answer_part


        return raw_answer

    def make_blueprint(self, procesed_text, hard_level=1, tight_level=3):

        hard_level = int(hard_level)
        tight_level = int(tight_level)

        level_one = self.rule_art_collection.union(self.rule_nouns_collection)
        level_one = level_one.union(self.rule_pron_collection)
        level_two = level_one.union(self.rule_times_collection)

        levels = [level_one,
                  level_two,
                  level_two]
        tightnes = [0.25, 0.5, 1]
        blueprints = {"to_contester": "", "to_data_base": ""}

        for item in procesed_text:

            if item[1] != "Norm":
                if item[1] in levels[hard_level - 1] and random() <= tightnes[tight_level-1]:

                    task_look = item[1]

                    if item[0] == "":
                        blueprints["to_data_base"] += "ничего"

                    if task_look in self.rule_nouns_collection:
                        task_look += " " + item[2]


                    blueprints["to_contester"] += task_look + " "
                else:
                    blueprints["to_contester"] += item[0] + (" " if item[0] != "" else "")
            else:
                blueprints["to_contester"] += item[0] + " "

            blueprints["to_data_base"] += item[0] + " "

        return blueprints


class BlueprintConverter(TasksCollections):

    def __init__(self):
        self.all_elements = []
        self.width_limit = 600
        super().__init__()

    def make_test(self, root, blueprint):
        self.all_elements = []
        words = blueprint.split('\n')
        frame = tk.Frame(root)
        frame.pack(anchor="w")

        self._make_simple_label(root, frame, words[0])
        words = words[1].split()
        frame = tk.Frame(root)
        frame.pack(anchor="w")

        l = len(words)

        need_continue = False

        for i in range(l):
            if need_continue:
                need_continue = False
                continue

            word = words[i]

            if word in self.rule_art_collection:
                OptionList = ['a', 'the', 'at', 'an', "ничего"]
                frame = self._make_option_menu(root, frame, OptionList)
            elif word in self.rule_nouns_collection:
                if word == self.nn1:
                    OptionList = [words[i+1] + 's', words[i+1] + "es"]
                    frame = self._make_option_menu(root, frame, OptionList)
                    need_continue = True
                else:
                    frame = self._make_entry(root, frame, "введите во мн. ч. " + words[i+1], words[i+1])
                    need_continue = True
            elif word in self.rule_pron_collection:
                OptionList = self.pron_option_vocab[word]
                frame = self._make_option_menu(root, frame, OptionList)
            elif word in self.rule_times_collection:
                OptionList = self.times_option_vocab[word]
                frame = self._make_option_menu(root, frame, OptionList)
            else:
                if i + 1 < l and words[i + 1] in string.punctuation + '’':
                    word += words[i + 1]

                    if words[i + 1] == '’':
                        word += words[i + 2]
                        words[i + 2] = ""

                    words[i + 1] = ""
                frame = self._make_simple_label(root, frame, word)



        return self.all_elements

    def _make_option_menu(self, root, frame, options):

        OptionList = options

        variable = tk.StringVar(frame)
        variable.set(OptionList[0])

        self.all_elements.append(variable)

        opt = tk.OptionMenu(frame, variable, *OptionList)
        opt.config(font=('Helvetica', 12))
        opt.pack(side="left", anchor='w', fill=tk.X)

        root.update_idletasks()
        new_width = frame.winfo_width()

        if new_width > self.width_limit:
            opt.destroy()
            frame = tk.Frame(root)
            frame.pack(anchor="w")
            opt = tk.OptionMenu(frame, variable, *OptionList)
            opt.config(font=('Helvetica', 12))
            opt.pack(side="left", anchor='w', fill=tk.X)
            frame.update_idletasks()

        return frame

    def entry_event_handler(self, entry, def_text=None, word=None):
        if entry.get() == "":
            entry.insert(0, def_text)
        else:
            if def_text == entry.get():
                entry.delete(0, tk.END)

    def _make_entry(self, root, frame, def_text=None, word=None):



        noun_entry = tk.Entry(frame, width = 25)
        noun_entry.insert(0, def_text)
        noun_entry.bind("<Button-1>", lambda event: self.entry_event_handler(noun_entry, def_text, word))
        noun_entry.pack(side="left", anchor='w', fill=tk.X)

        root.update_idletasks()
        new_width = frame.winfo_width()

        if new_width > self.width_limit:
            noun_entry.destroy()
            frame = tk.Frame(root)
            frame.pack(anchor="w")

            noun_entry = tk.Entry(frame)
            noun_entry.insert(0, def_text)
            noun_entry.bind("<Button-1>", lambda event: self.entry_event_handler(noun_entry, word))
            noun_entry.pack(side="left", anchor='w', fill=tk.X)

            frame.update_idletasks()

        self.all_elements.append(noun_entry)
        return frame


    def _make_simple_label(self, root, frame, word):

        if word == "":
            return frame

        label_text = (" " + word) if word not in string.punctuation else word
        normal_label = tk.Label(frame, text=label_text, font="Arial 12")
        normal_label.pack(side="left", anchor='w', fill=tk.X, pady=2)
        new_width = frame.winfo_width()
        frame.update_idletasks()

        if new_width > self.width_limit:
            normal_label.destroy()
            frame = tk.Frame(root)
            frame.pack(anchor="w")
            label_text = (" " + word) if word not in string.punctuation else word
            normal_label = tk.Label(frame, text=label_text, font="Arial 12")
            normal_label.pack(side="left", anchor='w', fill=tk.X, pady=2)
            frame.update_idletasks()

        self.all_elements.append(normal_label)
        return frame

    def clear_elements(self):
        self.all_elements = []