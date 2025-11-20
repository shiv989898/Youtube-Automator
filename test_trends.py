"""Test script to check if Google Trends is working"""
import random
from pytrends.request import TrendReq

print("=" * 60)
print("TESTING GOOGLE TRENDS API")
print("=" * 60)

try:
    print("\n1. Initializing pytrends with relaxed settings...")
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.5)
    print("✅ PyTrends initialized successfully")
    
    # Method 1: Trending searches
    print("\n2. Trying trending_searches() for United States...")
    try:
        trending_searches_df = pytrends.trending_searches(pn='united_states')
        if not trending_searches_df.empty:
            topics = trending_searches_df[0].head(10).tolist()
            print(f"✅ SUCCESS! Found {len(topics)} trending searches:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
        else:
            print("⚠️ Empty dataframe returned")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Method 2: Today's searches
    print("\n3. Trying today_searches() for US...")
    try:
        daily_trends = pytrends.today_searches(pn='US')
        if not daily_trends.empty:
            topics = daily_trends[0].head(10).tolist()
            print(f"✅ SUCCESS! Found {len(topics)} daily trends:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
        else:
            print("⚠️ Empty dataframe returned")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Method 3: Related queries
    print("\n4. Trying related_queries() for 'science'...")
    try:
        pytrends.build_payload(['science'], timeframe='now 7-d', geo='US')
        related = pytrends.related_queries()
        if 'science' in related and related['science']['top'] is not None:
            topics = related['science']['top']['query'].head(10).tolist()
            print(f"✅ SUCCESS! Found {len(topics)} related queries:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
        else:
            print("⚠️ No related queries found")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Method 4: Interest over time
    print("\n5. Trying interest_over_time() for popular topics...")
    try:
        keywords = ['artificial intelligence', 'space', 'technology']
        pytrends.build_payload(keywords, timeframe='now 1-d', geo='US')
        interest_df = pytrends.interest_over_time()
        if not interest_df.empty:
            print(f"✅ SUCCESS! Got interest data for {len(keywords)} keywords:")
            for keyword in keywords:
                if keyword in interest_df.columns:
                    avg_interest = interest_df[keyword].mean()
                    print(f"   - {keyword}: avg interest = {avg_interest:.1f}")
        else:
            print("⚠️ Empty interest data")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    print("\nThis means Google Trends API is not accessible.")
    print("Possible reasons:")
    print("- Google is blocking requests (rate limit)")
    print("- Network/firewall issues")
    print("- API endpoint changed")
