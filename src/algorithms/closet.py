"""Implementation of CLOSET Algorithm for closed frequent itemsets"""
import time
from itertools import combinations


class ClosetAlgorithm:
    """Implementation of CLOSET Algorithm for closed frequent itemsets"""
    
    def __init__(self, transactions, min_support=0.2, min_confidence=0.5):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.closed_itemsets = {}
        self.frequent_itemsets = {}
        self.rules = []
        
    def get_support(self, itemset):
        """Calculate support for an itemset"""
        count = 0
        for transaction in self.transactions:
            if set(itemset).issubset(set(transaction['items'])):
                count += 1
        return count / len(self.transactions) if self.transactions else 0
    
    def is_closed(self, itemset, all_frequent_itemsets):
        """Check if an itemset is closed (no superset has same support)"""
        itemset_support = self.get_support(itemset)
        itemset_set = set(itemset)
        
        for other_itemset, other_support in all_frequent_itemsets.items():
            other_set = set(other_itemset)
            # Check if other is a proper superset
            if itemset_set.issubset(other_set) and itemset_set != other_set:
                if abs(other_support - itemset_support) < 0.0001:  # Same support
                    return False
        return True
    
    def find_frequent_itemsets(self):
        """First find all frequent itemsets using Apriori-like approach"""
        # Get all items
        all_items = set()
        for transaction in self.transactions:
            all_items.update(transaction['items'])
        
        # Find frequent 1-itemsets
        current_itemsets = []
        for item in all_items:
            support = self.get_support([item])
            if support >= self.min_support:
                current_itemsets.append(tuple([item]))
                self.frequent_itemsets[tuple([item])] = support
        
        k = 2
        while current_itemsets:
            # Generate candidates
            candidates = []
            prev_list = list(current_itemsets)
            
            for i in range(len(prev_list)):
                for j in range(i + 1, len(prev_list)):
                    union = sorted(list(set(prev_list[i]) | set(prev_list[j])))
                    if len(union) == k and tuple(union) not in candidates:
                        candidates.append(tuple(union))
            
            # Check support and add frequent itemsets
            next_itemsets = []
            for candidate in candidates:
                support = self.get_support(list(candidate))
                if support >= self.min_support:
                    next_itemsets.append(candidate)
                    self.frequent_itemsets[candidate] = support
            
            current_itemsets = next_itemsets
            k += 1
        
        return self.frequent_itemsets
    
    def find_closed_itemsets(self):
        """Find closed frequent itemsets"""
        # First find all frequent itemsets
        self.find_frequent_itemsets()
        
        # Filter to find closed itemsets
        for itemset, support in self.frequent_itemsets.items():
            if self.is_closed(list(itemset), self.frequent_itemsets):
                self.closed_itemsets[itemset] = support
        
        return self.closed_itemsets
    
    def generate_rules(self):
        """Generate association rules from closed frequent itemsets"""
        for itemset, support in self.closed_itemsets.items():
            if len(itemset) > 1:
                # Generate all possible rules
                for i in range(1, len(itemset)):
                    for antecedent_tuple in self._get_subsets(itemset, i):
                        antecedent = set(antecedent_tuple)
                        consequent = set(itemset) - antecedent
                        
                        # Calculate confidence
                        antecedent_support = self.closed_itemsets.get(tuple(sorted(antecedent)), 0)
                        if antecedent_support == 0:
                            # Fallback to frequent itemsets
                            antecedent_support = self.frequent_itemsets.get(tuple(sorted(antecedent)), 0)
                        
                        if antecedent_support > 0:
                            confidence = support / antecedent_support
                            
                            if confidence >= self.min_confidence:
                                self.rules.append({
                                    'antecedent': list(antecedent),
                                    'consequent': list(consequent),
                                    'support': support,
                                    'confidence': confidence,
                                    'lift': confidence / self.closed_itemsets.get(tuple(sorted(consequent)), 
                                        self.frequent_itemsets.get(tuple(sorted(consequent)), 1))
                                })
        
        return self.rules
    
    def _get_subsets(self, itemset, size):
        """Get all subsets of given size from itemset"""
        return list(combinations(itemset, size))
    
    def run(self):
        """Run the complete CLOSET algorithm"""
        start_time = time.time()
        
        self.find_closed_itemsets()
        self.generate_rules()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            'algorithm': 'CLOSET',
            'execution_time': execution_time,
            'frequent_itemsets': len(self.closed_itemsets),
            'rules_generated': len(self.rules),
            'rules': self.rules
        }

