import time
import tkinter as tk
import itertools
from tkinter import filedialog, messagebox, ttk
import csv
from collections import Counter, defaultdict
import pandas as pd
from io import StringIO # Used for reading CSV content as a file-like object
import os
import psutil


PRODUCTS = [
    'Milk', 'Bread', 'Eggs', 'Cereal', 'Coffee', 
    'Apples', 'Bananas', 'Chicken', 'Cheese', 'Water'
]

all_transactions = []
current_basket = []
transaction_id_counter = 1

PRODUCTS_INVENTORY_FILE = 'products.csv'

class SupermarketApp:
    def __init__(self, master):
        self.master = master
        master.title("🛒 Supermarket Simulator: Transaction Creator")
        
        self.VALID_PRODUCTS_SET = set() 
        self.load_valid_products_list(PRODUCTS_INVENTORY_FILE)

        self.frame_import = tk.Frame(master, padx=10, pady=10, bd=2, relief=tk.GROOVE)
        self.frame_import.pack(fill='x', pady=5)
        self.setup_import_section()

        ttk.Separator(master, orient='horizontal').pack(fill='x', pady=10)
        
        self.setup_recommendation_controls()

        self.frame_main = tk.Frame(master)
        self.frame_main.pack(fill='both', expand=True)

        # Product Selection Section
        self.frame_products = tk.LabelFrame(self.frame_main, text="Select Products", padx=10, pady=10)
        self.frame_products.pack(side='left', fill='y', padx=10, pady=10)
        self.setup_product_section()

        # Current Basket Section
        self.frame_basket = tk.LabelFrame(self.frame_main, text="Current Basket", padx=10, pady=10)
        self.frame_basket.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.setup_basket_section()
        
        # Transactions List Section
        self.frame_transactions = tk.LabelFrame(master, text="Created Transactions", padx=10, pady=10)
        self.frame_transactions.pack(fill='both', expand=True, padx=10, pady=10)
        self.setup_transactions_section()
        
        # Initial display update
        self.update_basket_display()
        self.render_transactions_table()


    
    def setup_import_section(self):
        """Creates the file import interface."""
        tk.Label(self.frame_import, text="Import Transactions from CSV:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.import_button = tk.Button(self.frame_import, text="📂 Load CSV File", command=self.import_transactions_from_csv)
        self.import_button.pack(side='left', padx=10)
        self.import_status_label = tk.Label(self.frame_import, text="No file loaded.")
        self.import_status_label.pack(side='left', padx=10)

    def setup_product_section(self):
        """Creates the clickable buttons for products."""
        for product in PRODUCTS:
            btn = tk.Button(self.frame_products, text=product, width=15, 
                            command=lambda p=product: self.add_product_to_basket(p))
            btn.pack(pady=5)

    def setup_basket_section(self):
        """Creates the basket listbox and control buttons."""
        self.basket_listbox = tk.Listbox(self.frame_basket, height=10)
        self.basket_listbox.pack(fill='x', expand=True, pady=5)

        self.btn_create_transaction = tk.Button(self.frame_basket, text="🛒 Create Transaction", 
                                                command=self.create_transaction, state=tk.DISABLED)
        self.btn_create_transaction.pack(fill='x', pady=5)

        self.btn_clear_basket = tk.Button(self.frame_basket, text="🗑️ Clear Basket", 
                                          command=self.clear_basket)
        self.btn_clear_basket.pack(fill='x', pady=5)

    def setup_transactions_section(self):
        """Creates the Treeview widget for displaying transactions."""
        self.transactions_tree = ttk.Treeview(self.frame_transactions, 
                                             columns=("ID", "Items", "Count"), 
                                             show="headings")
        self.transactions_tree.heading("ID", text="Transaction ID", anchor=tk.W)
        self.transactions_tree.heading("Items", text="Items Purchased")
        self.transactions_tree.heading("Count", text="# Unique Items")
        
        self.transactions_tree.column("ID", width=100, anchor=tk.W)
        self.transactions_tree.column("Items", width=450, anchor=tk.W)
        self.transactions_tree.column("Count", width=100, anchor=tk.CENTER)

        self.transactions_tree.pack(fill='both', expand=True)


    def add_product_to_basket(self, product):
        """Adds a product to the current basket."""
        current_basket.append(product)
        self.update_basket_display()

    def clear_basket(self):
        """Clears the current basket state."""
        global current_basket
        current_basket = []
        self.update_basket_display()

    def update_basket_display(self):
        """Updates the listbox display and button state."""
        self.basket_listbox.delete(0, tk.END)
        for product in current_basket:
            self.basket_listbox.insert(tk.END, product)
            
        # Enable/Disable the create transction button
        if current_basket:
            self.btn_create_transaction.config(state=tk.NORMAL)
        else:
            self.btn_create_transaction.config(state=tk.DISABLED)

    def create_transaction(self):
        """Saves the current basket as a transaction and clears the basket."""
        global all_transactions, transaction_id_counter
        
        # Get unique items from the basket
        unique_items = sorted(list(set(current_basket)))

        # Create the new transaction object
        new_transaction = {
            'id': transaction_id_counter,
            'items': unique_items,
            'count': len(unique_items)
        }
        
        # Add to global list and increment counter
        all_transactions.append(new_transaction)
        transaction_id_counter += 1

        self.render_transactions_table()
        self.clear_basket()
        messagebox.showinfo("Success", f"Transaction T{new_transaction['id']} created successfully!")


    def import_transactions_from_csv(self):
        """Opens a file dialog, reads the CSV, and processes the data."""
        # Open file dialog to select CSV file
        filepath = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            self.import_status_label.config(text="File loading cancelled.")
            return

        # Use the cleaner `_parse_csv_data` function
        success, imported_count, error_count = self._parse_csv_data(filepath)
        
        if success:
            self.render_transactions_table()
            self.update_product_dropdown()
            total_transactions = len(all_transactions)
            
            status_text = f"Imported {imported_count} transactions. (Total: {total_transactions} loaded)."
            if error_count > 0:
                 status_text += f" {error_count} lines skipped (errors/empty)."
            
            self.import_status_label.config(text=status_text, fg='darkgreen')
        
            try:
                self.compare_performance(min_support=0.2, min_confidence=0.5)
            except Exception as e:
                print(f"Algorithm execution failed: {e}")

        else:
            self.import_status_label.config(text=f"Import failed. {imported_count}", fg='red')


    def _parse_csv_data(self, filepath):
        global all_transactions, transaction_id_counter
        
        # TRACKING VARIABLES
        initial_total_transactions = 0
        removed_empty_transactions = 0
        removed_single_transactions = 0
        total_duplicate_items_detected = 0
        total_invalid_items_detected = 0

        # FINAL STATS
        final_items_count = 0
        final_unique_products_set = set()

        imported_count = 0
        error_count = 0
        
        try:
            #Read the CSV content using pandas, setting the first row (index 0) as the header.
            df = pd.read_csv(filepath, header=0, encoding='utf-8') 
            
            #Basic validation: Must have at least two columns. 
            if df.shape[1] < 2:
                # If there aren't two columns of data after the header is read, error
                return False, "CSV format error: Expected at least two columns (ID, Items).", error_count
            
            # Reset column indexing for easier reference (assuming ID is column 0, Items is column 1)
            # .fillna prevents 'nan' strings from appearing in the transactions.

            df_items = df.iloc[:, 1].fillna('')
            initial_total_transactions = len(df_items)

            #Determines the separator used within the 'Items' column (Column 1)
            sample_items = df_items.head(10).astype(str).str.cat(sep='')
            
            if ',' in sample_items:
                item_separator = ','
            elif '|' in sample_items:
                item_separator = '|'
            elif ';' in sample_items:
                item_separator = ';'
            else:
                item_separator = ',' 

            for items_string in df_items:
                try:                    
                    # Split the string by the determined separator, filter out empty strings, and trim whitespace
                    raw_items_found = [item.strip().lower() for item in items_string.split(item_separator)]

                    # Remove empty strings resulting from extra delimiters like ',,'
                    cleaned_items = [item for item in raw_items_found if item]
                    
                    # Tracking empty transactions
                    if not cleaned_items:
                        removed_empty_transactions += 1
                        # If there are no items, skip them
                        continue
                        # Otherwise, process the unique items as usual
                    items_pre_validation = list(set(cleaned_items))
                    
                    # tracking duplicate items
                    total_duplicate_items_detected += (len(cleaned_items) - len(items_pre_validation))
                    
                    valid_items = []
                    for item in items_pre_validation:
                        if item in self.VALID_PRODUCTS_SET:
                            valid_items.append(item)
                        else:
                            # Tracking invalid items
                            total_invalid_items_detected += 1
                    
                    unique_items = valid_items
                    item_count = len(unique_items)

                    # Removing transactions containing only one item
                    if item_count < 2:
                        # tracking single-item transactions
                        if item_count == 1:
                            removed_single_transactions += 1
                        continue

                    # Create transaction data structure
                    new_transaction = {
                        'id': transaction_id_counter,
                        'items': unique_items,
                        'count': item_count
                    }

                    all_transactions.append(new_transaction)
                    transaction_id_counter += 1
                    imported_count += 1
                    
                    #Updating final dataset statistics
                    final_items_count += item_count
                    final_unique_products_set.update(unique_items)

                except Exception as e:
                    print(f"Error processing item string '{items_string}': {e}")
                    error_count += 1
           
           # REPORT GENERATION
            self._generate_report(
                initial_total_transactions,
                removed_empty_transactions,
                removed_single_transactions,
                total_duplicate_items_detected,
                total_invalid_items_detected,
                imported_count,
                final_items_count,
                len(final_unique_products_set)
            )
            return True, imported_count, error_count
            
        except FileNotFoundError:
            return False, "File not found.", error_count
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty or missing data after header.", error_count
        except Exception as e:
            return False, f"An unexpected error occurred: {e}", error_count

    def render_transactions_table(self):
        """Clears and re-populates the transaction Treeview widget."""
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        # Insert new data
        for transaction in all_transactions:
            self.transactions_tree.insert("", tk.END, 
                                          values=(f"T{transaction['id']}", 
                                                  ", ".join(transaction['items']), 
                                                  transaction['count']))
            
    def load_valid_products_list(self, filepath):
        """
        Reads the inventory CSV, standardizes product names, and populates
        the VALID_PRODUCTS_SET for validation.
        """
        try:
            # Load the inventory CSV. We assume 'product_name' is in the second column (index 1) 
            df_inventory = pd.read_csv(filepath, encoding='utf-8')
            
            # --- Standardize and Collect Product Names ---
            # Access the 'product_name' column (or second column if no header)
            # Convert all product names to lowercase and strip whitespace
            valid_names = df_inventory.iloc[:, 1].astype(str).str.strip().str.lower()

            # Populate the class set with unique, standardized names
            self.VALID_PRODUCTS_SET = set(valid_names)

            print(f"Loaded {len(self.VALID_PRODUCTS_SET)} unique valid products for validation.")
            if hasattr(self, 'product_choice'):
                self.update_product_dropdown()

        except FileNotFoundError:
            messagebox.showerror("Error", f"Product Inventory file '{filepath}' not found. Cannot validate transactions.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product inventory: {e}")

    def _generate_report(self, 
                     total_initial, 
                     removed_empty, 
                     removed_single, 
                     duplicates, 
                     invalids, 
                     valid_transactions, 
                     final_item_count, 
                     final_unique_count):
    
        # Calculate total transactions removed (for the report summary)
        total_removed = total_initial - valid_transactions

        report = (
            "\n"
            "=========================================\n"
            "        DATA PREPROCESSING REPORT\n"
            "=========================================\n"
            "\n"
            "## Before Cleaning:\n"
            f"- Total transactions scanned: {total_initial}\n"
            f"- Removed Empty transactions: {removed_empty}\n"
            f"- Removed Single-item transactions: {removed_single}\n"
            f"- Duplicates detected: {duplicates} instances\n"
            f"- Invalid products detected: {invalids} instances\n"
            "\n"
            "## After Cleaning:\n"
            f"- Transactions accepted (Valid): {valid_transactions}\n"
            f"- Total transactions removed: {total_removed}\n"
            f"- Final Total Items: {final_item_count}\n"
            f"- Final Unique Products: {final_unique_count}\n"
            "=========================================\n"
        )
        
        print(report)
        
        status_text = (f"Imported {valid_transactions} transactions. "
                    f"Removed {total_removed} transactions. "
                    f"Duplicates/Invalid items cleaned.")
        
        self.import_status_label.config(text=status_text, fg='darkgreen')


    # --APRIORI ALGORITHM IMPLEMENTATION--

    def _apriori_gen(self, Lk_minus_1):
        """Generates candidate k-itemsets (Ck) from frequent (k-1)-itemsets (Lk-1)."""
        Ck = set()
        list_Lk_minus_1 = sorted([tuple(sorted(t)) for t in Lk_minus_1]) # Ensure sorted tuples

        if not list_Lk_minus_1:
            return Ck

        k = len(list_Lk_minus_1[0]) + 1
        
        # Join Step: Combine every pair of itemsets Lk-1
        for i in range(len(list_Lk_minus_1)):
            for j in range(i + 1, len(list_Lk_minus_1)):
                L1 = list(list_Lk_minus_1[i])
                L2 = list(list_Lk_minus_1[j])
                
                # Check if the first (k-2) items are the same
                if L1[:-1] == L2[:-1]:
                    candidate = tuple(sorted(set(L1) | set(L2)))
                    
                    # Pruning Step: Check if all (k-1) subsets of the candidate are in Lk-1
                    is_valid = True
                    for subset_tuple in itertools.combinations(candidate, k - 1):
                        if subset_tuple not in Lk_minus_1:
                            is_valid = False
                            break
                    
                    if is_valid:
                        Ck.add(candidate)
                        
        return Ck
    
    def run_apriori(self, min_support_ratio=0.2, min_confidence=0.5):
        """
        Executes the Apriori algorithm with simplified core logic using TID-sets 
        for fast support counting.
        """
        transaction_items = [t['items'] for t in all_transactions]
        if not transaction_items:
            return None, "No transactions available."

        process = psutil.Process(os.getpid())
        start_time = time.time()
        start_memory = process.memory_info().rss

        # vertical Data Format Preparation (Used for Efficient Counting)
        item_transaction_map, N = self._encode_data_vertical(transaction_items)
        min_support_count = min_support_ratio * N
        frequent_itemsets = {} 

        # L1 (Frequent 1-Itemsets)
        L1 = set()
        for item, tids in item_transaction_map.items():
            support = len(tids)
            if support >= min_support_count:
                item_tuple = tuple([item])
                L1.add(item_tuple)
                frequent_itemsets[item_tuple] = support
        
        Lk_minus_1 = L1
        
        while Lk_minus_1:
            Ck = self._apriori_gen(Lk_minus_1)
            Lk = set()
            
            for candidate in Ck:
                candidate_tids = item_transaction_map[candidate[0]].copy() 
                for item in candidate[1:]:
                    candidate_tids.intersection_update(item_transaction_map[item])
                
                support = len(candidate_tids)
                
                if support >= min_support_count:
                    Lk.add(candidate)
                    frequent_itemsets[candidate] = support
            
            Lk_minus_1 = Lk

        # extract Association Rules
        rules = self._apriori_rules_gen(frequent_itemsets, N, min_confidence)
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        performance_data = {
            'Algorithm': 'Apriori', 
            'Time (ms)': round((end_time - start_time) * 1000, 2), 
            'Rules Generated': len(rules), 
            'Memory (MB)': round((end_memory - start_memory) / (1024 * 1024), 2)
        }
        return rules, performance_data
    
    def _encode_data_vertical(self, transaction_items):
        """Converts transaction list into vertical TID-set format."""
        
        item_transaction_map = defaultdict(set)
        
        for t_id, items in enumerate(transaction_items):
            for item in items:
                item_transaction_map[item].add(t_id)
                
        return item_transaction_map, len(transaction_items)

    def _eclat_recursive(self, prefix, tid_set_map, N, min_support_count, frequent_sets):

        for item_A, tid_set_A in tid_set_map.items():
            
            candidate_itemset = prefix + (item_A,)
            
            # Record the frequent itemset
            frequent_sets[candidate_itemset] = len(tid_set_A)
            
            new_tid_set_map = {}
            
            # Find potential extensions (items that appear AFTER item_A in the sorted list)
            # This is the DFS (depth-first search) traversal
            sorted_items = sorted(tid_set_map.keys())
            
            # Optimization: Only extend with items lexicographically greater than item_A
            start_index = sorted_items.index(item_A) + 1
            
            for item_B in sorted_items[start_index:]:
                tid_set_B = tid_set_map[item_B]
                
                # Efficient Intersection Operation (Support Counting)
                intersect_tid_set = tid_set_A.intersection(tid_set_B)
                
                if len(intersect_tid_set) >= min_support_count:
                    new_tid_set_map[item_B] = intersect_tid_set
            
            # Recurse if the new equivalence class is not empty
            if new_tid_set_map:
                self._eclat_recursive(candidate_itemset, new_tid_set_map, N, min_support_count, frequent_sets)

    def run_eclat(self, min_support_ratio=0.2, min_confidence=0.5):
        """Executes the Eclat algorithm with performance tracking."""
        
        transaction_items = [t['items'] for t in all_transactions]
        if not transaction_items:
            return None, "No transactions available."

        # Performance Tracking Setup
        process = psutil.Process(os.getpid())
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        # vertical Data Format Preparation (TID-sets)
        item_tid_sets, N = self._encode_data_vertical(transaction_items)
        min_support_count = min_support_ratio * N
        frequent_itemsets = {}
        
        initial_tid_set_map = {
            item: tids for item, tids in item_tid_sets.items() 
            if len(tids) >= min_support_count
        }

        # executes Recursive DFS
        self._eclat_recursive(
            prefix=tuple(), 
            tid_set_map=initial_tid_set_map, 
            N=N, 
            min_support_count=min_support_count, 
            frequent_sets=frequent_itemsets
        )

        # extract Association Rules (using the same Apriori rule generation logic)
        rules = self._apriori_rules_gen(frequent_itemsets, N, min_confidence)
        
        # Performance Tracking Finalization
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        performance_data = {
            'Algorithm': 'Eclat',
            'Time (ms)': round((end_time - start_time) * 1000, 2),
            'Rules Generated': len(rules),
            'Memory (MB)': round((end_memory - start_memory) / (1024 * 1024), 2),
            'Support': min_support_ratio,
            'Confidence': min_confidence
        }
        
        return rules, performance_data
    
    def _apriori_rules_gen(self, frequent_itemsets, N, min_confidence):
        """Generates association rules from frequent itemsets based on minimum confidence."""
        rules = [] # Stores (antecedent, consequent, support, confidence, lift)
        
        for itemset, support_count in frequent_itemsets.items():
            support_itemset = support_count / N
            
            # Only interested in itemsets with two or more items (to form a rule A -> B)
            if len(itemset) < 2:
                continue
                
            # Generate all possible non-empty subsets (antecedents)
            for k in range(1, len(itemset)):
                for antecedent_tuple in itertools.combinations(itemset, k):
                    
                    antecedent = tuple(sorted(list(antecedent_tuple)))
                    consequent = tuple(sorted(list(set(itemset) - set(antecedent))))
                    
                    # Retrieve support for the antecedent (A)
                    support_A_count = frequent_itemsets.get(antecedent)
                    
                    if support_A_count is None: continue 
                    
                    support_A = support_A_count / N
                    
                    # Calculate Confidence: Confidence(A -> B) = Support(A U B) / Support(A)
                    confidence = support_itemset / support_A
                    
                    if confidence >= min_confidence:
                        # Calculate Lift
                        support_B_count = frequent_itemsets.get(consequent)
                        support_B = support_B_count / N if support_B_count else 0
                        
                        # Lift(A -> B) = Confidence(A -> B) / Support(B)
                        lift = confidence / support_B if support_B > 0 else 0
                        
                        rules.append({
                            'antecedents': antecedent,
                            'consequents': consequent,
                            'support': support_itemset,
                            'confidence': confidence,
                            'lift': lift
                        })
                            
        return rules
    
    def compare_performance(self, min_support=0.2, min_confidence=0.5):
        """Runs both algorithms and presents a performance comparison table."""
        
        # --- Run Apriori ---
        apriori_rules, apriori_perf = self.run_apriori(min_support, min_confidence)
        
        # --- Run Eclat ---
        eclat_rules, eclat_perf = self.run_eclat(min_support, min_confidence)
        
        if apriori_perf is None or eclat_perf is None:
            messagebox.showerror("Error", "Analysis failed. Check console for details.")
            return

        df_comparison = pd.DataFrame([apriori_perf, eclat_perf])
        
        print("\n" + "="*50)
        print("           ALGORITHM PERFORMANCE COMPARISON ")
        print("="*50)
        print(f"Parameters: Min Support={min_support*100}%, Min Confidence={min_confidence*100}%")
        print("-" * 50)
        
        # Use a simplified text output for the console report
        print(df_comparison[['Algorithm', 'Rules Generated', 'Time (ms)', 'Memory (MB)']].to_string(index=False))
        print("="*50)
        
        return df_comparison
    
    def setup_recommendation_controls(self):
        """Creates ONLY the dropdown and button. Output goes to terminal."""
        # Small frame at the bottom just for controls
        control_frame = tk.Frame(self.master, pady=10, bd=2, relief=tk.RAISED) # Added border for visibility
        control_frame.pack(side='bottom', fill='x')

        # Label 1: Section Title
        tk.Label(control_frame, text=" Recommendations:", font=("Arial", 10, "bold")).pack(side='left', padx=10)
        
        # Label 2: Explicit Instruction (This was missing)
        tk.Label(control_frame, text="Select Product:", font=("Arial", 10)).pack(side='left', padx=5)

        # Dropdown (Combobox)
        self.product_choice = ttk.Combobox(control_frame, width=20, state="readonly")
        self.product_choice.pack(side='left', padx=5)
        
        # Populate the dropdown immediately
        self.update_product_dropdown()

        # Button
        btn_recommend = tk.Button(control_frame, text="Print Insights to Console", bg="#007BFF", fg="white", 
                                  command=self.show_recommendations_in_terminal)
        btn_recommend.pack(side='left', padx=10)
        
        # Label 3: Output Location Hint
        tk.Label(control_frame, text="(Check Terminal for Output)", font=("Arial", 8, "italic"), fg="gray").pack(side='left')

    def update_product_dropdown(self):
        """Refreshes the product list in the recommendation dropdown."""
        if hasattr(self, 'product_choice'):
            if self.VALID_PRODUCTS_SET:
                product_list = sorted(list(self.VALID_PRODUCTS_SET))
                self.product_choice['values'] = product_list
                self.product_choice.set(product_list[0])  # Auto-select first item
            else:
                self.product_choice['values'] = []
                self.product_choice.set("No products loaded")

    def show_recommendations_in_terminal(self):
        # 1. Validation
        selected_product = self.product_choice.get().strip().lower()
        
        if not selected_product:
            print("\n[ERROR] Please select a product from the dropdown first.")
            return

        # 2. Run Algorithm
        rules, _ = self.run_apriori(min_support_ratio=0.05, min_confidence=0.2)

        if not rules:
            print("\n[INFO] No rules generated. Try importing a larger CSV or lowering support.")
            print(f"[DEBUG] Total transactions: {len(all_transactions)}")
            return

        # 3. Filter Rules and Keep Only the BEST rule for each consequent product
        best_recommendations = {}  # Dictionary: product -> best_rule_data
        
        for rule in rules:
            if selected_product in rule['antecedents']:
                for assoc_prod in rule['consequents']:
                    conf_val = rule['confidence'] * 100
                    
                    # If this product isn't in our dict yet, OR if this rule has better confidence
                    if assoc_prod not in best_recommendations or conf_val > best_recommendations[assoc_prod]['conf']:
                        # Visual Bar Logic for Terminal
                        if conf_val >= 70:
                            bar_visual = "#" * 10 + " (Strong)"
                        elif conf_val >= 50:
                            bar_visual = "#" * 6 + " (Moderate)"
                        else:
                            bar_visual = "#" * 4 + " (Weak)"
                        
                        best_recommendations[assoc_prod] = {
                            'prod': assoc_prod.title(), 
                            'conf': conf_val, 
                            'conf_str': round(conf_val, 1),
                            'bar': bar_visual,
                            'support': rule['support'],
                        }

        # 4. Convert to list and Sort by confidence
        recommendations = list(best_recommendations.values())
        recommendations.sort(key=lambda x: x['conf'], reverse=True)

        # 5. PRINT TO TERMINAL
        print("\n" + "="*60)
        print(f" RECOMMENDATION REPORT FOR: {selected_product.title()}")
        print("="*60)
        
        if recommendations:
            print(f"Customers who bought {selected_product.title()} also bought:\n")
            for rec in recommendations:
                print(f"- {rec['prod']:<15} {rec['conf_str']}% of the time  {rec['bar']}")
            
            print("-" * 60)
            
            # Business Logic
            top_rec = recommendations[0]
            if top_rec['conf'] >= 50:
                print(f" Recommendation: Place {top_rec['prod']} near {selected_product.title()}.")
                print(f" Bundle Idea: {selected_product.title()} + {top_rec['prod']}")
            else:
                print(f" Recommendation: Consider a discount on {top_rec['prod']} to drive sales.")
           
        else:
            print("No significant associations found for this product.")
            print(f"\n[DEBUG INFO]")
            print(f"- Total rules generated: {len(rules)}")
            print(f"- Looking for '{selected_product}' in antecedents")
            
            # Show what products ARE in the rules
            all_antecedents = set()
            for rule in rules:
                all_antecedents.update(rule['antecedents'])
            
            if all_antecedents:
                print(f"- Products with associations: {', '.join(sorted(all_antecedents))}")
            else:
                print("- No products have associations at current thresholds")
        
        print("="*60 + "\n")
    

if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketApp(root)
    root.mainloop()