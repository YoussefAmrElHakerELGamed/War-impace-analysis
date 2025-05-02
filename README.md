Here’s your complete `README.md` file written in a single section with no collapsible parts, ready to paste into your repository:

# DataTools Wars: Economic Impact Analysis of Modern Conflicts

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)

An interactive dashboard analyzing the economic impact of modern wars and conflicts using World Bank economic indicators.

## 🌍 Overview

This project examines how major conflicts (Iraq War, Syrian Civil War, Ukraine Conflict, Yemeni Civil War) have affected key economic indicators in involved countries compared to global powers. The analysis includes:

- GDP trends before, during, and after conflicts
- Changes in trade balances and exports
- Inflation (CPI) and unemployment patterns
- Country-specific deep dives

## 📊 Key Features

- **Interactive Streamlit dashboard** with multiple visualization tabs  
- **Automated data fetching** from World Bank API  
- **Comparative analysis** of pre-war vs. during-war periods  
- **8 specialized visualizations** showing different economic dimensions  
- **Export functionality** for results and raw data  

## 📈 Included Visualizations

1. GDP Trends in War-Affected Countries  
2. Consumer Price Index (CPI) Trends  
3. GDP per Capita Change During Wars  
4. Trade Balance: Russia vs USA  
5. Export Changes During Conflicts  
6. GDP per Capita Comparison (War vs Global Powers)  
7. Unemployment Changes During Wars  
8. Egypt-Specific Economic Trends  

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/datatools-wars.git
   cd datatools-wars


2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

![Stream lit app](https://war-impace-analysis.streamlit.app/)

The app will automatically:

1. Fetch data from World Bank API
2. Clean and process the data
3. Perform comparative analysis
4. Launch interactive visualizations

## 📂 Project Structure

```
datatools-wars/
├── app.py                # Main Streamlit application
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── .gitignore            # Files to ignore in version control
└── assets/               # Optional: Store images/sample data
```

## 📝 Requirements

* Python 3.8+
* Streamlit
* Pandas
* Matplotlib
* Seaborn
* Requests

Install all requirements with:

```bash
pip install -r requirements.txt
```

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

```

Let me know if you'd like help generating the LICENSE file or a sample screenshot for the `assets/` folder.
```
