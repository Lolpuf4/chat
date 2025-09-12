class DataBaseError(Exception):
    pass

class DBMSErrors(Exception):
    pass


class UnknownCommandError(DBMSErrors):
    def __init__(self, command_name):
        self.message = f"Unknown command '{command_name}'."
        super().__init__(self.message)

class InvalidParenthesesError(DBMSErrors):
    def __init__(self):
        self.message = f"Invalid parentheses."
        super().__init__(self.message)

class NoDatabaseError(DBMSErrors):
    def __init__(self):
        self.message = f"Specify Database in SQL command."
        super().__init__(self.message)



class ForeignKeyError(DataBaseError):
    pass

class UnknownColumnInForeignKeyError(ForeignKeyError):
    def __init__(self, column_name):
        self.message = f"Unknown column '{column_name}' in foreign key."
        super().__init__(self.message)

class ReferenceError(ForeignKeyError):
    pass

class UnknownReferenceTableError(ReferenceError):
    def __init__(self, ReferenceTable):
        self.message = f"Unknown reference table '{ReferenceTable}'."
        super().__init__(self.message)

class UnknownReferenceColumnError(ReferenceError):
    def __init__(self, ReferenceColumn):
        self.message = f"Unknown reference table '{ReferenceColumn}'."
        super().__init__(self.message)




class ColumnIsNotInTableError(DataBaseError):
    def __init__(self, column_name, table_name):
        self.message = f"Column '{column_name}' is not in table '{table_name}.'"
        super().__init__(self.message)

class IncorrectDatatypeError(DataBaseError):
    def __init__(self, column_name, datatype_used, datatype_expected):
        self.message = f"Incorrect datatype used in column '{column_name}', expected {datatype_expected}, got {datatype_used}."
        super().__init__(self.message)

class NotEnoughColumnsError(DataBaseError):
    def __init__(self, name_of_table):
        self.message = f"Table '{name_of_table}' requires more columns."
        super().__init__(self.message)


class ServerError(Exception):
    pass