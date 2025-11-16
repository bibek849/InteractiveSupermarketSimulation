"""Implementation of Apriori Algorithm"""
import time
from itertools import combinations


class AprioriAlgorithm:
    """Implementation of Apriori Algorithm"""
    
    def __init__(self, transactions, min_support=0.2, min_confidence=0.5):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}
        self.rules = []
        
    def get_support(self, itemset):
        """Calculate support for an itemset"""
        count = 0
        for transaction in self.transactions:
            if set(itemset).issubset(set(transaction['items'])):
                count += 1
        return count / len(self.transactions) if self.transactions else 0
    
    def generate_candidates(self, prev_itemsets, k):
        """Generate candidate itemsets of size k"""
        candidates = []
        prev_list = list(prev_itemsets)
        
        for i in range(len(prev_list)):
            for j in range(i + 1, len(prev_list)):
                # Join step: merge itemsets that differ by one item
                union = sorted(list(set(prev_list[i]) | set(prev_list[j])))
                if len(union) == k and tuple(union) not in candidates:
                    candidates.append(tuple(union))
        
        return candidates
    
    def find_frequent_itemsets(self):
        """Find all frequent itemsets using Apriori"""
        # Start with frequent 1-itemsets
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
            candidates = self.generate_candidates(current_itemsets, k)
            
            # Prune candidates based on support
            next_itemsets = []
            for candidate in candidates:
                support = self.get_support(list(candidate))
                if support >= self.min_support:
                    next_itemsets.append(candidate)
                    self.frequent_itemsets[candidate] = support
            
            current_itemsets = next_itemsets
            k += 1
        
        return self.frequent_itemsets
    
    def generate_rules(self):
        """Generate association rules from frequent itemsets"""
        for itemset, support in self.frequent_itemsets.items():
            if len(itemset) > 1:
                # Generate all possible rules from this itemset
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
        """Run the complete Apriori algorithm"""
        start_time = time.time()
        
        self.find_frequent_itemsets()
        self.generate_rules()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            'algorithm': 'Apriori',
            'execution_time': execution_time,
            'frequent_itemsets': len(self.frequent_itemsets),
            'rules_generated': len(self.rules),
            'rules': self.rules
        }

