"""Implementation of Eclat Algorithm using vertical data format"""
import time
from collections import defaultdict
from itertools import combinations


class EclatAlgorithm:
    """Implementation of Eclat Algorithm using vertical data format"""
    
    def __init__(self, transactions, min_support=.2, min_confidence=0.5):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.tid_sets = {}  # Vertical representation
        self.frequent_itemsets = {}
        self.rules = []
        
    def create_tid_sets(self):
        """Convert horizontal format to vertical (TID-sets)"""
        self.tid_sets = defaultdict(set)
        
        for tid, transaction in enumerate(self.transactions):
            for item in transaction['items']:
                self.tid_sets[item].add(tid)
        
        return self.tid_sets
    
    def eclat_recursive(self, prefix, items, min_support_count):
        """Recursive Eclat algorithm"""
        while items:
            # Get first item
            item, tids = items[0]
            items = items[1:]
            
            # Check if frequent
            if len(tids) >= min_support_count:
                # Add to frequent itemsets
                new_itemset = tuple(sorted(prefix + [item]))
                self.frequent_itemsets[new_itemset] = len(tids) / len(self.transactions)
                
                # Generate combinations with remaining items
                suffix = []
                for other_item, other_tids in items:
                    # Intersection of TID sets
                    intersection = tids & other_tids
                    if len(intersection) >= min_support_count:
                        suffix.append((other_item, intersection))
                
                # Recursive call
                if suffix:
                    self.eclat_recursive(prefix + [item], suffix, min_support_count)
    
    def find_frequent_itemsets(self):
        """Main Eclat execution"""
        min_support_count = int(self.min_support * len(self.transactions))
        
        # Create vertical representation
        self.create_tid_sets()
        
        # Convert to list format for processing
        items = []
        for item, tids in self.tid_sets.items():
            if len(tids) >= min_support_count:
                items.append((item, tids))
                self.frequent_itemsets[tuple([item])] = len(tids) / len(self.transactions)
        
        # Sort items by support (optimization)
        items.sort(key=lambda x: len(x[1]), reverse=True)
        
        # Run Eclat
        for i, (item, tids) in enumerate(items):
            suffix = []
            for j in range(i + 1, len(items)):
                other_item, other_tids = items[j]
                intersection = tids & other_tids
                if len(intersection) >= min_support_count:
                    suffix.append((other_item, intersection))
            
            if suffix:
                self.eclat_recursive([item], suffix, min_support_count)
        
        return self.frequent_itemsets
    
    def generate_rules(self):
        """Generate association rules from frequent itemsets"""
        for itemset, support in self.frequent_itemsets.items():
            if len(itemset) > 1:
                # Generate all possible rules
                for i in range(1, len(itemset)):
                    for antecedent_tuple in self._get_subsets(itemset, i):
                        antecedent = set(antecedent_tuple)
                        consequent = set(itemset) - antecedent
                        
                        # Calculate confidence
                        antecedent_support = self.frequent_itemsets.get(tuple(sorted(antecedent)), 0)
                        if antecedent_support > 0:
                            confidence = support / antecedent_support
                            
                            if confidence >= self.min_confidence:
                                self.rules.append({
                                    'antecedent': list(antecedent),
                                    'consequent': list(consequent),
                                    'support': support,
                                    'confidence': confidence,
                                    'lift': confidence / self.frequent_itemsets.get(tuple(sorted(consequent)), 1)
                                })
        
        return self.rules
    
    def _get_subsets(self, itemset, size):
        """Get all subsets of given size from itemset"""
        return list(combinations(itemset, size))
    
    def run(self):
        """Run the complete Eclat algorithm"""
        start_time = time.time()
        
        self.find_frequent_itemsets()
        self.generate_rules()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            'algorithm': 'Eclat',
            'execution_time': execution_time,
            'frequent_itemsets': len(self.frequent_itemsets),
            'rules_generated': len(self.rules),
            'rules': self.rules
        }

