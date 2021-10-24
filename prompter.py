class Prompter:
    def __init__(self):
        self.ls_yes = ['y', 'ye', 'yes']
        self.__default_msg()
    
    def __default_msg(self):
        self.msg_generic = "Are you sure?"
        self.msg_menu = "Please select an integer"
        self.msg_input = "Please enter your input"

    def prompt_confirmation(self, msg=None):
        """
        Input: msg
        Return: True or False
        """
        msg = self.msg_generic if (msg is None) else msg #if none, generic; else msg
        return True if (input(msg + " (y/n) >> ").lower() in self.ls_yes) else False
    
    def prompt_menu(self, msg:str=None, ls:list=[]):
        """
        Input: msg, ls
        Return: item from list
        """ 
        msg = self.msg_menu if (msg is None) else msg 
        while True:
            try: # try 1) Print menu 2) get user input
                for i,j in enumerate(ls):
                    print(i, '|', j)
                user_input = input(msg + " >> ")
                user_input = int(user_input)
            except ValueError: # if usr enters error, ie, not an integer
                if (type(user_input) == str) and ('exit' in user_input.lower()):
                    break # if 'exit' then break
                print('Please enter an int. Try again.')
                continue
            if user_input in range(len(ls)): # if appropriate response
                return ls[user_input]
            else: # else int not in range
                print("Value is not in range. Try again.")

    def prompt_input(self, msg=None):
        msg = self.msg_menu if (msg is None) else msg 
        """
        Input: raw string text
        Return: clean text
        """
        while True:
            try:
                user_input = input(msg + " >> ")
            except ValueError:
                print('Error.')
                break
            if type(user_input) is str:
                return user_input