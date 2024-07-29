from argparse import ArgumentParser
from dataclasses import dataclass
from csv import reader
from datetime import datetime

@dataclass
class Transaction:
    date: datetime
    amount: int
    description: str
    account: str
    remark: str

def print_beancount_row(transaction: Transaction):
    if transaction.account.strip() != "":
        print(f"; {transaction.account}")
    
    print(f"{transaction.date.strftime("%Y-%m-%d")} * \"{transaction.description} {transaction.remark}\"")

    print(f"\tAssets:Checking:Cathay {transaction.amount} NTD")

    # this seems easy to write a map for
    if transaction.amount < 0:
        print(f"\tExpenses:Uncategorised {-transaction.amount} NTD")
    else:
        print(f"\tIncome:Uncategorised {-transaction.amount} NTD")

    print()

def parse_row(row: list[str]) -> Transaction:
    date = datetime(int(row[0][0:4]), int(row[0][4:6]), int(row[0][6:8]))
    amount = 0
    if row[2].strip() != "":
        amount = -int(row[2])
    if row[3].strip() != "":
        amount = int(row[3])

    description = row[5]
    account = row[6]
    remark = row[7]
    
    return Transaction(
        date,
        amount,
        description,
        account,
        remark
    )

def main():
    parser = ArgumentParser()
    parser.add_argument("source")
    parsed = parser.parse_args()

    with open(parsed.source, encoding="Big5") as f:
        f.readline()
        f.readline() # skip first line
        csv = reader(f)
        transactions = [parse_row(row) for row in csv]


    for row in transactions:
        print_beancount_row(row)

if __name__ == "__main__":
    main()
