"""
Demo: Competitor Product Selection System with X-Ray Debugging
"""

import random
import time
from xray_sdk.xray import xray

# Mock product data
MOCK_PRODUCTS = [
    {"id": "B001", "title": "HydroFlask 32oz Water Bottle", "price": 44.99, "rating": 4.5, "reviews": 8932},
    {"id": "B002", "title": "Yeti Rambler 26oz Bottle", "price": 34.99, "rating": 4.4, "reviews": 5621},
    {"id": "B003", "title": "Stanley Adventure Quencher", "price": 45.00, "rating": 4.3, "reviews": 4102},
    {"id": "B004", "title": "Generic Water Bottle", "price": 8.99, "rating": 3.2, "reviews": 45},
    {"id": "B005", "title": "Nalgene 32oz Bottle", "price": 12.99, "rating": 4.0, "reviews": 12500},
    {"id": "B006", "title": "Simple Modern Tumbler", "price": 24.99, "rating": 4.1, "reviews": 4200},
    {"id": "B007", "title": "Premium Titanium Bottle", "price": 89.00, "rating": 4.8, "reviews": 234},
    {"id": "B008", "title": "Contigo Autoseal 32oz", "price": 21.99, "rating": 4.0, "reviews": 2100},
    {"id": "B009", "title": "Replacement Bottle Lid", "price": 9.99, "rating": 3.8, "reviews": 120},
    {"id": "B010", "title": "Water Bottle Brush", "price": 12.99, "rating": 4.6, "reviews": 3421},
]

