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

def resolve_group_debts(transactions):
    # Mapping user IDs to matrix indices
    user_index = {}
    current_index = 0
    for transaction in transactions:
        if transaction.payer_id not in user_index:
            user_index[transaction.payer_id] = current_index
            current_index += 1
        if transaction.debtor_id not in user_index:
            user_index[transaction.debtor_id] = current_index
            current_index += 1

    # Create adjacency matrix for the Ford-Fulkerson algorithm
    size = len(user_index)
    graph = [[0] * size for _ in range(size)]

    for transaction in transactions:
        payer_idx = user_index[transaction.payer_id]
        debtor_idx = user_index[transaction.debtor_id]
        graph[payer_idx][debtor_idx] += transaction.amount

    # Placeholder source and sink - in an actual application, these would be dynamically determined
    source = 0  # Typically the group admin or an arbitrary point
    sink = size - 1  # Could be another arbitrary point or calculated based on conditions

    max_flow = ford_fulkerson(graph, source, sink)

    # Convert the flow values back to human-readable transaction instructions
    payment_instructions = []
    for i in range(size):
        for j in range(size):
            if graph[i][j] > 0:
                payer_id = list(user_index.keys())[list(user_index.values()).index(i)]
                debtor_id = list(user_index.keys())[list(user_index.values()).index(j)]
                payment_instructions.append(f"User {payer_id} should pay {graph[i][j]} to User {debtor_id}")

    return max_flow, payment_instructions

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
