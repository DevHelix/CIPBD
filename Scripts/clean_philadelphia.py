import pandas as pd

class Cleaner:
    def __init__(self, end_word, file_path):
        self.end_word = end_word
        self.file_path = file_path
    
    def remove_num(self, string):
        end_index = string.find(self.end_word)

        no_digits = []
        in_number = False

        for i in range(end_index):
            if string[i].isdigit():
                in_number = True                        # start skipping
            elif string[i].isalpha() and in_number:
                pass                                    # letter attached to number — skip
            elif string[i] == ' ' and in_number:
                in_number = False          # reset but don't append the space
            else:
                in_number = False                       # hit a space/punct — reset
                no_digits.append(string[i])

        result = ''.join(no_digits) + string[end_index:]
        return result

    def conversion(self, column_name):
        df = pd.read_csv(self.file_path)
        df[column_name] = df[column_name].map(self.remove_num)

c = Cleaner("item","C:/Users/vince/Document/GitHub/CIPBD/Philadelphia/CSV/2024.csv")
c.conversion("project_description")