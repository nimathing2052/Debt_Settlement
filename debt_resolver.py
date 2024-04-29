from flask import render_template
from app.models import Transaction, User, db
import heapq

# Comparator that will be used to make priority_queue
# containing pair of integers maxHeap Comparison is based
# on second entry in the pair which represents cash
# credit/debit
class AscCmp:
    def __call__(self, p1, p2):
        return p1[1] < p2[1]

# Comparator that will be used to make priority_queue
# containing pair of integers minHeap Comparison is based
# on second entry in the pair which represents cash
# credit/debit
class DscCmp:
    def __call__(self, p1, p2):
        return p1[1] > p2[1]

class Solution:
    def __init__(self):
        self.minQ = []
        self.maxQ = []

    def constructMinMaxQ(self, amount):
        for i in range(len(amount)):
            if amount[i] == 0:
                continue
            if amount[i] > 0:
                heapq.heappush(self.maxQ, (i, amount[i]))
            else:
                heapq.heappush(self.minQ, (i, amount[i]))

    def solveTransaction(self, persons):
        results = []
        while self.minQ and self.maxQ:
            maxCreditEntry = heapq.heappop(self.maxQ)
            maxDebitEntry = heapq.heappop(self.minQ)

            transaction_val = maxCreditEntry[1] + maxDebitEntry[1]
            debtor = maxDebitEntry[0]
            creditor = maxCreditEntry[0]
            owed_amount = 0

            if transaction_val == 0:
                owed_amount = maxCreditEntry[1]
            elif transaction_val < 0:
                owed_amount = maxCreditEntry[1]
                heapq.heappush(self.minQ, (maxDebitEntry[0], transaction_val))
            else:
                owed_amount = -maxDebitEntry[1]
                heapq.heappush(self.maxQ, (maxCreditEntry[0], transaction_val))

            # Use the User model to fetch user details
            debtor_user = User.query.get(persons[debtor])
            creditor_user = User.query.get(persons[creditor])

            results.append(f"{debtor_user.first_name} pays {owed_amount} euros to {creditor_user.first_name}")
        return results

    def minCashFlow(self, graph, persons):
        n = len(graph)
        amount = [0] * n
        for i in range(n):
            for j in range(n):
                diff = graph[j][i] - graph[i][j]
                amount[i] += diff
        self.constructMinMaxQ(amount)
        return self.solveTransaction(persons)
        n = len(graph)

        # Calculate the cash to be credited/debited to/from
        # each person and store in vector amount
        amount = [0] * n
        for i in range(n):
            for j in range(n):
                diff = graph[j][i] - graph[i][j]
                amount[i] += diff

        # Fill in both queues minQ and maxQ using amount
        # vector
        self.constructMinMaxQ(amount)

        # Solve the transaction using minQ, maxQ and amount
        # vector
        self.solveTransaction()

def read_db_to_adjacency_matrix():
    persons = set()  # Store unique person IDs

    # Using SQLAlchemy to query the Transaction model
    transactions = Transaction.query.all()

    # Determine unique persons
    for transaction in transactions:
        persons.add(transaction.payer_id)
        persons.add(transaction.debtor_id)

    persons = sorted(list(persons))  # Sort persons by their IDs (sorted for consistent order)

    n = len(persons)
    adjacency_matrix = [[0] * n for _ in range(n)]

    # Populate the adjacency matrix with transaction amounts
    for transaction in transactions:
        i = persons.index(transaction.payer_id)
        j = persons.index(transaction.debtor_id)
        adjacency_matrix[i][j] += transaction.amount

    return adjacency_matrix, persons