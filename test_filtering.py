#!/usr/bin/env python3
"""
Test filtering functionality
"""

import requests
import time

def test_filtering():
    print("Testing Mandi Prices Filtering")
    print("=" * 50)
    
    # Wait for backend to start
    time.sleep(3)
    
    base_url = "http://localhost:5000/api/mandi-prices"
    
    try:
        # Test 1: No filters - should get diverse data
        print("1. Testing NO FILTERS (should get diverse data from multiple states)")
        r = requests.get(base_url)
        if r.status_code == 200:
            data = r.json()
            states = set(item['state'] for item in data['prices'])
            print(f"   Records: {len(data['prices'])}")
            print(f"   States: {sorted(states)}")
            print(f"   Source: {data['source']}")
            if len(states) > 1:
                print("   [PASS] Getting diverse data from multiple states")
            else:
                print("   [WARN] Only getting data from one state")
        else:
            print(f"   [FAIL] Error: {r.status_code}")
        
        print()
        
        # Test 2: State filter
        print("2. Testing STATE FILTER (Karnataka)")
        r = requests.get(f"{base_url}?state=Karnataka")
        if r.status_code == 200:
            data = r.json()
            states = set(item['state'] for item in data['prices'])
            print(f"   Records: {len(data['prices'])}")
            print(f"   States: {sorted(states)}")
            print(f"   Source: {data['source']}")
            if states == {'Karnataka'}:
                print("   [PASS] State filtering working correctly")
            else:
                print("   [FAIL] State filtering not working - got other states")
        else:
            print(f"   [FAIL] Error: {r.status_code}")
        
        print()
        
        # Test 3: Different state filter
        print("3. Testing STATE FILTER (Punjab)")
        r = requests.get(f"{base_url}?state=Punjab")
        if r.status_code == 200:
            data = r.json()
            states = set(item['state'] for item in data['prices'])
            print(f"   Records: {len(data['prices'])}")
            print(f"   States: {sorted(states)}")
            print(f"   Source: {data['source']}")
            if states == {'Punjab'}:
                print("   [PASS] Punjab state filtering working correctly")
            else:
                print("   [FAIL] Punjab state filtering not working")
        else:
            print(f"   [FAIL] Error: {r.status_code}")
        
        print()
        
        # Test 4: Commodity filter
        print("4. Testing COMMODITY FILTER (Rice)")
        r = requests.get(f"{base_url}?commodity=Rice")
        if r.status_code == 200:
            data = r.json()
            commodities = set(item['name'] for item in data['prices'])
            print(f"   Records: {len(data['prices'])}")
            print(f"   Commodities: {sorted(commodities)}")
            print(f"   Source: {data['source']}")
            if 'Rice' in commodities and len(commodities) == 1:
                print("   [PASS] Commodity filtering working correctly")
            else:
                print("   [FAIL] Commodity filtering not working correctly")
        else:
            print(f"   [FAIL] Error: {r.status_code}")
        
        print()
        
        # Test 5: Combined filters
        print("5. Testing COMBINED FILTERS (Karnataka + Rice)")
        r = requests.get(f"{base_url}?state=Karnataka&commodity=Rice")
        if r.status_code == 200:
            data = r.json()
            states = set(item['state'] for item in data['prices'])
            commodities = set(item['name'] for item in data['prices'])
            print(f"   Records: {len(data['prices'])}")
            print(f"   States: {sorted(states)}")
            print(f"   Commodities: {sorted(commodities)}")
            print(f"   Source: {data['source']}")
            if states == {'Karnataka'} and 'Rice' in commodities:
                print("   [PASS] Combined filtering working correctly")
            else:
                print("   [FAIL] Combined filtering not working correctly")
        else:
            print(f"   [FAIL] Error: {r.status_code}")
        
        print()
        print("=" * 50)
        print("Filtering Test Complete!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_filtering()