class CompetitorSelector:
    """Find competitor products for a given product"""
    
    @xray.trace(name="Generate Search Keywords", step_type="llm")
    def generate_keywords(self, product_title):
        """Step 1: Generate search keywords from product title"""
        # Simulate LLM processing time
        time.sleep(0.05)
        
        # Generate keywords based on title
        words = product_title.lower().split()
        keywords = []
        
        # Strategy 1: Full title
        keywords.append(product_title)
        
        # Strategy 2: Key attributes
        key_terms = []
        if "stainless" in words:
            key_terms.append("stainless steel")
        if "insulated" in words:
            key_terms.append("insulated")
        if "water" in words and "bottle" in words:
            key_terms.append("water bottle")
        if "32oz" in product_title or "32 oz" in product_title:
            key_terms.append("32oz")
            
        if key_terms:
            keywords.append(" ".join(key_terms))
        
        # Strategy 3: Simplified version
        simple_title = " ".join(words[:4])  # First 4 words
        keywords.append(simple_title)
        
        # Remove duplicates
        unique_keywords = []
        seen = set()
        for kw in keywords:
            if kw and kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        # Add reasoning BEFORE returning
        xray.add_reasoning(
            f"Generated {len(unique_keywords)} keywords from title: '{product_title}'. "
            f"Extracted key terms: {', '.join(key_terms) if key_terms else 'None'}"
        )
        
        return unique_keywords
    
    @xray.trace(name="Search Products", step_type="search")
    def search_products(self, keyword, limit=10):
        """Step 2: Search for products using keyword"""
        # Simulate API call latency
        time.sleep(0.08)
        
        matches = []
        keyword_lower = keyword.lower()
        
        for product in MOCK_PRODUCTS:
            title_lower = product["title"].lower()
            product_words = set(title_lower.split())
            keyword_words = set(keyword_lower.split())
            
            # Calculate match score
            common_words = product_words.intersection(keyword_words)
            match_score = len(common_words)
            
            # Bonus for exact phrase match
            if keyword_lower in title_lower:
                match_score += 2
            
            if match_score >= 1:  # At least one word matches
                product_copy = product.copy()
                product_copy["match_score"] = match_score
                matches.append(product_copy)
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Remove match_score from final results
        results = []
        for match in matches[:limit]:
            result = match.copy()
            result.pop("match_score", None)
            results.append(result)
        
        total_matches = len(matches)
        returned_count = len(results)
        
        # Add reasoning BEFORE returning
        xray.add_reasoning(
            f"Searched for '{keyword}'. Found {total_matches} total matches, "
            f"returning top {returned_count} by relevance. "
            f"Best match: '{results[0]['title'] if results else 'None'}'"
        )
        
        return results
    
    @xray.trace(name="Apply Filters", step_type="filter")
    def apply_filters(self, products, reference_price, min_rating=3.8, min_reviews=100):
        """Step 3: Apply business filters to candidate products"""
        # Simulate processing time
        time.sleep(0.06)
        
        filtered = []
        evaluations = []
        detailed_evaluations = []
        
        min_price = reference_price * 0.5
        max_price = reference_price * 2.0
        
        # Convert to float for safety
        min_price = float(min_price)
        max_price = float(max_price)
        min_rating = float(min_rating)
        min_reviews = int(min_reviews)
        
        for product in products:
            # Get product values
            price = float(product["price"])
            rating = float(product["rating"])
            reviews = int(product["reviews"])
            
            # Check each filter
            price_ok = min_price <= price <= max_price
            rating_ok = rating >= min_rating
            reviews_ok = reviews >= min_reviews
            
            passed = price_ok and rating_ok and reviews_ok
            
            # Create evaluation record
            eval_record = {
                "product_id": product["id"],
                "product_title": product["title"],
                "price": price,
                "rating": rating,
                "reviews": reviews,
                "filter_results": {
                    "price_range": {
                        "passed": price_ok,
                        "min": min_price,
                        "max": max_price,
                        "value": price,
                        "detail": f"${price:.2f} is within ${min_price:.2f}-${max_price:.2f}" if price_ok 
                                 else f"${price:.2f} is outside ${min_price:.2f}-${max_price:.2f}"
                    },
                    "min_rating": {
                        "passed": rating_ok,
                        "threshold": min_rating,
                        "value": rating,
                        "detail": f"{rating:.1f} >= {min_rating}" if rating_ok 
                                 else f"{rating:.1f} < {min_rating}"
                    },
                    "min_reviews": {
                        "passed": reviews_ok,
                        "threshold": min_reviews,
                        "value": reviews,
                        "detail": f"{reviews} >= {min_reviews}" if reviews_ok 
                                 else f"{reviews} < {min_reviews}"
                    }
                },
                "passed_all_filters": passed
            }
            
            detailed_evaluations.append(eval_record)
            
            # Simple evaluation for console
            evaluations.append({
                "product": product["title"][:30] + ("..." if len(product["title"]) > 30 else ""),
                "price_check": f"${price:.2f} {'✓' if price_ok else '✗'} (${min_price:.2f}-${max_price:.2f})",
                "rating_check": f"{rating:.1f} {'✓' if rating_ok else '✗'} (min {min_rating})",
                "reviews_check": f"{reviews} {'✓' if reviews_ok else '✗'} (min {min_reviews})",
                "passed": passed
            })
            
            if passed:
                filtered.append(product)
        
        # Calculate statistics
        total_products = len(products)
        passed_count = len(filtered)
        failed_count = total_products - passed_count
        
        # Find most common failure reason
        failure_stats = {"price": 0, "rating": 0, "reviews": 0}
        for eval_item in detailed_evaluations:
            if not eval_item["passed_all_filters"]:
                filters = eval_item["filter_results"]
                if not filters["price_range"]["passed"]:
                    failure_stats["price"] += 1
                if not filters["min_rating"]["passed"]:
                    failure_stats["rating"] += 1
                if not filters["min_reviews"]["passed"]:
                    failure_stats["reviews"] += 1
        
        # Determine top failure reason
        top_failure = max(failure_stats.items(), key=lambda x: x[1])
        
        # Add reasoning BEFORE returning
        xray.add_reasoning(
            f"Applied filters to {total_products} candidates. "
            f"Results: {passed_count} passed, {failed_count} failed. "
            f"Price range: ${min_price:.2f}-${max_price:.2f} "
            f"(±{reference_price * 0.5:.2f} from ${reference_price:.2f}). "
            f"Most common failure: {top_failure[0]} filter ({top_failure[1]} products)."
        )
        
        return filtered, evaluations, detailed_evaluations
    
    @xray.trace(name="Rank Products", step_type="ranking")
    def rank_products(self, products):
        """Step 4: Rank and select best competitor"""
        # Simulate ranking computation
        time.sleep(0.04)
        
        if not products:
            xray.add_reasoning("No products to rank - returning None")
            return None
        
        scored_products = []
        
        for product in products:
            # Normalize scores (0-1 range)
            reviews_score = min(product["reviews"] / 20000, 1.0)  # Cap at 20k reviews
            rating_score = product["rating"] / 5.0  # 5-star scale
            
            # Price proximity: closer to $30 is better
            ideal_price = 30.0
            price_diff = abs(product["price"] - ideal_price)
            price_score = max(0, 1 - price_diff / 100)  # Decrease with difference
            
            # Weighted total score
            total_score = (
                reviews_score * 0.4 +      # 40% weight to reviews (popularity)
                rating_score * 0.35 +       # 35% weight to rating (quality)
                price_score * 0.25          # 25% weight to price proximity
            )
            
            scored_products.append({
                "product": product,
                "score_breakdown": {
                    "reviews_score": round(reviews_score, 3),
                    "rating_score": round(rating_score, 3),
                    "price_score": round(price_score, 3)
                },
                "total_score": round(total_score, 3)
            })
        
        # Sort by total score (highest first)
        scored_products.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Add rank
        for i, item in enumerate(scored_products):
            item["rank"] = i + 1
        
        best_product = scored_products[0]["product"]
        best_score = scored_products[0]["total_score"]
        best_breakdown = scored_products[0]["score_breakdown"]
        
        # Add reasoning BEFORE returning
        xray.add_reasoning(
            f"Ranked {len(products)} qualified products. "
            f"Selected: '{best_product['title']}' with score {best_score:.3f}. "
            f"Breakdown: Reviews={best_breakdown['reviews_score']:.3f}, "
            f"Rating={best_breakdown['rating_score']:.3f}, "
            f"Price={best_breakdown['price_score']:.3f}. "
            f"Runner-up: '{scored_products[1]['product']['title'] if len(scored_products) > 1 else 'None'}'"
        )
        
        # Return both the best product and full ranking for X-Ray
        xray_output = {
            "selected": best_product,
            "ranking": scored_products,
            "total_candidates": len(products)
        }
        
        # For backward compatibility, also return just the product
        return best_product
    
    def run_pipeline(self, prospect_product):
        """Complete competitor selection pipeline"""
        print("\n" + "="*60)
        print("COMPETITOR SELECTION PIPELINE")
        print("="*60)
        print(f"Prospect: {prospect_product['title']}")
        print(f"Price: ${prospect_product['price']:.2f}")
        print("="*60)
        
        # Start trace
        trace_id = xray.start_trace(
            f"CompetitorSelection_{prospect_product['title'][:30]}"
        )
        
        try:
            # Step 1: Generate keywords
            print("\n [Step 1] Generating search keywords...")
            keywords = self.generate_keywords(prospect_product["title"])
            print(f"   ✓ Generated {len(keywords)} keywords:")
            for i, kw in enumerate(keywords, 1):
                print(f"     {i}. '{kw}'")
            
            # Step 2: Search for each keyword
            print("\n [Step 2] Searching for products...")
            all_candidates = []
            for i, keyword in enumerate(keywords[:2], 1):  # Use first 2 keywords
                print(f"   Search {i}/2: '{keyword}'")
                results = self.search_products(keyword, limit=5)
                all_candidates.extend(results)
                print(f"     Found {len(results)} products")
            
            # Remove duplicates by ID
            unique_candidates = []
            seen_ids = set()
            for product in all_candidates:
                if product["id"] not in seen_ids:
                    seen_ids.add(product["id"])
                    unique_candidates.append(product)
            
            print(f"    Total unique candidates: {len(unique_candidates)}")
            
            # Step 3: Apply filters
            print("\n [Step 3] Applying business filters...")
            filtered_products, simple_evals, detailed_evals = self.apply_filters(
                unique_candidates, 
                prospect_product["price"],
                min_rating=3.8,
                min_reviews=100
            )
            
            print(f"   ✓ {len(filtered_products)} products passed filters")
            print(f"   ✗ {len(unique_candidates) - len(filtered_products)} products failed")
            
            # Show sample evaluations
            if simple_evals:
                print("\n   Sample evaluations:")
                for eval_item in simple_evals[:3]:  # Show first 3
                    status = "✓ PASS" if eval_item["passed"] else "✗ FAIL"
                    print(f"     • {eval_item['product']} → {status}")
                if len(simple_evals) > 3:
                    print(f"     ... and {len(simple_evals) - 3} more")
            
            # Step 4: Rank and select
            print("\n [Step 4] Ranking and selecting best competitor...")
            if filtered_products:
                best_competitor = self.rank_products(filtered_products)
                
                print("\n" + "="*60)
                print(" FINAL SELECTION")
                print("="*60)
                print(f"   Selected Competitor: {best_competitor['title']}")
                print(f"   Price: ${best_competitor['price']:.2f}")
                print(f"   Rating: {best_competitor['rating']:.1f} ⭐")
                print(f"   Reviews: {best_competitor['reviews']:,} reviews")
                print(f"   Match Quality: Excellent")
                print("="*60)
                
                return {
                    "success": True,
                    "selected_competitor": best_competitor,
                    "total_candidates": len(unique_candidates),
                    "qualified_candidates": len(filtered_products),
                    "trace_id": trace_id
                }
            else:
                print("\n" + "="*60)
                print(" PIPELINE RESULT")
                print("="*60)
                print("   No qualified competitors found")
                print("="*60)
                
                return {
                    "success": False,
                    "error": "No qualified competitors found",
                    "total_candidates": len(unique_candidates),
                    "qualified_candidates": 0,
                    "trace_id": trace_id
                }
                
        except Exception as e:
            print(f"\n Error in pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "trace_id": trace_id
            }
        finally:
            # End trace
            saved_file = xray.end_trace()
            if saved_file:
                print(f"\n X-Ray trace saved: {saved_file}")
                print("="*60)

