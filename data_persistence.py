# Application Imports
from schemas import Spending

# TODO: define an abstract DataPersister Base Class;
# Derive in-memory and SQL solutions.
IN_MEMORY_STORAGE = []


def persist_spending(spending: Spending):
    IN_MEMORY_STORAGE.append(spending)
