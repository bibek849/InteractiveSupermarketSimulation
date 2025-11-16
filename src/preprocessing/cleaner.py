"""Data preprocessing and cleaning functionality"""


class DataPreprocessor:
    """Handles all data preprocessing tasks"""
    
    def __init__(self, transactions, valid_products):
        self.transactions = transactions
        self.valid_products = [p.lower() for p in valid_products]
        self.report = {
            'total_transactions': len(transactions),
            'empty_transactions': 0,
            'single_item_transactions': 0,
            'duplicate_items_count': 0,
            'case_inconsistencies': 0,
            'invalid_items': 0,
            'whitespace_issues': 0,
            'cleaned_transactions': 0,
            'total_items_after': 0,
            'unique_products_after': 0
        }
    
    def clean(self):
        """Main cleaning function"""
        cleaned = []
        
        for transaction in self.transactions:
            items = transaction['items']
            
            # Check for empty transaction
            if not items or (len(items) == 1 and items[0] == ''):
                self.report['empty_transactions'] += 1
                continue
            
            # Clean items
            cleaned_items = []
            seen = set()
            
            for item in items:
                if not item or item.strip() == '':
                    continue
                    
                # Check for whitespace issues
                if item != item.strip():
                    self.report['whitespace_issues'] += 1
                    
                # Standardize to lowercase and strip whitespace
                clean_item = item.strip().lower()
                
                # Check for case inconsistency
                if item.strip() != clean_item and item.strip().lower() == clean_item:
                    self.report['case_inconsistencies'] += 1
                
                # Check if valid product
                if clean_item not in self.valid_products:
                    self.report['invalid_items'] += 1
                    continue
                
                # Check for duplicates
                if clean_item in seen:
                    self.report['duplicate_items_count'] += 1
                    continue
                    
                seen.add(clean_item)
                cleaned_items.append(clean_item)
            
            # Check for single-item transaction
            if len(cleaned_items) <= 1:
                self.report['single_item_transactions'] += 1
                continue
                
            if cleaned_items:
                cleaned.append({
                    'id': transaction['id'],
                    'items': cleaned_items
                })
        
        self.report['cleaned_transactions'] = len(cleaned)
        self.report['total_items_after'] = sum(len(t['items']) for t in cleaned)
        all_items = set()
        for t in cleaned:
            all_items.update(t['items'])
        self.report['unique_products_after'] = len(all_items)
        
        return cleaned, self.report

