from datetime import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from dataclasses import dataclass

@dataclass
class Transaction:
    date: datetime
    payee: str
    amount: int
    credited: bool

def parse_tr(tr) -> Transaction:
    cells = [td.get_text() for td in tr.findAll("td")]
    date = datetime.strptime(cells[0],"%Y/%m/%d")
    payee = cells[1]
    amount = int(cells[2].split()[1].replace(",",""))
    credited = (cells[-1] == "Credited")
    transaction = Transaction(
        date,
        payee,
        amount,
        credited
    )
    return transaction

def print_beancount(rows: list[Transaction]):
    for row in rows:
        print_beancount_row(row)

def print_beancount_row(transaction: Transaction):
    print(f"{transaction.date.strftime("%Y-%m-%d")} * \"{transaction.payee}\"")
    print(f"\tLiabilities:Checking:ESUN -{transaction.amount} NTD")
    print(f"\tExpenses:Uncategorised {transaction.amount} NTD")
    print()

def main():
    parser = ArgumentParser()
    parser.add_argument("source")
    parsed = parser.parse_args()

    with open(parsed.source) as f:
        doc = f.read()

    soup = BeautifulSoup(doc, features="html.parser")
    table = soup.findAll("table")[1]
    trs = table.findAll("tr")
    transactions = []
    for tr in trs[1:]:
        transactions.append(parse_tr(tr))
    print_beancount(transactions)
    

if __name__ == "__main__":
    main()

