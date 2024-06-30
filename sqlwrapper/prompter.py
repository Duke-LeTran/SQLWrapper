from src.errors import YesNoParseError

class Prompter:
    def __init__(self):
        self.ls_yes = ['y', 'ye', 'yes']
        self.ls_no = ['n', 'no']
        self.__default_msg()
    
    def __default_msg(self):
        self.msg_generic = "Are you sure?"
        self.msg_menu = "Please select an integer"
        self.msg_input = "Please enter your input"
    
    def prompt_confirmation(self, msg:str=None, answer:str=None):
        """
        Input: msg
        Return: True or False
        """
        # if answer is provided
        if (answer is not None):
            if answer.lower() in self.ls_yes:
                return True
            elif answer.lower() in self.ls_no:
                return False
            else:
                raise YesNoParseError
        
        else:
            msg = self.msg_generic if (msg is None) else msg #if none, generic; else msg
            if (input(msg + " (y/n) >> ").lower() in self.ls_yes):
                return True
            elif (input(msg + " (y/n) >> ").lower() in self.ls_no):
                return False
            else:
                raise YesNoParseError
    
    def prompt_menu(self, msg:str=None, ls:list=[], sep='|'):
        """
        Input: msg, ls
        Return: item from list
        """ 
        # set message or use default
        msg = self.msg_menu if (msg is None) else msg 
        # if no list of menu passed, return hints
        if len(ls) == 0:
            print('You must pass a list for the menu using the parameter"ls=[]".')
            return False
        while True:
            try: # try 1) Print menu 2) get user input
                for i,j in enumerate(ls):
                    print(i, sep, j)
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
                print("Value is not in range. Try again. Type 'exit' to exit menu.")

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