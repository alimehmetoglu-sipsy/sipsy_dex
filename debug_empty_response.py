#!/usr/bin/env python3
"""
Debug empty process list response
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"
AGENT_ID = "desktop-jk5g34l-dexagent"

def get_token():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]

def debug_empty_response():
    """Debug why process API returns empty array"""
    
    print(f"🔍 Debugging Empty Process Response for: {AGENT_ID}")
    
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Check agent status in detail
        print("\n📊 Agent Status Check:")
        agent_response = requests.get(f"{BASE_URL}/api/v1/agents/{AGENT_ID}", headers=headers)
        
        if agent_response.status_code == 200:
            agent = agent_response.json()
            print(f"  Status: {agent.get('status')}")
            print(f"  Connected: {agent.get('is_connected')}")
            print(f"  Last Seen: {agent.get('last_seen')}")
            print(f"  Connection ID: {agent.get('connection_id')}")
            
            if not agent.get('is_connected'):
                print("  ❌ Agent is not connected via WebSocket!")
                print("  This explains why process API returns empty array")
                return False
        else:
            print("  ❌ Agent not found")
            return False
        
        # 2. Test process API with detailed timing
        print(f"\n🔄 Testing Process API with timing:")
        
        start_time = time.time()
        try:
            process_response = requests.get(
                f"{BASE_URL}/api/v1/agents/{AGENT_ID}/processes",
                headers=headers,
                timeout=90
            )
            end_time = time.time()
            
            print(f"  Response Time: {end_time - start_time:.2f} seconds")
            print(f"  Status Code: {process_response.status_code}")
            
            if process_response.status_code == 200:
                processes = process_response.json()
                print(f"  Process Count: {len(processes)}")
                
                if len(processes) == 0:
                    print("  ❌ Empty array returned!")
                    print("  This could mean:")
                    print("    - Agent is not connected via WebSocket")
                    print("    - PowerShell command failed")
                    print("    - WebSocket response not received")
                    print("    - Command timeout on agent side")
                else:
                    print("  ✅ Processes received:")
                    for proc in processes[:3]:
                        print(f"    - {proc.get('name')} (PID: {proc.get('pid')})")
                        
            elif process_response.status_code == 400:
                error = process_response.json()
                print(f"  ❌ Bad Request: {error.get('detail')}")
                
            elif process_response.status_code == 408:
                print(f"  ⏱️  Request Timeout")
                print("  PowerShell command took too long to execute")
                
            else:
                print(f"  ❌ Error: {process_response.status_code}")
                print(f"  Response: {process_response.text}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Client timeout after 90 seconds")
            
        # 3. Check if we can send a simple command to agent
        print(f"\n🧪 Testing Basic Agent Communication:")
        
        # Try to get agent list to see if any agents are connected
        agents_response = requests.get(f"{BASE_URL}/api/v1/agents/", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            connected_agents = [a for a in agents if a.get('is_connected')]
            print(f"  Total Agents: {len(agents)}")
            print(f"  Connected Agents: {len(connected_agents)}")
            
            for agent in connected_agents:
                print(f"    - {agent.get('id')} ({agent.get('hostname')})")
                
        return True
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False

if __name__ == "__main__":
    debug_empty_response()