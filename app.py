"""
CRYPTO vs M2 LIQUIDITY ANALYZER - WEB APP
==========================================
Streamlit web application for analyzing crypto/M2 correlation with lag analysis
Deploy to Streamlit Cloud for free public access
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import requests
from io import StringIO
import base64

# Page config
st.set_page_config(
    page_title="Crypto vs M2 Liquidity Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class CryptoM2Analyzer:
    """Main analyzer class"""
    
    def __init__(self):
        self.crypto_data = None
        self.m2_data = None
    
    def fetch_crypto_coingecko(self):
        """Fetch crypto market cap from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {"vs_currency": "usd", "days": "max", "interval": "daily"}
            
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                market_caps = data.get('market_caps', [])
                
                df = pd.DataFrame(market_caps, columns=['timestamp', 'btc_market_cap'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['market_cap_billions'] = (df['btc_market_cap'] / 1e9) * 1.75
                
                return df[['date', 'market_cap_billions']]
        except:
            return None
    
    def fetch_m2_fred(self):
        """Fetch M2 from FRED"""
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
            params = {"id": "M2SL", "cosd": "2013-01-01"}
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                df.columns = ['date', 'm2_billions']
                df['date'] = pd.to_datetime(df['date'])
                df['m2_billions'] = pd.to_numeric(df['m2_billions'], errors='coerce')
                return df.dropna()
        except:
            return None
    
    def calculate_m2_zscore(self, df, window=90):
        """Calculate M2 Z-Score"""
        df = df.set_index('date').resample('D').interpolate().reset_index()
        df['m2_pct_change_3m'] = df['m2_billions'].pct_change(periods=window) * 100
        
        rolling_mean = df['m2_pct_change_3m'].rolling(window=252, min_periods=90).mean()
        rolling_std = df['m2_pct_change_3m'].rolling(window=252, min_periods=90).std()
        
        df['m2_zscore'] = (df['m2_pct_change_3m'] - rolling_mean) / rolling_std
        df['m2_zscore'] = df['m2_zscore'].fillna(0)
        
        return df
    
    def analyze_lag(self, crypto_df, m2_df, max_lag_weeks=20):
        """Analyze optimal lag"""
        merged = pd.merge(crypto_df, m2_df[['date', 'm2_zscore']], on='date', how='inner')
        merged = merged.dropna().sort_values('date')
        
        correlations = []
        for lag_weeks in range(0, max_lag_weeks + 1):
            lag_days = lag_weeks * 7
            test_df = merged.copy()
            test_df['m2_zscore_shifted'] = test_df['m2_zscore'].shift(lag_days)
            test_df = test_df.dropna()
            
            if len(test_df) > 30:
                corr = test_df['market_cap_billions'].corr(test_df['m2_zscore_shifted'])
                correlations.append((lag_weeks, corr))
        
        best_lag, best_corr = max(correlations, key=lambda x: abs(x[1]))
        return best_lag, best_corr, correlations
    
    def process_uploaded_data(self, crypto_file, m2_file):
        """Process uploaded CSV files"""
        try:
            # Read crypto data
            crypto_df = pd.read_csv(crypto_file)
            crypto_df.columns = [c.lower().strip() for c in crypto_df.columns]
            
            # Try to find date and value columns
            date_col = [c for c in crypto_df.columns if 'date' in c or 'time' in c][0]
            value_cols = [c for c in crypto_df.columns if 'market' in c or 'cap' in c or 'value' in c or 'price' in c]
            value_col = value_cols[0] if value_cols else crypto_df.columns[1]
            
            crypto_df = crypto_df[[date_col, value_col]].copy()
            crypto_df.columns = ['date', 'market_cap_billions']
            crypto_df['date'] = pd.to_datetime(crypto_df['date'])
            crypto_df['market_cap_billions'] = pd.to_numeric(crypto_df['market_cap_billions'], errors='coerce')
            
            # Read M2 data
            m2_df = pd.read_csv(m2_file)
            m2_df.columns = [c.lower().strip() for c in m2_df.columns]
            
            date_col = [c for c in m2_df.columns if 'date' in c or 'time' in c][0]
            value_cols = [c for c in m2_df.columns if 'm2' in c or 'value' in c or 'supply' in c]
            value_col = value_cols[0] if value_cols else m2_df.columns[1]
            
            m2_df = m2_df[[date_col, value_col]].copy()
            m2_df.columns = ['date', 'm2_billions']
            m2_df['date'] = pd.to_datetime(m2_df['date'])
            m2_df['m2_billions'] = pd.to_numeric(m2_df['m2_billions'], errors='coerce')
            
            return crypto_df.dropna(), m2_df.dropna()
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            return None, None

def create_chart(crypto_df, m2_df, lag_weeks, correlation):
    """Create the main chart with LARGE clean zones"""
    merged = pd.merge(crypto_df, m2_df[['date', 'm2_zscore']], on='date', how='inner').dropna()
    
    lag_days = lag_weeks * 7
    merged['m2_zscore_lagged'] = merged['m2_zscore'].shift(lag_days)
    merged = merged.dropna()
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12), 
                                    gridspec_kw={'height_ratios': [2.5, 1], 'hspace': 0.08})
    
    # ============================================
    # SMOOTH M2 for CLEAN ZONES (not daily noise!)
    # ============================================
    merged['m2_smooth'] = merged['m2_zscore_lagged'].rolling(window=90, min_periods=1).mean()
    
    # Identify expansion/contraction zones based on SMOOTHED M2
    positive_zones = []
    negative_zones = []
    
    current_zone_start = None
    current_zone_positive = None
    
    for i in range(len(merged)):
        is_positive = merged.iloc[i]['m2_smooth'] > 0
        
        if current_zone_start is None:
            current_zone_start = merged.iloc[i]['date']
            current_zone_positive = is_positive
        elif is_positive != current_zone_positive:
            zone_end = merged.iloc[i-1]['date']
            if current_zone_positive:
                positive_zones.append((current_zone_start, zone_end))
            else:
                negative_zones.append((current_zone_start, zone_end))
            
            current_zone_start = merged.iloc[i]['date']
            current_zone_positive = is_positive
    
    # Add last zone
    if current_zone_start is not None:
        zone_end = merged.iloc[-1]['date']
        if current_zone_positive:
            positive_zones.append((current_zone_start, zone_end))
        else:
            negative_zones.append((current_zone_start, zone_end))
    
    # Plot LARGE background zones on both charts
    for start, end in positive_zones:
        ax1.axvspan(start, end, alpha=0.25, color='#4CAF50', zorder=0)
        ax2.axvspan(start, end, alpha=0.25, color='#4CAF50', zorder=0)
    
    for start, end in negative_zones:
        ax1.axvspan(start, end, alpha=0.25, color='#F44336', zorder=0)
        ax2.axvspan(start, end, alpha=0.25, color='#F44336', zorder=0)
    
    # ============================================
    # TOP CHART: Crypto Market Cap
    # ============================================
    ax1.plot(merged['date'], merged['market_cap_billions'],
            color='white', linewidth=3, label='Total Crypto Market Cap', zorder=5)
    
    ax1.set_ylabel('Market Cap (Billions USD)', fontsize=16, fontweight='bold', color='white')
    ax1.set_title(f'Total Crypto Market Cap vs M2 Liquidity Zones\nM2 LEADS by ~{lag_weeks} weeks | Correlation: {correlation:.3f}',
                 fontsize=18, fontweight='bold', pad=20, color='white')
    
    ax1.grid(True, alpha=0.1, color='gray', linestyle='-', linewidth=0.5)
    ax1.set_facecolor('#0a0a0a')
    ax1.legend(loc='upper left', fontsize=13, framealpha=0.95)
    ax1.tick_params(axis='x', labelbottom=False)
    
    # ============================================
    # BOTTOM CHART: M2 Z-Score bars (BIGGER!)
    # ============================================
    positive = merged['m2_zscore_lagged'] >= 0
    
    # Use WIDER bars
    bar_width = 5
    
    ax2.bar(merged[positive]['date'], merged[positive]['m2_zscore_lagged'],
           color='#4CAF50', alpha=0.95, width=bar_width, label='M2 Expansion', zorder=5, edgecolor='none')
    ax2.bar(merged[~positive]['date'], merged[~positive]['m2_zscore_lagged'],
           color='#F44336', alpha=0.95, width=bar_width, label='M2 Contraction', zorder=5, edgecolor='none')
    
    ax2.axhline(y=0, color='white', linestyle='-', linewidth=1.5, alpha=0.7, zorder=4)
    
    ax2.set_ylabel(f'M2 Z-Score\n(+{lag_weeks}w lead)', fontsize=15, fontweight='bold', color='white')
    ax2.set_xlabel('Year', fontsize=15, fontweight='bold', color='white')
    
    ax2.grid(True, alpha=0.1, color='gray', linestyle='-', linewidth=0.5)
    ax2.set_facecolor('#0a0a0a')
    ax2.legend(loc='upper left', fontsize=12, framealpha=0.95)
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.tick_params(colors='white', labelsize=12)
        for spine in ax.spines.values():
            spine.set_color('#333333')
            spine.set_linewidth(1.5)
    
    fig.patch.set_facecolor('#1a1a1a')
    plt.tight_layout()
    
    return fig

