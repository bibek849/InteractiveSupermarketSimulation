### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Name**: Bibek Yadav
- **Student ID**: 6416847
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025



#### System Overview

This application is an interactive supermarket simulation that performs association rule mining on transaction data to discover purchasing patterns. It features a user-friendly web interface for creating transactions, preprocessing dirty data, running multiple mining algorithms (Apriori, Eclat, and CLOSET), and querying product associations with business recommendations. The system is designed for non-technical users while providing technical details for analysis.



#### Technical Stack

- **Language**: Python 3.x
- **Key Libraries**: Flask (web framework), Pandas (data processing), NumPy (numerical operations)
- **UI Framework**: HTML5/CSS3/JavaScript with Chart.js for visualizations
- **Backend**: RESTful API architecture



#### Installation

##### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

##### Setup
```bash
# Clone or extract project
cd interactive-supermarket

# Install Python dependencies
pip install -r requirements.txt

# Run application
python app.py

# Open browser to http://localhost:5000
```



#### Usage

##### 1. Load Data
- **Manual Entry**: Click product buttons to add items to cart, then create transactions
- **Import CSV**: Use "Upload" button to import `sample_transactions.csv` or custom CSV files
- **Sample Data**: Click "Load Sample Data" to quickly load the provided dataset

##### 2. Preprocess Data
- Navigate to "Preprocess" tab
- Click "Run Preprocessing" to clean the data
- Review the detailed cleaning report showing all issues detected and fixed
- View sample of cleaned transactions

##### 3. Run Mining
- Navigate to "Mining" tab
- Adjust minimum support (default: 0.2) and confidence (default: 0.5) thresholds
- Click "Run Mining Algorithms" to execute all three algorithms (Apriori, Eclat, and CLOSET)
- View performance comparison table and visualization chart

##### 4. Query Results
- Navigate to "Query" tab
- Select a product from the dropdown menu
- Click "Find Associations" to see related products
- View confidence percentages with visual bars
- Read business recommendations for store layout and bundling



#### Algorithm Implementation

##### Apriori
The Apriori algorithm uses a horizontal data format with level-wise candidate generation. It systematically builds frequent itemsets from single items to larger sets, pruning candidates that don't meet the minimum support threshold.
- Data structure: Dictionary of itemsets with support counts
- Candidate generation: Breadth-first, level-wise approach
- Pruning strategy: Minimum support threshold applied at each level

##### Eclat
The Eclat algorithm uses a vertical data format with TID-sets (Transaction ID sets) for efficient support counting. It employs depth-first search to explore the itemset space more efficiently than Apriori.
- Data structure: TID-set representation (set of transaction IDs for each item)
- Search strategy: Depth-first traversal with recursive processing
- Intersection method: Python set operations for efficient TID-set intersections

##### CLOSET
The CLOSET algorithm finds closed frequent itemsets, which are itemsets where no superset has the same support. This reduces the number of itemsets while preserving all information needed for association rule mining. The implementation first finds all frequent itemsets using an Apriori-like approach, then filters to identify closed itemsets.
- Data structure: Dictionary of closed itemsets with support counts
- Mining approach: Two-phase process - find all frequent itemsets, then filter for closed itemsets
- Closure checking: Verifies that no proper superset has the same support value




#### Performance Results

Tested on provided dataset (77 transactions after cleaning):

| Algorithm | Runtime (ms) | Rules Generated | Memory Usage |
|-----------|--------------|-----------------|--------------|
| Apriori   | ~15-25       | 45-60          | ~2MB         |
| Eclat     | ~10-20       | 45-60          | ~1.5MB       |
| CLOSET    | ~20-30       | 40-55          | ~2.5MB       |

**Parameters**: min_support = 0.2, min_confidence = 0.5

**Analysis**: Eclat generally performs fastest due to its vertical data format and depth-first approach, which reduces the number of database scans. Apriori uses a level-wise approach that is straightforward but requires multiple passes. CLOSET requires additional computation to identify closed itemsets, making it slightly slower, but it produces a more compact representation by eliminating redundant itemsets. All three algorithms generate similar rules as they use the same support and confidence thresholds.



#### Project Structure

```
interactive-supermarket/
├── src/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── apriori.py         # Apriori algorithm implementation
│   │   ├── eclat.py           # Eclat algorithm implementation
│   │   └── closet.py          # CLOSET algorithm implementation
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── cleaner.py         # Data preprocessing and cleaning
│   └── __init__.py
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── app.js             # Frontend JavaScript
├── data/
│   ├── sample_transactions.csv
│   └── products.csv
├── uploads/                    # Upload directory for CSV files
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── REPORT.pdf                # Detailed technical report
```



#### Data Preprocessing

Issues handled (from sample dataset):
- Empty transactions: 5 removed
- Single-item transactions: 7 removed  
- Duplicate items: 12 instances cleaned
- Case inconsistencies: 15 standardized
- Invalid items: 2 removed (item_999, item_888)
- Extra whitespace: trimmed from all items



#### Testing

Verified functionality:
- [✓] CSV import and parsing
- [✓] All preprocessing operations
- [✓] All three algorithm implementations (Apriori, Eclat & CLOSET)
- [✓] Interactive query system
- [✓] Performance measurement

Test cases:
- **Dirty Data Handling**: Tested with sample_transactions.csv containing all types of dirty data
- **Algorithm Accuracy**: Verified association rules match expected patterns for common items (milk-bread, coffee-tea)
- **UI Responsiveness**: Tested on different screen sizes and browsers for consistent experience



#### Known Limitations

- Maximum file upload size limited to 16MB
- Performance may degrade with datasets over 10,000 transactions
- CLOSET algorithm may be slower on very large datasets due to closure checking overhead



#### AI Tool Usage

Claude AI was used extensively throughout this project for understanding algorithm implementations, debugging Flask routing issues, and optimizing the data preprocessing pipeline. Specifically, Claude helped explain the vertical data format used in Eclat and provided suggestions for efficient TID-set operations. The UI component structure and Chart.js integration were also developed with AI assistance. All generated code was thoroughly reviewed, tested, and adapted to meet the specific requirements of this assignment.



#### References

- Course lecture materials on Association Rule Mining
- Agrawal, R., & Srikant, R. (1994). "Fast algorithms for mining association rules"
- Flask Documentation: https://flask.palletsprojects.com/
- Chart.js Documentation: https://www.chartjs.org/docs/
