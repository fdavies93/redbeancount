from dataclasses import dataclass
from datetime import datetime
from argparse import ArgumentParser

@dataclass
class EsunTransaction:
    account_no: str
    date: datetime
    db_cr: str
    amount: int
    fee: int
    subtotal: int
    type: str
    remark: str
    

def parse_row(row: str):
    account_no = row[:13] # account no.
    roc_date = row[14:21] # date in ROC format
    date = datetime(int(roc_date[:3]) + 1911, int(roc_date[3:5]), int(roc_date[5:7]))
    
    db_cr = row[21:23] # debit or credit?
    amount = int(row[24:36])
    fee = int(row[36:38])
    subtotal = int(row[39:51])

    type = row[53:59].strip()
    remark = row[59:64].strip()

    return EsunTransaction(
        account_no,
        date,
        db_cr,
        amount,
        fee,
        subtotal,
        type,
        remark
    )

def print_human(transactions: list[EsunTransaction]):
    for transaction in transactions:
        print_row_human(transaction)

def print_row_human(transaction: EsunTransaction):    
    print(f"Account #: {transaction.account_no}")
    print(f"Date:      {transaction.date}")
    print(f"DB/CR:     {transaction.db_cr}")
    print(f"Amount:    {transaction.amount}")
    print(f"Fee:       {transaction.fee}")
    print(f"Subtotal:  {transaction.subtotal}")
    print(f"Type:      {transaction.type}")
    print(f"Remark:    {transaction.remark}")

def print_csv(transactions: list[EsunTransaction]):
    fields = [
        "account_no",
        "date",
        "DB/CR",
        "amount",
        "fee",
        "subtotal",
        "type",
        "remark"
    ]
    print(",".join(fields))
    for transaction in transactions:
        print_row_csv(transaction)

def print_row_csv(transaction: EsunTransaction):
    fields = [
        transaction.account_no,
        transaction.date.strftime("%Y-%m-%d"),
        transaction.db_cr,
        str(transaction.amount),
        str(transaction.fee),
        str(transaction.subtotal),
        transaction.type,
        transaction.remark
    ]
    print(",".join(fields))

def print_beancount(transactions: list[EsunTransaction]):
    for transaction in transactions:
        print_row_beancount(transaction)

def print_row_beancount(transaction: EsunTransaction):
    remark = "Bank Transfer"
    if transaction.remark != "":
        remark = transaction.remark
    print(f"{transaction.date.strftime("%Y-%m-%d")} * \"{remark}\"")

    if transaction.db_cr == "DB":
        print(f"\tAssets:Checking:ESUN -{transaction.amount} NTD")
        print(f"\tExpenses:Uncategorised {transaction.amount} NTD")

    if transaction.db_cr == "CR":
        print(f"\tAssets:Checking:ESUN {transaction.amount} NTD")
        print(f"\tIncome:Uncategorised -{transaction.amount} NTD")

    print()

def main():

    parser = ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--format", choices=["csv","human","beancount"], default="human")
    parsed = parser.parse_args()
    
    with open(parsed.source, encoding="Big5") as source:
        rows = []
        while True:
            row = source.readline()
            if row == "": break
            try: 
                transaction = parse_row(row)
                rows.append(transaction)
            except Exception:
                continue

    if parsed.format == "csv":
        print_csv(rows)
    elif parsed.format == "human":
        print_human(rows)
    elif parsed.format == "beancount":
        print_beancount(rows)


if __name__ == "__main__":
    main()
