"""
API Demo Script
Demonstrates all features of the Dengue Resource Allocation API
"""

import requests
import json
import time
from typing import Dict

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def print_response(response: requests.Response, show_full: bool = False):
    """Print formatted API response"""
    try:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        
        if show_full:
            print(json.dumps(data, indent=2))
        else:
            # Print summary
            if 'status' in data:
                print(f"Status: {data['status']}")
            if 'message' in data:
                print(f"Message: {data['message']}")
            if 'count' in data:
                print(f"Count: {data['count']}")
    except:
        print(f"Status Code: {response.status_code}")
        print(response.text)


def demo_health_check():
    """Demo: Check API health"""
    print_section("1. HEALTH CHECK")
    
    print("\n📍 Checking API health...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, show_full=True)


def demo_resource_management():
    """Demo: Resource management operations"""
    print_section("2. RESOURCE MANAGEMENT")
    
    # Get current resources
    print("\n📍 Getting current resources...")
    response = requests.get(f"{BASE_URL}/resources/")
    print_response(response)
    
    # Set resources
    print("\n📍 Setting available resources...")
    resources = {
        "Fogging_Units": 100,
        "Health_Inspectors": 50,
        "Inspection_Teams": 30,
        "Treatment_Units": 80
    }
    response = requests.post(f"{BASE_URL}/resources/", json=resources)
    print_response(response)
    
    # Update specific resource
    print("\n📍 Updating Fogging Units to 120...")
    response = requests.put(f"{BASE_URL}/resources/Fogging_Units?quantity=120")
    print_response(response)
    
    # Get updated resources
    print("\n📍 Getting updated resources...")
    response = requests.get(f"{BASE_URL}/resources/")
    data = response.json()
    print(f"Available resources: {data['available_resources']}")
    print(f"Total: {data['total_resources']}")


def demo_predictions():
    """Demo: Prediction generation and retrieval"""
    print_section("3. PREDICTIONS")
    
    # Generate predictions
    print("\n📍 Generating new predictions...")
    response = requests.post(f"{BASE_URL}/predictions/generate")
    print_response(response)
    
    time.sleep(1)  # Brief pause
    
    # Get all predictions
    print("\n📍 Retrieving all district predictions...")
    response = requests.get(f"{BASE_URL}/predictions/districts")
    data = response.json()
    print(f"Total districts: {data['count']}")
    
    if data['predictions']:
        print("\nSample predictions:")
        for pred in data['predictions'][:3]:
            print(f"  • {pred['District']}: {pred['Risk_Level']} "
                  f"(Confidence: {pred['High_Probability']:.2%})")
    
    # Get specific district
    print("\n📍 Getting prediction for Colombo...")
    response = requests.get(f"{BASE_URL}/predictions/districts/Colombo")
    if response.status_code == 200:
        data = response.json()
        district = data['district']
        print(f"District: {district['District']}")
        print(f"Risk Level: {district['Risk_Level']}")
        print(f"High Risk Probability: {district['High_Probability']:.2%}")
        print(f"Is Hotspot: {district.get('Is_Hotspot', False)}")


def demo_hotspots():
    """Demo: Hotspot identification"""
    print_section("4. HOTSPOT IDENTIFICATION")
    
    print("\n📍 Retrieving dengue hotspots...")
    response = requests.get(f"{BASE_URL}/predictions/hotspots")
    data = response.json()
    
    print(f"Total hotspots identified: {data['count']}")
    
    if data['hotspots']:
        print("\n🔴 Hotspot Districts:")
        for i, hotspot in enumerate(data['hotspots'], 1):
            print(f"  {i}. {hotspot['District']}")
            print(f"     Risk Level: {hotspot['Risk_Level']}")
            print(f"     Priority Score: {hotspot.get('Hotspot_Priority', 0):.3f}")
    else:
        print("✓ No hotspots detected - all districts are low to medium risk")


def demo_recommendations():
    """Demo: Resource recommendations"""
    print_section("5. RESOURCE RECOMMENDATIONS")
    
    print("\n📍 Getting ML-generated resource recommendations...")
    response = requests.get(f"{BASE_URL}/predictions/recommendations")
    data = response.json()
    
    print(f"Recommendations generated for {data['count']} districts")
    
    if 'totals' in data:
        print("\n📊 Total Resources Recommended:")
        for resource, amount in data['totals'].items():
            print(f"  • {resource}: {amount}")
    
    if data['recommendations']:
        print("\n📋 Sample District Recommendations:")
        for rec in data['recommendations'][:3]:
            print(f"\n  District: {rec['District']}")
            print(f"    Fogging Units: {rec['Fogging_Units']}")
            print(f"    Health Inspectors: {rec['Health_Inspectors']}")
            print(f"    Inspection Teams: {rec['Inspection_Teams']}")
            print(f"    Treatment Units: {rec['Treatment_Units']}")
    
    # Get specific district recommendation
    print("\n📍 Getting recommendation for Colombo...")
    response = requests.get(f"{BASE_URL}/predictions/recommendations/Colombo")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data['recommendation'], indent=2))


