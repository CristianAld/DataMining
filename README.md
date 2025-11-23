### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Name**: Cristian Aldana, Samuel Artiste
- **Student ID**: 6426411, 6538723
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025



#### System Overview

This project is an interactive application that simulates a supermarket transaction system to perform Association Rule Mining on customer data. It integrates a data preprocessing pipeline with custom implementations of the Apriori and Eclat algorithms to discover and compare purchasing patterns. The tool features a user-friendly dashboard for generation transacations, visualizing algorithmic performs in the console, and querying product recommendations based on association strength.



#### Technical Stack

- **Language**: Python 3.0
- **Key Libraries**: Pandas, psutil, itertools
- **UI Framework**: Tkinter



#### Installation

##### Prerequisites
- Python 3

##### Setup
No set up, run the main python file

# Clone or extract project
(https://github.com/CristianAld/DataMining.git)

# Install dependencies
pip install pandas
pip install psutil

# Run application
Run Main python file 

#### Usage

##### 1. Load Data
- **Manual Entry**: Click items to create transactions
- **Import CSV**: Use "Import" button to load `sample_transactions.csv`

##### 2. Preprocess Data
- Automatically runs data for you when you import the sample_transaction.csv

##### 3. Run Mining
- Set minimum support and confidence thresholds already added. 
- Wait for completion (~1-3 seconds)

##### 4. Query Results
- Select product from dropdown
- View associated items and recommendation report strength


#### Algorithm Implementation

##### Apriori
The Apriori implementation utilizes a dictionary of TID-sets (vertical data encoding), instead of traditional horizontal, to allow for efficient support counting through set intersections rather than repeated database scans. The algorithm proceeds with a breadth-first, level-wise candidate generation strategy, iteratively building larger itemsets from valid smaller ones. The pruning strategy is based on a minimum support threshold, discarding infrequent itemsets at each level before proceeding.

##### Eclat
The Eclat implementation uses a vertical TID-set representation, mapping each item directly to the set of transaction IDs in which it appears. It employs a depth first search strategy, recursively extending frequent itemsets to explore the search space. Support counting is performed through set intersection operations, allowing the algorithm to determine the support of candidate itemsets without scanning the entire database.

#### Performance Results

Tested on provided dataset (80-100 transactions after cleaning):

| Algorithm | Runtime (ms) | Rules Generated | Memory Usage |
|-----------|--------------|-----------------|--------------|
| Apriori   | 0.0          | [11]            | [0.04MB]     |
| Eclat     | 1.0          | [11]            | [0.01MB]     |

**Parameters**: min_support = 0.2, min_confidence = 0.5

**Analysis**: 
Based on the analysis done and the test case used we are able to find that Apriori algorithm was indeed faster than Eclat but Apriori actually consumed 0.03 more MB of Memory than Eclat which means Eclat is slower but utilizes less Memory. 

#### Project Structure

```
project-root/
├── src/
│   └── main.py
├── data/
│   ├── sample_transactions.csv
│   └── products.csv
├── README.md
├── REPORT.pdf
```
#### Data Preprocessing

Issues handled:
- Total transactions scanned: 100
- Empty transactions: 5 removed
- Single-item transactions: 6 removed
- Duplicate items: 9 instances cleaned
- Invalid items: 2 removed
- Extra whitespace: trimmed from all items



#### Testing

Verified functionality:
- [✓] CSV import and parsing
- [✓] All preprocessing operations
- [✓] Two algorithm implementations
- [✓] Interactive query system
- [✓] Performance measurement

Test cases:
| Feature tested | Test Data input | Expected Outcome|
|-----------|--------------|-----------------|
| Case Inconsistency   | Milk, milk, BREAD     | Items are standardized to {'milk', 'bread'}           |
| Duplicate Item counting     | T1: Bread, Milk, Milk       | Preprocessing Report: Duplicates detected: 1. Final transaction: {bread, milk}|


#### Known Limitations
Since the Apriori implementation is not library-optimized, generating candidates for every iteration can lead to significant memory use, especially with dense datasets or when the maximum frequent itemset size is large.



#### AI Tool Usage
During the implementation of this project, we relied on Gemini AI, primarily for coding assistance. We used it to help guide and explain functionalities like how to implement preprocessing for CSV standardization, and helping to walk through the complex logic and implementation of the Association rule mining algorithms. At first we prototyped by having Gemini generate HTML/ Javascript code for the initial interactive system, but ended up making the change to Tkinter. Github Copilot was also used to help during the implementation phase to help reduce and understand boilerplate code when writing the Tikinter UI and integrating the performance tracking. AI definitely helped us in the developing and debugging phase of the algorithms and assisting with general project documentation and allowed us to propel the development of this project.

#### References

- Course lecture materials
- Google Gemini AI
- Copilot 
- Pandas Doc
- Tkinter Doc
- psutil Doc
