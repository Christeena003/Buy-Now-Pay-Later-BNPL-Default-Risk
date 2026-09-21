# 📊 BNPL Financial Default Risk Analytics

A full-stack data analytics project built with **Python** and **Streamlit** that analyses Buy Now Pay Later (BNPL) customer data to identify default risk patterns, generate actionable business insights, and provide an interactive dashboard.

---

## 📁 Project Structure

```
bnpl_default_risk/
│
├── app.py                  # Streamlit dashboard (frontend)
├── data_analytics.py       # Core analytics pipeline (backend)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

BNPL_Financial_Default_Risk_Dataset.csv   # Raw dataset (root level)
```

---

## 📋 Dataset Overview

| Column | Type | Description |
|---|---|---|
| `Customer_ID` | ID | Unique customer identifier |
| `Age` | Numeric | Customer age in years |
| `Employment_Status` | Categorical | Employed / Student / Freelancer / Unemployed |
| `Income_USD` | Numeric | Annual income in USD |
| `Credit_Score` | Numeric | Credit score on 300–900 scale |
| `Total_BNPL_Active_Loans` | Numeric | Number of currently active BNPL loans |
| `Total_BNPL_Debt_USD` | Numeric | Total outstanding BNPL debt |
| `Late_Payment_History` | Binary | Yes / No |
| `Shopping_Category_Most_Frequent` | Categorical | Fashion / Electronics / Travel / etc. |
| `Average_Transaction_Value_USD` | Numeric | Average BNPL transaction value |
| `Default_Risk` | Target | Low / Medium / High |

**Dataset size:** 10,000 customer records

---

## 🔧 Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Clone or copy the project

```bash
# If using git
git clone <repository-url>
cd "IBM Project"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r bnpl_default_risk/requirements.txt
```

### 4. Run the Streamlit app

```bash
cd bnpl_default_risk
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🗂️ Dashboard Pages

| Page | Description |
|---|---|
| 🏠 **Overview** | KPI cards, risk distribution pie chart, key metric comparisons |
| 🔍 **Data Quality** | Missing values, duplicate detection, cleaning log, full stats |
| 📋 **Summary Statistics** | Grouped averages, totals and counts by risk, employment, category and age |
| 📈 **Risk Analysis** | Credit score histograms, income vs debt scatter, DTI box plots, credit band risk |
| 👥 **Demographic Insights** | Risk by employment, age group heat maps, income violins |
| 🛒 **Behavioural Patterns** | Shopping category analysis, correlation heatmap, loan distribution |
| 💡 **Business Insights** | Auto-generated findings and recommendations with a decision framework |
| 📂 **Raw Data Explorer** | Multi-filter interactive table with CSV export |

---

## 🔬 Analytics Pipeline (`data_analytics.py`)

```
load_data()         →  Load CSV into Pandas DataFrame
validate_data()     →  Detect missing values, duplicates, unexpected categories
clean_data()        →  Impute, encode, derive features (DTI ratio)
compute_summary()   →  Grouped aggregations (risk, employment, category, age, credit band)
generate_insights() →  Rule-based business insight generation
```

### Derived Features

| Feature | Formula |
|---|---|
| `Debt_to_Income_Ratio` | `Total_BNPL_Debt_USD / Income_USD` |
| `Late_Payment_Binary` | `Yes → 1, No → 0` |
| `Age_Group` | Bucketed: 18-25, 26-35, 36-45, 46-55, 56+ |
| `Credit_Band` | Standard bands: Very Poor, Poor, Fair, Good, Very Good, Exceptional |

---

## 💡 Key Business Findings

1. **High-risk customers** have significantly lower credit scores, higher DTI ratios, and more active BNPL loans than low-risk customers.
2. **Late payment history** is the single strongest predictor of default risk.
3. **Unemployed borrowers** carry the highest average BNPL debt relative to income.
4. **Students** show above-average exposure despite very low incomes.
5. A **DTI ceiling of 0.15** would filter out the majority of high-risk applicants automatically.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Pandas | Data loading, cleaning, aggregation |
| NumPy | Numerical operations |
| Plotly | Interactive charts |
| Seaborn / Matplotlib | Statistical plots |
| Streamlit | Web dashboard frontend |
| scikit-learn | (Available for future ML extension) |

---

## 📄 License

This project is developed for educational and analytical purposes as part of an IBM Data Analytics initiative.
