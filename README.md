### Interactive Supermarket Simulation with Association Rule Mining

#### Author Information

- **Name**: Cristian Aldana, Samuel Artiste
- **Student ID**: 6426411, 
- **Course**: CAI 4002 - Artificial Intelligence
- **Semester**: Fall 2025



#### System Overview

[2-3 sentences describing what your application does]



#### Technical Stack

- **Language**: Python 3.0
- **Key Libraries**: Pandas, psutil
- **UI Framework**: Tkinter



#### Installation
You will need to install Pandas library and psutil libraries 
pip install pandas
pip install psutil

##### Prerequisites
- Python 3

##### Setup
No set up just run the main python file
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
- View associated items and recommendation strength
- Optional: View technical details (raw rules, performance metrics)


#### Algorithm Implementation

##### Apriori
[2-3 sentences on your implementation approach]
- Data structure: [e.g., dictionary of itemsets]
- Candidate generation: [breadth-first, level-wise]
- Pruning strategy: [minimum support]

##### Eclat
[2-3 sentences on your implementation approach]
- Data structure: [e.g., TID-set representation]
- Search strategy: [depth-first]
- Intersection method: [set operations]

##### CLOSET
[2-3 sentences on your implementation approach]
- Data structure: [e.g., FP-tree / prefix tree]
- Mining approach: [closed itemsets only]
- Closure checking: [method used]



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
│   └── main.[py/js/java]
├── data/
│   ├── sample_transactions.csv
│   └── products.csv
├── README.md
├── REPORT.pdf

#### Data Preprocessing

Issues handled:
- Empty transactions: [count] removed
- Single-item transactions: [count] removed
- Duplicate items: [count] instances cleaned
- Case inconsistencies: [count] standardized
- Invalid items: [count] removed
- Extra whitespace: trimmed from all items



#### Testing

Verified functionality:
- [✓] CSV import and parsing
- [✓] All preprocessing operations
- [✓] Two algorithm implementations
- [✓] Interactive query system
- [✓] Performance measurement

Test cases:
- [Describe 2-3 key test scenarios]
The key test cases included single-item transactions and empty transactions 


#### Known Limitations

[List any known issues or constraints, if applicable]



#### AI Tool Usage

[Required: 1 paragraph describing which AI tools you used and for what purpose]

Example:

"We used variety of AI tools, We allowed codex and ChatGPT to explain to us the process of the algorithms and create the algorithm functions, With Perplexity AI we used it to create the layout of Tkinter and explain basic GUI layout and how to expand it"


#### References

- Course lecture materials
- ChatGPT/Codex
- Perplexity AI
- Pandas Doc
- Tkinter Doc
- psutil Doc