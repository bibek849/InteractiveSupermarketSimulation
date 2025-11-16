

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
import csv
from io import StringIO

# Import algorithms and preprocessing modules
from src.algorithms import AprioriAlgorithm, EclatAlgorithm, ClosetAlgorithm
from src.preprocessing import DataPreprocessor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables to store data
transactions = []
cleaned_transactions = []
products_df = None
preprocessing_report = {}
mining_results = {}

def load_products():
    """Load the products list from CSV"""
    global products_df
    products_df = pd.read_csv('data/products.csv')
    return products_df

def load_initial_transactions():
    """Load initial transactions from sample file"""
    global transactions
    df = pd.read_csv('data/sample_transactions.csv')
    transactions = []
    for _, row in df.iterrows():
        if pd.notna(row['items']) and row['items']:
            items = [item.strip() for item in row['items'].split(',')]
            transactions.append({
                'id': row['transaction_id'],
                'items': items
            })
    return transactions

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/products')
def get_products():
    """Get all products"""
    products = load_products()
    return jsonify(products.to_dict('records'))

@app.route('/api/transactions')
def get_transactions():
    """Get current transactions"""
    return jsonify(transactions)

@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    global transactions
    data = request.json
    new_id = max([t['id'] for t in transactions]) + 1 if transactions else 1
    transactions.append({
        'id': new_id,
        'items': data['items']
    })
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    global transactions
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read CSV content
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        
        new_transactions = []
        for row in csv_reader:
            if 'items' in row and row['items']:
                items = [item.strip() for item in row['items'].split(',')]
                new_transactions.append({
                    'id': int(row.get('transaction_id', len(transactions) + len(new_transactions) + 1)),
                    'items': items
                })
        
        transactions.extend(new_transactions)
        return jsonify({
            'success': True,
            'loaded': len(new_transactions),
            'total': len(transactions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/preprocess', methods=['POST'])
def preprocess_data():
    """Run data preprocessing"""
    global cleaned_transactions, preprocessing_report
    
    products = load_products()
    valid_products = products['product_name'].tolist()
    
    preprocessor = DataPreprocessor(transactions, valid_products)
    cleaned_transactions, preprocessing_report = preprocessor.clean()
    
    return jsonify({
        'success': True,
        'report': preprocessing_report,
        'cleaned_transactions': cleaned_transactions
    })

@app.route('/api/mine', methods=['POST'])
def run_mining():
    """Run association rule mining algorithms"""
    global mining_results
    
    data = request.json
    min_support = float(data.get('min_support', 0.2))
    min_confidence = float(data.get('min_confidence', 0.5))
    
    if not cleaned_transactions:
        return jsonify({'error': 'Please preprocess data first'}), 400
    
    results = {}
    
    # Run Apriori
    apriori = AprioriAlgorithm(cleaned_transactions, min_support, min_confidence)
    results['apriori'] = apriori.run()
    
    # Run Eclat
    eclat = EclatAlgorithm(cleaned_transactions, min_support, min_confidence)
    results['eclat'] = eclat.run()
    
    # Run CLOSET
    closet = ClosetAlgorithm(cleaned_transactions, min_support, min_confidence)
    results['closet'] = closet.run()
    
    mining_results = results
    
    return jsonify(results)

@app.route('/api/query', methods=['POST'])
def query_associations():
    """Query associations for a specific product"""
    data = request.json
    product = data.get('product', '').lower()
    
    if not mining_results:
        return jsonify({'error': 'Please run mining algorithms first'}), 400
    
    # Get rules where the product is in the antecedent
    associations = []
    seen = set()
    
    # Use Apriori results (you could also use Eclat or combine both)
    for rule in mining_results['apriori']['rules']:
        if product in rule['antecedent']:
            for consequent_item in rule['consequent']:
                if consequent_item not in seen:
                    seen.add(consequent_item)
                    associations.append({
                        'item': consequent_item,
                        'confidence': rule['confidence'] * 100,  # Convert to percentage
                        'support': rule['support'],
                        'lift': rule['lift']
                    })
    
    # Sort by confidence
    associations.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Generate recommendations
    recommendations = []
    if associations:
        if associations[0]['confidence'] > 70:
            recommendations.append(f"Strong association: Consider placing {associations[0]['item']} near {product}")
        
        # Bundle recommendation
        if len(associations) >= 2:
            bundle_items = [product] + [a['item'] for a in associations[:2]]
            recommendations.append(f"Potential bundle: {', '.join(bundle_items)}")
    
    return jsonify({
        'query': product,
        'associations': associations[:10],  # Return top 10
        'recommendations': recommendations
    })

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    stats = {
        'total_transactions': len(transactions),
        'cleaned_transactions': len(cleaned_transactions),
        'unique_products': 0
    }
    
    if cleaned_transactions:
        all_items = set()
        for t in cleaned_transactions:
            all_items.update(t['items'])
        stats['unique_products'] = len(all_items)
    
    return jsonify(stats)

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Reset all data"""
    global transactions, cleaned_transactions, preprocessing_report, mining_results
    transactions = load_initial_transactions()
    cleaned_transactions = []
    preprocessing_report = {}
    mining_results = {}
    return jsonify({'success': True})

if __name__ == '__main__':
    # Load initial data
    load_products()
    load_initial_transactions()
    
    app.run(debug=True, port=5000)
