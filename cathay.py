from argparse import ArgumentParser
import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class Transaction:
    transaction_date: datetime
    billing_date: datetime
    is_transfer: bool
    amount: int
    category: str
    counterparty: str
    note: str

'''
Row layout is:
0 Transaction date (2024/10/04\\n22:00)
1 Billing date (2024/10/07)
2 Description ( 跨行轉入 (bank transfer) | 卡片費用 (card fees) | 簽帳消費 (spending) )
3 Withdraw ( - | int )
4 Deposit ( - | int )
5 Balance ( int ) - not used
6 Transaction data ( str ) - counterparty account number
7 Notes
'''
def parse_row(row: list[str]) -> Transaction:
    date_str = row[0]
    transaction_date = datetime.strptime(date_str.split()[0], "%Y/%m/%d")
    billing_date = datetime.strptime(row[1], "%Y/%m/%d")
   
    is_transfer = False
    category = ""

    if row[2] == "卡片費用":
        category = "Expenses:Bank-Fees"
    elif row[3] == "簽帳消費":
        is_transfer = True

    amount = 0
    if row[3] == "−":
        amount = int(row[4].replace(",",""))
        category = "Income:Unassigned"
    elif row[4] == "−":
        amount = -int(row[3].replace(",",""))
        if category == "":
            category = "Expenses:Unassigned"

    return Transaction(
        transaction_date=transaction_date,
        billing_date=billing_date,
        is_transfer=is_transfer,
        amount=amount,
        category=category,
        counterparty=row[6],
        note=row[7].strip()
    )

def parse_csv(filename: str) -> list[Transaction]:
    rows: list[list[str]] = []
    transactions: list[Transaction] = []
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    for i, row in enumerate(rows):
        try:
            transaction = parse_row(row)
            transactions.append(transaction)
        except:
            print(f"Couldn't parse row {i}: {row}", file=sys.stderr)
            continue

    return transactions

def render_beancount_transaction(transaction: Transaction):
    print(f"{transaction.transaction_date.strftime("%Y-%m-%d")} * \"{transaction.note}\"")
    print(f"\tAssets:Checking:ESUN {transaction.amount} NTD")
    print(f"\t{transaction.category} {-transaction.amount} NTD")
    print()

def render_beancount(transactions: list[Transaction]): 
    for transaction in transactions:
        render_beancount_transaction(transaction)

def main():
    parser = ArgumentParser()
    parser.add_argument("file")
    parsed = parser.parse_args()
    # remapping step would go here 
    transactions = parse_csv(parsed.file)
    transactions.sort(key= lambda t: t.transaction_date )
    render_beancount(transactions)

if __name__ == "__main__":
    main()
