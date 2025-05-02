import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# App Configuration
st.set_page_config(
    page_title="DataTools Wars",
    page_icon="⚔️",
    layout="wide"
)

# Constants
BASE_URL = "http://api.worldbank.org/v2/country/all/indicator"
INDICATORS = {
    'NY.GDP.MKTP.CD': 'GDP (current US$)',
    'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
    'NE.EXP.GNFS.CD': 'Exports of goods and services (current US$)',
    'NE.IMP.GNFS.CD': 'Imports of goods and services (current US$)',
    'FP.CPI.TOTL': 'Consumer price index (2010 = 100)',
    'SL.UEM.TOTL.ZS': 'Unemployment, total (% of total labor force)',
    'GE.EST': 'Political Stability and Absence of Violence/Terrorism'
}
WAR_PERIODS = {
    'Iraq War': ('2003', '2011'),
    'Syrian Civil War': ('2011', '2023'),
    'Ukraine Conflict': ('2014', '2023'),
    'Yemeni Civil War': ('2014', '2023')
}
COUNTRIES_OF_INTEREST = ['EG', 'SY', 'IQ', 'UA', 'YE', 'US', 'DE', 'RU']
WAR_COUNTRIES = ['SY', 'IQ', 'UA', 'YE']

# Set pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
plt.style.use('ggplot')

# Helper Functions
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_wb_data(indicator, years='1960:2023'):
    url = f"{BASE_URL}/{indicator}?format=json&date={years}&per_page=20000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[1] if len(data) > 1 and data[1] else None
    except Exception as e:
        st.error(f"Error fetching data for {indicator}: {str(e)}")
        return None

def process_data(raw_data, indicator_name):
    processed = []
    for record in raw_data:
        if record.get('value') is not None:
            processed.append({
                'country': record['country']['value'],
                'country_code': record['country']['id'],
                'year': record['date'],
                'indicator': indicator_name,
                'value': record['value']
            })
    return pd.DataFrame(processed)

@st.cache_data
def get_all_indicators():
    all_data = []
    with st.spinner("Fetching World Bank data..."):
        for code, name in INDICATORS.items():
            raw_data = fetch_wb_data(code)
            if raw_data:
                df = process_data(raw_data, name)
                all_data.append(df)
    
    if not all_data:
        st.error("No data was fetched for any indicator")
        st.stop()
        
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df.pivot_table(
        index=['country', 'country_code', 'year'],
        columns='indicator',
        values='value'
    ).reset_index()

def clean_data(df):
    """Clean and prepare the dataset for analysis"""
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    df = df[df['country_code'].isin(COUNTRIES_OF_INTEREST)]
    
    if df.empty:
        st.error("No data available for selected countries")
        st.stop()
    
    if all(col in df.columns for col in ['Exports of goods and services (current US$)', 
                                        'Imports of goods and services (current US$)']):
        df['Trade Balance'] = df['Exports of goods and services (current US$)'] - \
                            df['Imports of goods and services (current US$)']
    
    df = df.sort_values(['country', 'year'])
    df = df.groupby('country').apply(lambda x: x.ffill())
    
    return df.dropna(subset=['GDP (current US$)'])

@st.cache_data
def analyze_war_impact(df):
    results = []
    
    with st.spinner("Analyzing war impacts..."):
        for war, (start, end) in WAR_PERIODS.items():
            war_start = int(start)
            war_end = int(end)
            pre_war = df[(df['year'].dt.year >= war_start - 5) & 
                        (df['year'].dt.year < war_start)]
            during_war = df[(df['year'].dt.year >= war_start) & 
                            (df['year'].dt.year <= war_end)]
            
            for country in df['country_code'].unique():
                country_name = df[df['country_code'] == country]['country'].iloc[0]
                country_pre = pre_war[pre_war['country_code'] == country]
                country_during = during_war[during_war['country_code'] == country]
                
                if not country_pre.empty and not country_during.empty:
                    for indicator in INDICATORS.values():
                        if indicator in df.columns:
                            try:
                                pre_mean = country_pre[indicator].mean()
                                during_mean = country_during[indicator].mean()
                                change = ((during_mean - pre_mean) / pre_mean) * 100 if pre_mean != 0 else 0
                                
                                results.append({
                                    'War': war,
                                    'Country': country_name,
                                    'Country Code': country,
                                    'Indicator': indicator,
                                    'Pre-War Mean': pre_mean,
                                    'During-War Mean': during_mean,
                                    '% Change': change
                                })
                            except Exception as e:
                                st.warning(f"Error processing {indicator} for {country}: {e}")
    
    if not results:
        st.error("No valid war impact comparisons could be made")
        st.stop()
        
    return pd.DataFrame(results)

