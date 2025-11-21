import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from collections import Counter
import pandas as pd
from io import StringIO # Used for reading CSV content as a file-like object


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
            total_transactions = len(all_transactions)
            
            status_text = f"Imported {imported_count} transactions. (Total: {total_transactions} loaded)."
            if error_count > 0:
                 status_text += f" {error_count} lines skipped (errors/empty)."
            
            self.import_status_label.config(text=status_text, fg='darkgreen')
        else:
            self.import_status_label.config(text=f"❌ Import failed. {imported_count}", fg='red')


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
        # Clear existing data
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
            # after the header row. We rely on the header being present in the first row.
            df_inventory = pd.read_csv(filepath, encoding='utf-8')
            
            # --- Standardize and Collect Product Names ---
            # 1. Access the 'product_name' column (or second column if no header)
            # 2. Convert all product names to lowercase and strip whitespace
            valid_names = df_inventory.iloc[:, 1].astype(str).str.strip().str.lower()

            # Populate the class set with unique, standardized names
            self.VALID_PRODUCTS_SET = set(valid_names)

            print(f"Loaded {len(self.VALID_PRODUCTS_SET)} unique valid products for validation.")
        
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
        
        # Print the report to the console (for debugging/review)
        print(report)
        
        # Display a concise version of the report in the GUI status label
        status_text = (f"Imported {valid_transactions} transactions. "
                    f"Removed {total_removed} transactions. "
                    f"Duplicates/Invalid items cleaned.")
        
        self.import_status_label.config(text=status_text, fg='darkgreen')

if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketApp(root)
    root.mainloop()