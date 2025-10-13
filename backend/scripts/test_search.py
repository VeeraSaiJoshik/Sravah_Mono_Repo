import sys
sys.path.append('..')

from database.search import search_projects

def test_search():
    """Test various search queries."""
    
    test_queries = [
        "sentiment dashboard",
        "widget blank",
        "ML API",
        "customer feedback",
        "emoji edge case"
    ]
    
    print("🔍 Testing Search Functionality")
    print("="*70)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-"*70)
        
        try:
            results = search_projects(query, limit=3)
            
            if not results:
                print("   ❌ No results found")
                continue
            
            for i, result in enumerate(results, 1):
                print(f"\n   {i}. {result['name']}")
                print(f"      ID: {result['id']}")
                print(f"      Score: {result['score']:.4f}")
                print(f"      Description: {result['description'][:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Test complete!")


if __name__ == "__main__":
    test_search()