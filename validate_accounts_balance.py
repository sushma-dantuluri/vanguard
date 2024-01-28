####################################################
# Script Usage: python validate_accounts_balance.py
####################################################

import pandas as pd
import argparse


def compute_balance(transactions_file):

    # read csv files
    transactions_data = pd.read_csv(transactions_file)
    # Group by product_id, account_id, and transaction_type
    grouped_transactions = transactions_data.groupby(['product_id', 'account_id', 'transaction_type']).sum()
    # Unstack the DataFrame to make it easier to calculate the balance
    unstacked = grouped_transactions.unstack(level='transaction_type').fillna(0)
    # Calculate the balance
    unstacked['balance'] = unstacked['amount']['deposit'] - unstacked['amount']['withdrawal']

    return unstacked


def compare_balance(accounts_file, unstacked_transactions):

    account_balance_data = pd.read_csv(accounts_file)
    # sort the data based on product_id
    account_balance_data = account_balance_data.sort_values(by=["product_id"])
    # Create an empty 'balance' column in account_balance_data
    account_balance_data['calculated_balance'] = 0

    # Iterate through rows and fill the 'balance' column
    for index, row in account_balance_data.iterrows():
        product_id = row['product_id']
        account_id = row['account_id']
        # Find the corresponding balance in the unstacked DataFrame
        balance_value = unstacked_transactions.loc[(product_id, account_id), 'balance']
        # Fill the 'calculated_balance' column in account_balance_data
        account_balance_data.at[index, 'calculated_balance'] = balance_value

    for index, row in account_balance_data.iterrows():
        account_balance_data['balance_validation'] = "CORRECT" if row['total_product_balance'] == row['calculated_balance'] else "WRONG"

    return account_balance_data


def main(args):
    accounts_balance = compute_balance(args.transactions_file)
    account_balance_validation = compare_balance(args.accounts_file, accounts_balance)

    # Print the product accounts balance comparison
    print(account_balance_validation)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate and validate the balance of accounts',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--accounts_file', help="FILE WITH ACCOUNTS BALANCE", default='account.csv', type=str)
    parser.add_argument('-t', '--transactions_file', help="FILE WITH LIST OF TRANSACTIONS", default='transactions.csv', type=str)
    args = parser.parse_args()

    main(args)