def main():
    """Run the demo"""
    print("\n" + "="*60)
    print(" X-RAY DEBUGGING DEMO: Competitor Product Selection")
    print("="*60)
    print("Debugging multi-step algorithmic systems")
    print("="*60)
    
    # Create prospect product (seller's product)
    prospect_product = {
        "id": "PRO001",
        "title": "Stainless Steel Water Bottle 32oz Insulated",
        "price": 29.99,
        "rating": 4.2,
        "reviews": 1247,
        "category": "Sports & Outdoors > Water Bottles"
    }
    
    print(f"\n PROSPECT PRODUCT:")
    print(f"   Title: {prospect_product['title']}")
    print(f"   Price: ${prospect_product['price']:.2f}")
    print(f"   Rating: {prospect_product['rating']:.1f} ⭐")
    print(f"   Reviews: {prospect_product['reviews']:,}")
    print(f"   Category: {prospect_product['category']}")
    
    # Create selector and run pipeline
    selector = CompetitorSelector()
    result = selector.run_pipeline(prospect_product)
    
    print("\n" + "="*60)
    print(" PIPELINE METRICS")
    print("="*60)
    print(f"   Success: {'✓ YES' if result['success'] else '✗ NO'}")
    print(f"   Candidates considered: {result['total_candidates']}")
    print(f"   Qualified candidates: {result['qualified_candidates']}")
    print(f"   Qualification rate: {(result['qualified_candidates']/result['total_candidates']*100 if result['total_candidates'] > 0 else 0):.1f}%")
    
    if result['success']:
        comp = result['selected_competitor']
        price_diff = comp['price'] - prospect_product['price']
        price_diff_pct = (price_diff / prospect_product['price']) * 100
        
        print("\n BUSINESS INSIGHTS:")
        print(f"   • Selected competitor is {abs(price_diff_pct):.1f}% {'more' if price_diff > 0 else 'less'} expensive")
        print(f"   • Competitor has {comp['reviews']/prospect_product['reviews']:.1f}x more reviews")
        print(f"   • Quality match: {'Superior' if comp['rating'] > prospect_product['rating'] else 'Comparable'}")
        print(f"   • Market position: {'Established leader' if comp['reviews'] > 5000 else 'Growing competitor'}")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Check X-Ray Dashboard: http://localhost:8000")
    print("2. Review detailed trace for debugging insights")
    print("3. Adjust filters or ranking weights as needed")
    print("="*60)

if __name__ == "__main__":
    main()