# Visualization Functions
def plot_gdp_trends(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for country in WAR_COUNTRIES:
        if country in df['country_code'].unique():
            country_data = df[df['country_code'] == country]
            if not country_data.empty and 'GDP (current US$)' in country_data.columns:
                ax.plot(country_data['year'], country_data['GDP (current US$)'],
                       label=country_data['country'].iloc[0])
    
    ax.set_title('GDP Trends in War-Affected Countries', fontsize=16)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('GDP (current US$)', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

def plot_cpi_trends(df):
    plot_data = df[df['country_code'].isin(WAR_COUNTRIES) & 
                df['Consumer price index (2010 = 100)'].notna()].copy()
    
    if not plot_data.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        for code in WAR_COUNTRIES:
            sub_data = plot_data[plot_data['country_code'] == code]
            if not sub_data.empty:
                ax.plot(sub_data['year'], sub_data['Consumer price index (2010 = 100)'], 
                       label=sub_data['country'].iloc[0])
        
        ax.set_title('Consumer Price Index in War-Affected Countries', fontsize=16)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('CPI (2010 = 100)', fontsize=14)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)

def plot_gdp_per_capita_change(analysis_df):
    gdp_pc_data = analysis_df[analysis_df['Indicator'] == 'GDP per capita (current US$)'].copy()
    
    if not gdp_pc_data.empty:
        gdp_pc_data = gdp_pc_data.dropna(subset=['% Change'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=gdp_pc_data, x='Country', y='% Change', hue='War', ax=ax)
        ax.set_title('GDP per Capita Change During Wars', fontsize=16)
        ax.set_ylabel('% Change from Pre-War Period', fontsize=14)
        ax.set_xlabel('Country', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)

def plot_trade_balance_comparison(df):
    countries = ['RU', 'US']
    plot_data = df[df['country_code'].isin(countries) & df['Trade Balance'].notna()].copy()
    
    if not plot_data.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        for code in countries:
            sub_data = plot_data[plot_data['country_code'] == code]
            if not sub_data.empty:
                ax.plot(sub_data['year'], sub_data['Trade Balance'], 
                       label=sub_data['country'].iloc[0])
        
        ax.set_title('Trade Balance Over Time: Russia vs USA', fontsize=16)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Trade Balance (US$)', fontsize=14)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)

def plot_exports_change(analysis_df):
    exports_data = analysis_df[analysis_df['Indicator'] == 'Exports of goods and services (current US$)'].copy()
    
    if not exports_data.empty:
        exports_data = exports_data.dropna(subset=['% Change'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=exports_data, x='Country', y='% Change', hue='War', ax=ax)
        ax.set_title('Change in Exports During War Periods', fontsize=16)
        ax.set_ylabel('% Change from Pre-War Period', fontsize=14)
        ax.set_xlabel('Country', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)

def plot_gdp_per_capita_trends(df):
    countries_to_plot = ['SY', 'IQ', 'UA', 'YE', 'US', 'DE', 'RU']
    plot_data = df[df['country_code'].isin(countries_to_plot) & 
                df['GDP per capita (current US$)'].notna()].copy()
    
    if not plot_data.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        for code in countries_to_plot:
            sub_data = plot_data[plot_data['country_code'] == code]
            if not sub_data.empty:
                ax.plot(sub_data['year'], sub_data['GDP per capita (current US$)'], 
                       label=sub_data['country'].iloc[0])
        
        ax.set_title('GDP per Capita Trends (War-Affected vs. Global Powers)', fontsize=16)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('GDP per Capita (US$)', fontsize=14)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)

def plot_unemployment_change(analysis_df):
    unemployment_data = analysis_df[analysis_df['Indicator'] == 'Unemployment, total (% of total labor force)'].copy()
    
    if not unemployment_data.empty:
        unemployment_data = unemployment_data.dropna(subset=['% Change'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=unemployment_data, x='Country', y='% Change', hue='War', ax=ax)
        ax.set_title('Change in Unemployment During War Periods', fontsize=16)
        ax.set_ylabel('% Change from Pre-War Period', fontsize=14)
        ax.set_xlabel('Country', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)

def plot_egypt_trade_balance(df):
    if 'EG' in df['country_code'].unique() and 'Trade Balance' in df.columns:
        egypt_data = df[df['country_code'] == 'EG'].copy()
        egypt_data = egypt_data.dropna(subset=['Trade Balance'])
        
        if not egypt_data.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(egypt_data['year'], egypt_data['Trade Balance'], 
                   marker='o', color='purple')
            ax.set_title("Egypt's Trade Balance Over Time", fontsize=16)
            ax.set_xlabel('Year', fontsize=14)
            ax.set_ylabel('Trade Balance (US$)', fontsize=14)
            ax.grid(True)
            plt.tight_layout()
            st.pyplot(fig)

def plot_egypt_cpi_unemployment(df):
    if 'EG' in df['country_code'].unique():
        egypt_data = df[df['country_code'] == 'EG'].copy()
        indicators = ['Consumer price index (2010 = 100)', 
                     'Unemployment, total (% of total labor force)']
        available = [ind for ind in indicators if ind in egypt_data.columns]
        
        if available:
            fig, ax = plt.subplots(figsize=(10, 6))
            for ind in available:
                sub = egypt_data[['year', ind]].dropna()
                ax.plot(sub['year'], sub[ind], label=ind)
            
            ax.set_title("Egypt: CPI vs. Unemployment Over Time", fontsize=16)
            ax.set_xlabel('Year', fontsize=14)
            ax.set_ylabel('Value', fontsize=14)
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            st.pyplot(fig)

# Main App
def main():
    st.title('⚔️ DataTools Wars')
    st.header('Economic Impact Analysis of Modern Conflicts')
    
    # Data Loading Section
    with st.expander("📊 Data Loading", expanded=True):
        try:
            df = get_all_indicators()
            clean_df = clean_data(df)
            st.success(f"✅ Data loaded successfully for countries: {', '.join(clean_df['country'].unique())}")
            
            if st.checkbox("Show raw data"):
                st.dataframe(clean_df)
                
        except Exception as e:
            st.error(f"❌ Failed to load data: {str(e)}")
            st.stop()
    
    # Analysis Section
    with st.expander("📈 War Impact Analysis", expanded=True):
        try:
            analysis_df = analyze_war_impact(clean_df)
            st.success("✅ Analysis completed successfully!")
            
            # Show analysis results
            st.subheader("Key Metrics Change During Wars")
            st.dataframe(analysis_df.sort_values('% Change', ascending=False))
            
            # Visualizations in tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "GDP Analysis", 
                "Trade Analysis", 
                "Social Indicators", 
                "Country Focus"
            ])
            
            with tab1:
                st.subheader("GDP Trends")
                col1, col2 = st.columns(2)
                with col1:
                    plot_gdp_trends(clean_df)
                with col2:
                    plot_gdp_per_capita_change(analysis_df)
                
                st.subheader("GDP per Capita Comparison")
                plot_gdp_per_capita_trends(clean_df)
                
            with tab2:
                st.subheader("Trade Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    plot_trade_balance_comparison(clean_df)
                with col2:
                    plot_exports_change(analysis_df)
                
            with tab3:
                st.subheader("Social Indicators")
                col1, col2 = st.columns(2)
                with col1:
                    plot_cpi_trends(clean_df)
                with col2:
                    plot_unemployment_change(analysis_df)
                
            with tab4:
                st.subheader("Egypt Focus")
                col1, col2 = st.columns(2)
                with col1:
                    plot_egypt_trade_balance(clean_df)
                with col2:
                    plot_egypt_cpi_unemployment(clean_df)
                
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
    
    # Export Section
    with st.expander("💾 Export Results"):
        if st.button("Export Data to CSV"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_df.to_csv(f'war_economic_data_{timestamp}.csv', index=False)
            analysis_df.to_csv(f'war_impact_comparison_{timestamp}.csv', index=False)
            st.success("✅ Data exported successfully!")

if __name__ == "__main__":
    main()