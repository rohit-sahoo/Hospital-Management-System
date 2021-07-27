class Config:

    def __init__(self):
        # Will change to OS Environment Variable
        self.__secret_key = '3addd1d0e167f86cba86bd2c'

    @property
    def secret_key(self):
        return self.__secret_key
