import pandas as pd

class Cleaner:

    folder_path="C:\\Users\\vince\\Documents\\GitHub\\CIPBD\\Philadelphia\\CSV\\"
    bad_desc = []

    def __init__(self, end_word):
        self.end_word = end_word
    
    def remove_num(self, string):
        if not isinstance(string, str):
            return string
        
        print("Before: " + string)
        end_index = string.find(self.end_word)
        if end_index == -1:
            end_index = len(string)

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
        print("After: " + result)
        return result

    def conversion(self, file_path, column_name):
        df = pd.read_csv(file_path)
        df[column_name] = df[column_name].map(self.remove_num)
        df.to_csv(file_path, index=False)

    def combine(self): #combines conversion + remove_num
        for i in range(2019,2025):
            print(i)
            self.conversion(self.folder_path+str(i)+".csv","project_description")

    def runFind_bd(self, target):
        results = {}
        for i in range(2019,2025):
            df = pd.read_csv(self.folder_path+str(i)+".csv")
            for _, row in df.iterrows():
                desc = row.get('project_description', '')
                if isinstance(desc, str) and target in desc:
                    results[row['project_id']] = {
                    'cip_year': row.get('cip_year', str(i)),
                    'description': desc
                }
                 
        return results
    
           
c = Cleaner("item")
#c.remove_num("This includes the Airport arrival and departure 1,000 program roadways, and areas on which a hotel, parking facilities, and car 62,950 rental entities operate.")
#c.s()
print(c.runFind_bd("D."))
