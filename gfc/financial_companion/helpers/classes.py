import tabula
import pandas as pd
import re
import dateutil.parser as dparser
from typing import Any

class ParseStatementPDF:
    def __init__(self):
        self.number_regex: str = r'[^-\d.]'
        self.reset_object()
    
    def reset_object(self):
        """Sets all transaction data to none"""
        self.date = None
        self.reset_data()
    
    def reset_data(self):
        """Sets all transaction data except date to none"""
        self.amount = None
        self.transaction_type = None
        self.description = None
        self.balance = None
    
    def get_pdf_statement_column_expense_indexes(self, statement_dataframe_list: list[pd.DataFrame]) -> tuple[int, int, bool]:
        """Checks if income and expense fields are separate or together"""
        if pd.isna(statement_dataframe_list[0].iloc[0][-3]) or re.sub(self.number_regex, '', statement_dataframe_list[0].iloc[0][-3])[1:].replace(".","", 1).replace("-","", 1).isnumeric():
            return -3, -2, False
        if re.sub(self.number_regex, '', statement_dataframe_list[0].iloc[0][-2])[1:].replace(".","", 1).replace("-","", 1).isnumeric():
            return -2, -2, False

        return -1, -1, True
    
    def get_transactions_from_dataframe_list(self, statement_dataframe_list: list[pd.DataFrame], indexes: dict[str, int], transactions: list[dict[str, Any]] = []) -> list[dict[str, Any]]:
        """Returns list of transaction data from list of dataframes"""
        for statement_dataframe in statement_dataframe_list:
            transactions = self.get_transactions_from_dataframe(statement_dataframe, transactions, indexes)
        return transactions

    def set_expense_and_income_columns_correct_way_around(self, transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Checks the expense and income columns are the correct way around in the data
        Set the expense and income columns in the data if incorrect
        """

        if len(transactions) > 1:
            if not ((transactions[1]["balance"] - transactions[0]["balance"] > 0 and transactions[1]["transaction_type"] == "income") or (transactions[1]["balance"] - transactions[0]["balance"] < 0 and transactions[1]["transaction_type"] == "expense")):
                for transaction in transactions:
                    if transaction["transaction_type"] == "income":
                        transaction["transaction_type"] = "expense"
                    elif transaction["transaction_type"] == "expense":
                        transaction["transaction_type"] = "income"
        
        return transactions
    
    def set_initial_balance_from_dataframe(self, statement_dataframe: pd.DataFrame, indexes: dict[str, int]):
        """
        Sets object balance data if statement dataframe balance block is not empty 
        or balance is already set
        """
        if self.balance is None and len(statement_dataframe.columns[indexes["balance"]]) > 0:
            try:
                self.balance = float(re.sub(self.number_regex, '', str(statement_dataframe.columns[indexes["balance"]])))
            except Exception:
                pass
  
    def set_date_from_datataframe_row(self, statement_dataframe_row: list[Any], indexes: dict[str, int]):
        """Updates object date data if statement dataframe row date block is understandable"""
        try:
            self.date = pd.to_datetime(dparser.parse(str(statement_dataframe_row[indexes["date"]]), fuzzy=True), infer_datetime_format=True)
        except Exception:
            pass
    
    def set_balance_from_datataframe_row(self, statement_dataframe_row: list[Any], indexes: dict[str, int]):
        """Updates object balance data if statement dataframe row balance block is not empty"""
        if not pd.isna(statement_dataframe_row[indexes["balance"]]):
                self.balance = float(re.sub(self.number_regex, '', str(statement_dataframe_row[indexes["balance"]])))

    def set_amount_and_transaction_type_from_datataframe_row(self, statement_dataframe_row: list[Any], indexes: dict[str, int]):
        """Updates amount and transaction type data if statement dataframe row income or expense block is valid"""
        if not pd.isna(statement_dataframe_row[indexes["income"]]) and float(re.sub(self.number_regex, '', str(statement_dataframe_row[indexes["income"]]))) >= 0:
                self.amount = abs(float(re.sub(self.number_regex, '', str(statement_dataframe_row[indexes["income"]]))))
                self.transaction_type = "income"
        elif not pd.isna(statement_dataframe_row[indexes["expense"]]):
            self.amount = abs(float(re.sub(self.number_regex, '', str(statement_dataframe_row[indexes["expense"]]))))
            self.transaction_type = "expense"
    
    def set_description_from_datataframe_row(self, statement_dataframe_row: list[Any], indexes: dict[str, int]):
        """Updates object description data if statement dataframe row descritiption block is not empty"""
        if not pd.isna(statement_dataframe_row[indexes["description"]]):
            if self.description is None:
                self.description = [str(statement_dataframe_row[indexes["description"]])]
            else:
                self.description += [statement_dataframe_row[indexes["description"]]]
    
    def set_all_data_from_dataframe_row(self, statement_dataframe_row: list[Any], indexes: dict[str, int]):
        """Parses dataframe row and updates object data where rows aren't empty"""
        self.set_date_from_datataframe_row(statement_dataframe_row, indexes)
        self.set_balance_from_datataframe_row(statement_dataframe_row, indexes)
        self.set_amount_and_transaction_type_from_datataframe_row(statement_dataframe_row, indexes)
        self.set_description_from_datataframe_row(statement_dataframe_row, indexes)
    
    def add_new_transaction(self, transactions, new_transaction: dict[str, Any]) -> list[dict[str, Any]]:
        """Returns transactions list, adding new transaction if valid"""
        if not all(new_transaction.values()):
            return transactions
        
        # TODO: Allow user to choose which description row for account and description, or autoparse it for them
        self.reset_data()
        return [*transactions, new_transaction]
    
    def get_transactions_from_dataframe(self, statement_dataframe: pd.DataFrame, transactions: list[dict[str, Any]], indexes: dict[str, int]) -> list[dict[str, Any]]:
        """Returns list of transaction data from dataframe"""
        statement_dataframe.dropna(
            how='all', axis=1, inplace=True
        )
        self.set_initial_balance_from_dataframe(statement_dataframe, indexes)

        for statement_dataframe_row in statement_dataframe.iloc():
            self.set_all_data_from_dataframe_row(statement_dataframe_row, indexes)
            
            new_transaction = {
                "date": self.date,
                "amount": self.amount,
                "balance": self.balance,
                "transaction_type": self.transaction_type,
                "description": self.description
            }  
            
            transactions = self.add_new_transaction(transactions, new_transaction)

        return self.set_expense_and_income_columns_correct_way_around(transactions)
    
    def get_transactions_from_pdf_statement(self, statement_name: str) -> list[dict[str, Any]]:
        """Returns list of dictionary of transaction data from pdf"""
        statement_dataframe_list: list[pd.DataFrame] = tabula.read_pdf(statement_name, pages='all')

        if len(statement_dataframe_list) <= 0:
            return []

        indexes: dict[str, int] = {}
        indexes["date"] = 0
        indexes["balance"] = -1
        indexes["income"], indexes["expense"], fail = self.get_pdf_statement_column_expense_indexes(statement_dataframe_list)
        indexes["description"] = indexes["income"] - 1
    
        self.reset_object()
        if not fail:
            transactions: list[dict[str, Any]] = self.get_transactions_from_dataframe_list(statement_dataframe_list, indexes)

        return transactions