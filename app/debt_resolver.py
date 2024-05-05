from flask import render_template
from app.models import User, db, GroupTransaction, Transaction
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

    # Now, you need to calculate the total amount each member needs to pay or receive.
    # This is like calculating the net balance for each user.

    net_balances = {}
    for transaction in transactions:
        # For each transaction, add/subtract the amount to/from the appropriate user's balance
        net_balances[transaction.debtor_id] = net_balances.get(transaction.debtor_id, 0) - transaction.amount
        net_balances[transaction.payer_id] = net_balances.get(transaction.payer_id, 0) + transaction.amount

    # Now, split the balances into payers and receivers
    payers = [(user_id, balance) for user_id, balance in net_balances.items() if balance > 0]
    receivers = [(user_id, -balance) for user_id, balance in net_balances.items() if balance < 0]

    # Sort them by the amount to optimize the number of transactions
    payers.sort(key=lambda x: x[1], reverse=True)
    receivers.sort(key=lambda x: x[1])

    payment_instructions = []
    i, j = 0, 0
    # Go through the payers and receivers and settle debts
    while i < len(payers) and j < len(receivers):
        payer_id, pay_amount = payers[i]
        receiver_id, receive_amount = receivers[j]

        # Determine the amount to be settled
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
    transactions = GroupTransaction.query.all()
    users = User.query.all()
    matrix = {}
    persons = {}

    # Initialize matrix and persons dictionary
    for user in users:
        persons[user.id] = user.first_name  # Simplified; adjust as needed
        for other_user in users:
            matrix[(user.id, other_user.id)] = 0

    # Populate matrix with transaction data
    for transaction in transactions:
        matrix[(transaction.debtor_id, transaction.payer_id)] += transaction.amount

    return matrix, persons


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