def demo_resource_assignment():
    """Demo: Resource assignment to districts"""
    print_section("6. RESOURCE ASSIGNMENT")
    
    # Assign resources to a district
    print("\n📍 Assigning resources to Colombo...")
    assignment = {
        "district": "Colombo",
        "Fogging_Units": 15,
        "Health_Inspectors": 8,
        "Inspection_Teams": 5,
        "Treatment_Units": 12,
        "notes": "High priority hotspot allocation"
    }
    
    response = requests.post(f"{BASE_URL}/resources/assign", json=assignment)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        print(f"\nAssigned Resources:")
        for resource, amount in data['assigned_resources'].items():
            print(f"  • {resource}: {amount}")
        print(f"\nRemaining Resources:")
        for resource, amount in data['remaining_resources'].items():
            print(f"  • {resource}: {amount}")
    else:
        print_response(response)
    
    # Get assignment history
    print("\n📍 Viewing assignment history...")
    response = requests.get(f"{BASE_URL}/resources/assignments")
    data = response.json()
    print(f"Total assignments: {data['count']}")
    
    if data['assignments']:
        print("\nRecent assignments:")
        for assignment in data['assignments'][-3:]:
            print(f"  • {assignment['district']}: {assignment['resources']}")
            print(f"    Assigned at: {assignment.get('assigned_at', 'N/A')}")


def demo_admin_dashboard():
    """Demo: Admin dashboard features"""
    print_section("7. ADMIN DASHBOARD")
    
    # Get overview
    print("\n📍 Loading admin overview...")
    response = requests.get(f"{BASE_URL}/admin/overview")
    data = response.json()
    
    print("\n📊 SUMMARY:")
    summary = data['summary']
    print(f"  Total Districts: {summary['total_districts']}")
    print(f"  High Risk: {summary['high_risk_count']}")
    print(f"  Medium Risk: {summary['medium_risk_count']}")
    print(f"  Low Risk: {summary['low_risk_count']}")
    print(f"  Hotspots: {summary['hotspot_count']}")
    
    print("\n📦 AVAILABLE RESOURCES:")
    for resource, amount in data['available_resources'].items():
        print(f"  • {resource}: {amount}")
    
    if data['hotspots']:
        print(f"\n🔴 TOP HOTSPOTS ({len(data['hotspots'])}):")
        for hotspot in data['hotspots'][:3]:
            print(f"  • {hotspot['District']}")
    
    # Get statistics
    print("\n📍 Loading detailed statistics...")
    response = requests.get(f"{BASE_URL}/admin/statistics")
    data = response.json()
    
    if 'statistics' in data:
        stats = data['statistics']
        print("\n📈 RISK DISTRIBUTION:")
        for level, count in stats.get('risk_distribution', {}).items():
            print(f"  • {level}: {count}")
    
    # Resource gap analysis
    print("\n📍 Analyzing resource gaps...")
    response = requests.get(f"{BASE_URL}/admin/resource-gap")
    data = response.json()
    
    if 'gap_analysis' in data:
        print("\n⚖️  RESOURCE GAP ANALYSIS:")
        for resource, analysis in data['gap_analysis'].items():
            status = "✓ Sufficient" if analysis['sufficient'] else "⚠ Insufficient"
            print(f"  {resource}: {status}")
            print(f"    Recommended: {analysis['total_recommended']}")
            print(f"    Available: {analysis['currently_available']}")
            print(f"    Gap: {analysis['gap']} ({analysis['gap_percentage']:.1f}%)")


def demo_comparison():
    """Demo: District comparison"""
    print_section("8. DISTRICT COMPARISON")
    
    print("\n📍 Comparing all districts...")
    response = requests.get(f"{BASE_URL}/admin/district-comparison")
    data = response.json()
    
    if data.get('comparison'):
        print(f"\n📊 Districts ranked by risk (showing top 5):")
        for i, district in enumerate(data['comparison'][:5], 1):
            print(f"\n  {i}. {district['District']}")
            print(f"     Risk: {district['Risk_Level']}")
            print(f"     High Prob: {district.get('High_Probability', 0):.2%}")
            if 'Recommended_Fogging_Units' in district:
                print(f"     Recommended Fogging: {district['Recommended_Fogging_Units']}")


def main():
    """Run complete API demonstration"""
    print("\n" + "="*70)
    print(" DENGUE RESOURCE ALLOCATION API - COMPLETE DEMO")
    print("="*70)
    print("\nThis demo will showcase all API features")
    print("Make sure the API server is running at:", BASE_URL)
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Run all demos
        demo_health_check()
        time.sleep(0.5)
        
        demo_resource_management()
        time.sleep(0.5)
        
        demo_predictions()
        time.sleep(0.5)
        
        demo_hotspots()
        time.sleep(0.5)
        
        demo_recommendations()
        time.sleep(0.5)
        
        demo_resource_assignment()
        time.sleep(0.5)
        
        demo_admin_dashboard()
        time.sleep(0.5)
        
        demo_comparison()
        
        # Final summary
        print_section("DEMO COMPLETE")
        print("\n✅ All API features demonstrated successfully!")
        print("\n📚 For more information:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Alternative Docs: http://localhost:8000/redoc")
        print("   • README: See README.md")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   python3 -m uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()