"""
Data Persistence Module.
"""
# Standard Library Imports
from collections import deque

# Application Imports
from schemas import Spending

# TODO: define an abstract DataPersister Base Class;
# Derive in-memory and SQL solutions.
IN_MEMORY_STORAGE = {
    "USD_by_amount": deque([]),
    "HUF_by_amount": deque([]),
    "USD_by_time": deque([]),
    "HUF_by_time": deque([]),
    "ALL_by_amount": deque([]),
    "ALL_by_time": deque([]),
}


def persist_spending(spending: Spending):
    for prefix in [spending.currency, "ALL"]:
        # By Amount
        for index, item in enumerate(IN_MEMORY_STORAGE[f"{prefix}_by_amount"]):
            if item.amount > spending.amount:
                IN_MEMORY_STORAGE[f"{prefix}_by_amount"].insert(index,
                                                                spending)
                break
        else:
            IN_MEMORY_STORAGE[f"{prefix}_by_amount"].append(spending)

        # By Time
        for index, item in enumerate(IN_MEMORY_STORAGE[f"{prefix}_by_time"]):
            if item.spent_at > spending.spent_at:
                IN_MEMORY_STORAGE[f"{prefix}_by_time"].insert(index, spending)
                break
        else:
            IN_MEMORY_STORAGE[f"{prefix}_by_time"].append(spending)
