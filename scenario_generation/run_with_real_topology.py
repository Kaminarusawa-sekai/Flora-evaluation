"""Run scenario generation with real topology data from Neo4j."""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenario_generation.example_with_topology import example_with_real_topology

if __name__ == "__main__":
    print("""
================================================================================
Scenario Generation with Real Topology Data
================================================================================

This script will:
1. Load and normalize APIs from erp-server.json
2. Build topology graph in Neo4j
3. Extract topology data (APIs, dependencies, entities)
4. Discover API paths from topology
5. Generate test themes for each path
6. Generate test scenarios (normal + exception)
7. Save results to output/real_topology_scenarios.json

Prerequisites:
- Neo4j running at bolt://192.168.1.210:7687
- erp-server.json in project root directory
- Python packages: neo4j, openai (optional)

================================================================================
""")

    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        sys.exit(0)

    print("\nStarting...\n")
    example_with_real_topology()
