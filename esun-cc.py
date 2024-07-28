from datetime import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from dataclasses import dataclass
import json
import re

@dataclass
class Transaction:
    date: datetime
    payee: str
    amount: int
    credited: bool
    category: str

@dataclass
class MapEntry:
   pattern: str # regexp pattern to match in payee
   new_category: str
   new_payee: str
    

def parse_tr(tr) -> Transaction:
    cells = [td.get_text() for td in tr.findAll("td")]
    date = datetime.strptime(cells[0],"%Y/%m/%d")
    payee = cells[1]
    amount = int(cells[2].split()[1].replace(",",""))
    credited = (cells[-1] == "Credited")
    category = "Expenses:Uncategorised"
    
    transaction = Transaction(
        date,
        payee,
        amount,
        credited,
        category
    )
    return transaction

def print_beancount(rows: list[Transaction]):
    for row in rows:
        print_beancount_row(row)

def print_beancount_row(transaction: Transaction):
    print(f"{transaction.date.strftime("%Y-%m-%d")} * \"{transaction.payee}\"")
    print(f"\tLiabilities:CreditCard:ESUN -{transaction.amount} NTD")
    print(f"\t{transaction.category} {transaction.amount} NTD")
    print()

def reclassify_from_map(transactions: list[Transaction], map_list: list[MapEntry]) -> list[Transaction]:
    new_transactions = []
    for transaction in transactions:
        working_transaction = Transaction(transaction.date, transaction.payee, transaction.amount, transaction.credited, transaction.category)
        for map_entry in map_list:
            if re.match(map_entry.pattern, transaction.payee) == None:
                continue
            working_transaction.payee = map_entry.new_payee
            working_transaction.category = map_entry.new_category
            break
        new_transactions.append(working_transaction)
    return new_transactions

def main():
    parser = ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--map")
    parsed = parser.parse_args()

    with open(parsed.source) as f:
        doc = f.read()

    soup = BeautifulSoup(doc, features="html.parser")
    table = soup.findAll("table")[1]
    trs = table.findAll("tr")
    transactions = []
    for tr in trs[1:]:
        transactions.append(parse_tr(tr))

    if parsed.map != None:
        with open(parsed.map) as f:
            map_json = json.load(f)
            map_list = [MapEntry(obj["pattern"], obj["new_category"], obj["new_payee"]) for obj in map_json]
        transactions = reclassify_from_map(transactions, map_list)
        
    print_beancount(transactions)
    

if __name__ == "__main__":
    main()