def main():
    """Main app"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Crypto vs M2 Liquidity Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze the correlation between crypto market cap and global liquidity with lag analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    data_source = st.sidebar.radio(
        "Data Source:",
        ["Fetch from APIs (Auto)", "Upload CSV Files"]
    )
    
    if data_source == "Upload CSV Files":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📁 Upload Data")
        st.sidebar.info("Upload CSV files with Date and Value columns")
        
        crypto_file = st.sidebar.file_uploader("Crypto Market Cap CSV", type=['csv'])
        m2_file = st.sidebar.file_uploader("M2 Data CSV", type=['csv'])
    
    max_lag = st.sidebar.slider("Max Lag Analysis (weeks)", 5, 30, 20)
    zscore_window = st.sidebar.slider("Z-Score Window (days)", 60, 180, 90)
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    analyzer = CryptoM2Analyzer()
    
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing data..."):
            
            # Get data
            if data_source == "Fetch from APIs (Auto)":
                crypto_df = analyzer.fetch_crypto_coingecko()
                m2_df = analyzer.fetch_m2_fred()
                
                if crypto_df is None or m2_df is None:
                    st.error("❌ Failed to fetch data from APIs. Try uploading CSV files instead.")
                    return
                    
            else:
                if crypto_file is None or m2_file is None:
                    st.warning("⚠️ Please upload both CSV files")
                    return
                
                crypto_df, m2_df = analyzer.process_uploaded_data(crypto_file, m2_file)
                if crypto_df is None or m2_df is None:
                    return
            
            # Calculate Z-Score
            m2_df = analyzer.calculate_m2_zscore(m2_df, window=zscore_window)
            
            # Analyze lag
            best_lag, best_corr, all_corr = analyzer.analyze_lag(crypto_df, m2_df, max_lag)
            
            # Display metrics
            col1.metric("📈 Best Lag", f"{best_lag} weeks", "Optimal delay")
            col2.metric("🔗 Correlation", f"{best_corr:.3f}", "At optimal lag")
            col3.metric("📊 Data Points", f"{len(crypto_df):,}", "Total records")
            
            st.markdown("---")
            
            # Main insight
            st.success(f"""
            ### 💡 Key Finding
            
            **M2 liquidity changes LEAD crypto market movements by approximately {best_lag} weeks.**
            
            When global M2 liquidity increases, the crypto market typically follows with a **{best_lag}-week delay**, 
            with a correlation of **{best_corr:.3f}**.
            """)
            
            # Create chart
            fig = create_chart(crypto_df, m2_df, best_lag, best_corr)
            st.pyplot(fig)
            
            # Lag correlation chart
            st.markdown("---")
            st.subheader("📉 Correlation vs Lag Analysis")
            
            lag_df = pd.DataFrame(all_corr, columns=['Lag (weeks)', 'Correlation'])
            
            fig2, ax = plt.subplots(figsize=(12, 5))
            ax.plot(lag_df['Lag (weeks)'], lag_df['Correlation'], 
                   marker='o', linewidth=2, markersize=6, color='#4CAF50')
            ax.axvline(x=best_lag, color='red', linestyle='--', linewidth=2, 
                      label=f'Optimal Lag: {best_lag} weeks')
            ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
            ax.set_xlabel('Lag (weeks)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Correlation', fontsize=12, fontweight='bold')
            ax.set_title('How Correlation Changes with Different Lags', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=11)
            fig2.patch.set_facecolor('#1a1a1a')
            ax.set_facecolor('#0a0a0a')
            plt.tight_layout()
            
            st.pyplot(fig2)
            
            # Download section
            st.markdown("---")
            st.subheader("💾 Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download data
                result_df = pd.merge(crypto_df, m2_df[['date', 'm2_zscore']], on='date', how='inner')
                csv = result_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Data (CSV)",
                    csv,
                    "crypto_m2_analysis.csv",
                    "text/csv"
                )
            
            with col2:
                st.info(f"""
                **Analysis Summary:**
                - Optimal Lag: {best_lag} weeks
                - Correlation: {best_corr:.3f}
                - Period: {crypto_df['date'].min().date()} to {crypto_df['date'].max().date()}
                """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Built with ❤️ using Streamlit | Data sources: CoinGecko & FRED</p>
        <p style='font-size: 0.8em;'>Tip: When M2 liquidity increases, watch for crypto pumps in the following weeks!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
