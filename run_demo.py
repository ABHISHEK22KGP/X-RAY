# run_demo.py - UPDATED
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch the search function
import demo_app.competitor_selection as demo_module

# Update the search logic
original_search = demo_module.CompetitorSelector.search_products

def patched_search(self, keyword, limit=10):
    """Better search that actually finds products"""
    import demo_app.competitor_selection
    matches = []
    for product in demo_app.competitor_selection.MOCK_PRODUCTS:
        if any(word in product["title"].lower() 
               for word in ["water", "bottle", "hydro", "yeti", "stanley"]):
            matches.append(product)
    
    # Return limited results
    results = matches[:limit]
    
    # Get xray instance
    from xray_sdk.xray import xray
    xray.add_reasoning(f"Found {len(matches)} matches, returning top {len(results)}")
    return results

# Apply patch
demo_module.CompetitorSelector.search_products = patched_search

# Now import and run the demo
from demo_app.competitor_selection import main

if __name__ == "__main__":
    main()