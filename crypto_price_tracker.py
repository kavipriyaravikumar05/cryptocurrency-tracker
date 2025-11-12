# crypto_tracker.py
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def setup_driver():
    """Setup Chrome browser in headless mode"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_crypto_prices():
    """Scrape top 10 cryptocurrency prices from CoinMarketCap"""
    driver = setup_driver()
    crypto_data = []
    
    try:
        print("🔄 Loading CoinMarketCap...")
        driver.get("https://coinmarketcap.com/")
        
        wait = WebDriverWait(driver, 15)
        
        # Accept cookies if present
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_button.click()
            print("✅ Cookies accepted")
            time.sleep(2)
        except:
            print("ℹ️ No cookie banner found")
        
        # Wait for table and load data
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.cmc-table")))
        time.sleep(3)
        
        # Get top 10 coins
        rows = driver.find_elements(By.CSS_SELECTOR, "table.cmc-table tbody tr")
        
        print(f"📊 Found {len(rows)} cryptocurrencies, extracting top 10...")
        
        for i, row in enumerate(rows[:10], 1):
            try:
                # Extract data using text content (most reliable method)
                row_data = row.text.split('\n')
                
                if len(row_data) >= 6:
                    coin_info = {
                        'Rank': i,
                        'Name': row_data[1],
                        'Symbol': row_data[2],
                        'Price': row_data[3],
                        '24h_Change': row_data[4],
                        'Market_Cap': row_data[5] if len(row_data) > 5 else "N/A",
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    crypto_data.append(coin_info)
                    print(f"✅ {i}. {coin_info['Name']} - ${coin_info['Price']} ({coin_info['24h_Change']})")
                    
            except Exception as e:
                print(f"❌ Error with coin {i}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Scraping error: {e}")
    finally:
        driver.quit()
    
    return crypto_data

def save_to_csv(data, filename="crypto_prices.csv"):
    """Save data to CSV file"""
    if not data:
        print("❌ No data to save!")
        return False
    
    df = pd.DataFrame(data)
    
    try:
        # Append to existing file or create new
        try:
            existing_df = pd.read_csv(filename)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(filename, index=False)
            print(f"📁 Data appended to {filename}")
        except FileNotFoundError:
            df.to_csv(filename, index=False)
            print(f"📁 New file created: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return False

def display_data(data):
    """Display data in formatted table"""
    if not data:
        print("❌ No data to display!")
        return
    
    print("\n" + "="*80)
    print("🎯 TOP 10 CRYPTOCURRENCIES - LIVE PRICES")
    print("="*80)
    print(f"{'Rank':<4} {'Name':<15} {'Price':<15} {'24h Change':<12} {'Market Cap':<20}")
    print("-"*80)
    
    for coin in data:
        change = coin['24h_Change']
        if change.startswith('+'):
            change_display = f"🟢 {change}"
        elif change.startswith('-'):
            change_display = f"🔴 {change}"
        else:
            change_display = f"⚪ {change}"
            
        print(f"{coin['Rank']:<4} {coin['Name']:<15} {coin['Price']:<15} {change_display:<12} {coin['Market_Cap']:<20}")

def analyze_data(data):
    """Analyze and filter cryptocurrency data"""
    if not data:
        return
    
    print("\n🔍 QUICK ANALYSIS")
    print("-" * 40)
    
    # Count gainers and losers
    gainers = [coin for coin in data if coin['24h_Change'].startswith('+')]
    losers = [coin for coin in data if coin['24h_Change'].startswith('-')]
    
    print(f"📈 Gainers: {len(gainers)} coins")
    print(f"📉 Losers: {len(losers)} coins")
    
    # Show top gainer
    if gainers:
        top_gainer = max(gainers, key=lambda x: float(x['24h_Change'].replace('+', '').replace('%', '')))
        print(f"🏆 Top Gainer: {top_gainer['Name']} ({top_gainer['24h_Change']})")
    
    # Show top loser
    if losers:
        top_loser = min(losers, key=lambda x: float(x['24h_Change'].replace('-', '').replace('%', '')))
        print(f"💥 Top Loser: {top_loser['Name']} ({top_loser['24h_Change']})")

def main():
    """Main function to run the cryptocurrency tracker"""
    print("🚀 CRYPTO TRACKER - TOP 10 COINS")
    print("=" * 50)
    
    # Scrape data
    crypto_data = scrape_crypto_prices()
    
    if crypto_data:
        # Display data
        display_data(crypto_data)
        
        # Save to CSV
        save_to_csv(crypto_data)
        
        # Show analysis
        analyze_data(crypto_data)
        
        print(f"\n⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💡 Run again to update prices!")
        
    else:
        print("❌ Failed to fetch data. Please try again.")

if __name__ == "__main__":
    main()