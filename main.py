import streamlit as st
from collections import defaultdict
import pandas as pd


class Expense:
    def __init__(self, description, amount, paid_by, split_among):
        self.description = description
        self.amount = amount
        self.paid_by = paid_by
        self.split_among = split_among


class ExpenseManager:
    def __init__(self):
        self.expenses = []
        self.balances = defaultdict(float)

    def add_expense(self, expense):
  
        if expense.paid_by not in expense.split_among:
            expense.split_among.append(expense.paid_by)

        self.expenses.append(expense)


        share = expense.amount / len(expense.split_among)


        self.balances[expense.paid_by] += expense.amount

 
        for person in expense.split_among:
            self.balances[person] -= share

    def get_expenses(self):
   
        expense_data = [{
            "Description": expense.description,
            "Amount": expense.amount,
            "Paid By": expense.paid_by,
            "Shared Among": ", ".join(expense.split_among),
        } for expense in self.expenses]

        return pd.DataFrame(expense_data)

    def get_balances(self):
    
        return pd.DataFrame(list(self.balances.items()), columns=["Person", "Balance"])

    def get_debts(self):

        creditors = {k: v for k, v in self.balances.items() if v > 0}
        debtors = {k: v for k, v in self.balances.items() if v < 0}
        
        debts = []
        for debtor, debt in debtors.items():
            for creditor, credit in creditors.items():
                if debt == 0:
                    break
                payment = min(-debt, credit)
                debts.append((debtor, creditor, payment))
                creditors[creditor] -= payment
                debtors[debtor] += payment
        
        return pd.DataFrame(debts, columns=["Debtor", "Creditor", "Amount"])


manager = ExpenseManager()


st.title("Roommate Expense Sharing App")


with st.form(key='expense_form'):
    description = st.text_input("Expense Description")
    amount = st.number_input("Expense Amount", min_value=0.0, step=0.01)
    paid_by = st.text_input("Paid By")
    split_among = st.text_input("Split Among (comma-separated)")

 
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        split_among_list = [person.strip() for person in split_among.split(",")]
        expense = Expense(description, amount, paid_by, split_among_list)
        manager.add_expense(expense)
        st.success("Expense added!")


st.header("All Expenses")
expenses_df = manager.get_expenses()
st.table(expenses_df)


st.header("Current Balances")
balances_df = manager.get_balances()
st.table(balances_df)


st.header("Who Owes Whom")
debts_df = manager.get_debts()
st.table(debts_df)
