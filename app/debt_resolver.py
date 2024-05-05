from flask import render_template
from app.models import User, db, GroupTransaction
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

        # Calculate net amount to be paid to (positive) or paid by (negative) each person
        for i in range(n):
            for j in range(n):
                amount[i] += (graph[j][i] - graph[i][j])

        min_heap = []  # Debtors
        max_heap = []  # Creditors

        # Create min and max heaps
        for i in range(n):
            if amount[i] < 0:
                heapq.heappush(min_heap, (amount[i], i))  # Min-heap for debtors
            elif amount[i] > 0:
                heapq.heappush(max_heap, (-amount[i], i))  # Max-heap for creditors (negate amount)

        results = []
        # Settle debts
        while min_heap and max_heap:
            debt_amount, debtor = heapq.heappop(min_heap)
            credit_amount, creditor = heapq.heappop(max_heap)

            settled_amount = min(-debt_amount, -credit_amount)  # Amount is negated back
            debtor_user = User.query.get(persons[debtor])
            creditor_user = User.query.get(persons[creditor])
            results.append(f"{debtor_user.first_name} pays {settled_amount} euros to {creditor_user.first_name}")

            # Update the heaps
            if -debt_amount > settled_amount:
                heapq.heappush(min_heap, (debt_amount + settled_amount, debtor))
            if -credit_amount > settled_amount:
                heapq.heappush(max_heap, (credit_amount + settled_amount, creditor))

        return results


def read_db_to_adjacency_matrix():
    persons = set()  # Store unique person IDs

    # Using SQLAlchemy to query the Transaction model
    transactions = GroupTransaction.query.all()

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

def build_adjacency_matrix_from_transactions(transactions):
    persons = {}
    index = 0
    adjacency_matrix = []

    for transaction in transactions:
        if transaction.payer_id not in persons:
            persons[transaction.payer_id] = index
            index += 1
            adjacency_matrix.append([0] * len(persons))

        if transaction.debtor_id not in persons:
            persons[transaction.debtor_id] = index
            index += 1
            adjacency_matrix.append([0] * len(persons))

        payer_index = persons[transaction.payer_id]
        debtor_index = persons[transaction.debtor_id]
        adjacency_matrix[payer_index][debtor_index] += transaction.amount
        # Ensure mutual debts are considered:
        adjacency_matrix[debtor_index][payer_index] -= transaction.amount

    return adjacency_matrix, list(persons.keys())


def resolve_group_debts(group_id):
    # Fetch transactions related to the specified group only
    transactions = GroupTransaction.query.filter_by(group_id=group_id).all()

    # to calculate the total amount each member needs to pay or receive
    # calculating the net balance for each user

    net_balances = {}
    for transaction in transactions:
        # For each transaction, add/subtract the amount to/from the appropriate user's balance
        net_balances[transaction.debtor_id] = net_balances.get(transaction.debtor_id, 0) - transaction.amount
        net_balances[transaction.payer_id] = net_balances.get(transaction.payer_id, 0) + transaction.amount

    # split the balances into payers and receivers
    payers = [(user_id, balance) for user_id, balance in net_balances.items() if balance > 0]
    receivers = [(user_id, -balance) for user_id, balance in net_balances.items() if balance < 0]

    # Sort by amount to optimize the number of transactions
    payers.sort(key=lambda x: x[1], reverse=True)
    receivers.sort(key=lambda x: x[1])

    payment_instructions = []
    i, j = 0, 0
    # go through the payers and receivers and settle debts
    while i < len(payers) and j < len(receivers):
        payer_id, pay_amount = payers[i]
        receiver_id, receive_amount = receivers[j]

        # Determine amount to be settled
        settled_amount = min(pay_amount, receive_amount)
        payers[i] = (payer_id, pay_amount - settled_amount)
        receivers[j] = (receiver_id, receive_amount - settled_amount)

        # Create a payment instruction
        payer = User.query.get(payer_id)
        receiver = User.query.get(receiver_id)
        payment_instructions.append(f"{payer.first_name} pays {settled_amount} euros to {receiver.first_name}")

        # Move to the next payer/receiver if they have nothing left to pay/receive
        if payers[i][1] == 0:
            i += 1
        if receivers[j][1] == 0:
            j += 1

    return payment_instructions

def read_db_to_adjacency_matrix():
    persons = set()  # Store unique person IDs

    # Using SQLAlchemy to query the Transaction model
    transactions = GroupTransaction.query.all()

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


# Function to implement the Ford-Fulkerson method for maximum flow problem
def ford_fulkerson(graph, source, sink):
    parent = [-1] * len(graph)
    max_flow = 0

    def bfs(residual_graph):
        visited = [False] * len(residual_graph)
        queue = [source]
        visited[source] = True

        while queue:
            u = queue.pop(0)

            for ind, val in enumerate(residual_graph[u]):
                if not visited[ind] and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u
                    if ind == sink:
                        return True
        return False

    residual_graph = [row[:] for row in graph]

    while bfs(residual_graph):
        path_flow = float('Inf')
        s = sink

        while s != source:
            path_flow = min(path_flow, residual_graph[parent[s]][s])
            s = parent[s]

        v = sink
        while v != source:
            u = parent[v]
            residual_graph[u][v] -= path_flow
            residual_graph[v][u] += path_flow
            v = parent[v]

        max_flow += path_flow

    return max_flow
