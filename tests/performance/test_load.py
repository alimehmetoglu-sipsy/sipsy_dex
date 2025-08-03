#!/usr/bin/env python3
"""
Performance and Load Tests for DexAgent
This module tests the system performance under various load conditions.
"""

import asyncio
import concurrent.futures
import json
import time
import uuid
import statistics
import pytest
import requests
import websockets
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import threading

# Test configuration
PERF_CONFIG = {
    'backend_url': 'http://localhost:8080',
    'websocket_url': 'ws://localhost:8080/api/v1/ws',
    'test_user': {
        'username': 'admin',
        'password': 'admin123'
    },
    'load_test': {
        'concurrent_agents': 50,
        'concurrent_commands': 100,
        'test_duration': 60,  # seconds
        'ramp_up_time': 10,   # seconds
    },
    'performance_thresholds': {
        'api_response_time': 2.0,  # seconds
        'websocket_latency': 0.5,  # seconds
        'command_execution_time': 5.0,  # seconds
        'memory_usage_mb': 512,  # MB
        'cpu_usage_percent': 80,  # %
    }
}

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: float
    threshold: float = None
    
    @property
    def is_within_threshold(self) -> bool:
        if self.threshold is None:
            return True
        return self.value <= self.threshold

@dataclass
class LoadTestResult:
    """Load test result data structure"""
    test_name: str
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    errors: List[str]
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

class PerformanceTestBase:
    """Base class for performance tests"""
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.metrics: List[PerformanceMetric] = []
        
    def setup_method(self):
        """Setup method called before each test"""
        self.authenticate()
        self.metrics.clear()
        
    def authenticate(self):
        """Authenticate with the API"""
        response = self.session.post(
            f"{PERF_CONFIG['backend_url']}/api/v1/auth/login",
            json=PERF_CONFIG['test_user']
        )
        assert response.status_code == 200
        
        data = response.json()
        self.auth_token = data['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}'
        })
        
    def add_metric(self, name: str, value: float, unit: str, threshold: float = None):
        """Add a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            threshold=threshold
        )
        self.metrics.append(metric)
        return metric
        
    def measure_response_time(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure response time of a function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        response_time = end_time - start_time
        return result, response_time
        
    def assert_performance_thresholds(self):
        """Assert that all metrics are within thresholds"""
        failed_metrics = [m for m in self.metrics if not m.is_within_threshold]
        if failed_metrics:
            failures = [f"{m.name}: {m.value} {m.unit} > {m.threshold} {m.unit}" 
                       for m in failed_metrics]
            raise AssertionError(f"Performance thresholds exceeded: {', '.join(failures)}")

class TestAPIPerformance(PerformanceTestBase):
    """Test API endpoint performance"""
    
    def test_api_response_times(self):
        """Test API response times under normal load"""
        
        endpoints = [
            ('GET', '/api/v1/agents'),
            ('GET', '/api/v1/commands/saved'),
            ('GET', '/api/v1/system/health'),
            ('GET', '/api/v1/system/info'),
        ]
        
        for method, endpoint in endpoints:
            response_times = []
            
            # Test each endpoint multiple times
            for _ in range(10):
                if method == 'GET':
                    response, response_time = self.measure_response_time(
                        self.session.get, f"{PERF_CONFIG['backend_url']}{endpoint}"
                    )
                    
                    assert response.status_code == 200
                    response_times.append(response_time)
                    
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            self.add_metric(
                f"API {endpoint} avg response time",
                avg_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['api_response_time']
            )
            
            self.add_metric(
                f"API {endpoint} max response time",
                max_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['api_response_time'] * 2
            )
            
        self.assert_performance_thresholds()
        
    def test_concurrent_api_requests(self):
        """Test API performance under concurrent load"""
        
        def make_request():
            try:
                start_time = time.time()
                response = self.session.get(f"{PERF_CONFIG['backend_url']}/api/v1/agents")
                end_time = time.time()
                
                return {
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time,
                    'status_code': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'response_time': 0,
                    'error': str(e)
                }
                
        # Run concurrent requests
        concurrent_requests = 50
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
            
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            
            self.add_metric(
                "Concurrent API avg response time",
                avg_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['api_response_time']
            )
            
            self.add_metric(
                "Concurrent API P95 response time",
                p95_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['api_response_time'] * 1.5
            )
            
        success_rate = len(successful_requests) / len(results) * 100
        self.add_metric(
            "Concurrent API success rate",
            success_rate,
            "%",
            95.0  # 95% success rate threshold
        )
        
        total_duration = end_time - start_time
        requests_per_second = len(results) / total_duration
        self.add_metric(
            "API requests per second",
            requests_per_second,
            "req/s"
        )
        
        self.assert_performance_thresholds()

class TestWebSocketPerformance(PerformanceTestBase):
    """Test WebSocket performance"""
    
    async def test_websocket_latency(self):
        """Test WebSocket message latency"""
        
        latencies = []
        
        async def measure_ping_latency():
            uri = f"{PERF_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                
                for i in range(10):
                    # Send ping message
                    ping_msg = {
                        'type': 'ping',
                        'id': str(uuid.uuid4()),
                        'timestamp': time.time()
                    }
                    
                    send_time = time.time()
                    await websocket.send(json.dumps(ping_msg))
                    
                    # Wait for pong response
                    response = await websocket.recv()
                    receive_time = time.time()
                    
                    response_data = json.loads(response)
                    if response_data['type'] == 'pong':
                        latency = receive_time - send_time
                        latencies.append(latency)
                        
                    await asyncio.sleep(0.1)
                    
        await measure_ping_latency()
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            
            self.add_metric(
                "WebSocket avg latency",
                avg_latency,
                "seconds",
                PERF_CONFIG['performance_thresholds']['websocket_latency']
            )
            
            self.add_metric(
                "WebSocket max latency",
                max_latency,
                "seconds",
                PERF_CONFIG['performance_thresholds']['websocket_latency'] * 2
            )
            
        self.assert_performance_thresholds()
        
    async def test_concurrent_websocket_connections(self):
        """Test performance with multiple WebSocket connections"""
        
        connection_count = 20
        messages_per_connection = 5
        results = []
        
        async def test_single_connection(connection_id):
            try:
                uri = f"{PERF_CONFIG['websocket_url']}/agent"
                async with websockets.connect(uri) as websocket:
                    
                    # Register agent
                    agent_data = {
                        'id': f'perf_test_agent_{connection_id}',
                        'name': f'Performance Test Agent {connection_id}',
                        'hostname': f'perf-test-{connection_id}',
                        'ip_address': f'192.168.1.{100 + connection_id}',
                        'os': 'Windows 10',
                        'version': '1.0.0'
                    }
                    
                    registration_msg = {
                        'type': 'agent_register',
                        'id': str(uuid.uuid4()),
                        'timestamp': time.time(),
                        'payload': agent_data
                    }
                    
                    start_time = time.time()
                    await websocket.send(json.dumps(registration_msg))
                    
                    # Wait for registration response
                    response = await websocket.recv()
                    registration_time = time.time() - start_time
                    
                    # Send heartbeat messages
                    heartbeat_times = []
                    for _ in range(messages_per_connection):
                        heartbeat_msg = {
                            'type': 'agent_heartbeat',
                            'id': str(uuid.uuid4()),
                            'timestamp': time.time(),
                            'payload': {
                                'agent_id': agent_data['id'],
                                'status': 'idle'
                            }
                        }
                        
                        msg_start = time.time()
                        await websocket.send(json.dumps(heartbeat_msg))
                        msg_end = time.time()
                        heartbeat_times.append(msg_end - msg_start)
                        
                        await asyncio.sleep(0.1)
                        
                    return {
                        'connection_id': connection_id,
                        'success': True,
                        'registration_time': registration_time,
                        'avg_heartbeat_time': statistics.mean(heartbeat_times),
                        'total_messages': messages_per_connection + 1
                    }
                    
            except Exception as e:
                return {
                    'connection_id': connection_id,
                    'success': False,
                    'error': str(e)
                }
                
        # Run concurrent connections
        start_time = time.time()
        tasks = [test_single_connection(i) for i in range(connection_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_connections = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_connections = [r for r in results if not isinstance(r, dict) or not r.get('success')]
        
        if successful_connections:
            avg_registration_time = statistics.mean([r['registration_time'] for r in successful_connections])
            avg_heartbeat_time = statistics.mean([r['avg_heartbeat_time'] for r in successful_connections])
            
            self.add_metric(
                "WebSocket avg registration time",
                avg_registration_time,
                "seconds",
                1.0  # 1 second threshold
            )
            
            self.add_metric(
                "WebSocket avg heartbeat time",
                avg_heartbeat_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['websocket_latency']
            )
            
        success_rate = len(successful_connections) / len(results) * 100
        self.add_metric(
            "WebSocket connection success rate",
            success_rate,
            "%",
            95.0  # 95% success rate threshold
        )
        
        total_duration = end_time - start_time
        connections_per_second = len(results) / total_duration
        self.add_metric(
            "WebSocket connections per second",
            connections_per_second,
            "conn/s"
        )
        
        self.assert_performance_thresholds()

class TestCommandExecutionPerformance(PerformanceTestBase):
    """Test command execution performance"""
    
    def test_sequential_command_execution(self):
        """Test sequential command execution performance"""
        
        # Create test agent
        agent_data = {
            'id': f'perf_cmd_agent_{uuid.uuid4().hex[:8]}',
            'name': 'Performance Command Test Agent',
            'hostname': 'perf-cmd-machine',
            'ip_address': '192.168.1.200',
            'os': 'Windows 10',
            'version': '1.0.0'
        }
        
        # Register agent (simulated)
        response = self.session.post(
            f"{PERF_CONFIG['backend_url']}/api/v1/agents",
            json=agent_data
        )
        # Note: This might fail if endpoint doesn't exist, but we'll continue
        
        # Test command execution times
        commands = [
            'Get-Date',
            'Get-Process | Select-Object -First 5 Name',
            'Get-Service | Where-Object {$_.Status -eq "Running"} | Select-Object -First 3',
            'Get-ComputerInfo | Select-Object WindowsProductName',
            'Get-EventLog -LogName System -Newest 1'
        ]
        
        execution_times = []
        for command in commands:
            execution_data = {
                'command': command,
                'timeout': 30,
                'parameters': {}
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{PERF_CONFIG['backend_url']}/api/v1/commands/agent/{agent_data['id']}/execute",
                json=execution_data
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Note: In real test, we'd wait for command completion
            # Here we're just measuring API response time
            
        if execution_times:
            avg_execution_time = statistics.mean(execution_times)
            max_execution_time = max(execution_times)
            
            self.add_metric(
                "Command execution avg time",
                avg_execution_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['command_execution_time']
            )
            
            self.add_metric(
                "Command execution max time",
                max_execution_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['command_execution_time'] * 1.5
            )
            
        self.assert_performance_thresholds()
        
    def test_concurrent_command_execution(self):
        """Test concurrent command execution performance"""
        
        def execute_command(agent_id, command_index):
            try:
                execution_data = {
                    'command': f'Get-Date; Write-Output "Command {command_index}"',
                    'timeout': 30,
                    'parameters': {}
                }
                
                start_time = time.time()
                response = self.session.post(
                    f"{PERF_CONFIG['backend_url']}/api/v1/commands/agent/{agent_id}/execute",
                    json=execution_data
                )
                end_time = time.time()
                
                return {
                    'success': response.status_code in [200, 201],
                    'response_time': end_time - start_time,
                    'command_index': command_index
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'command_index': command_index
                }
                
        # Simulate multiple agents
        agent_count = 5
        commands_per_agent = 10
        
        agents = []
        for i in range(agent_count):
            agent_data = {
                'id': f'perf_concurrent_agent_{i}',
                'name': f'Performance Concurrent Agent {i}',
                'hostname': f'perf-concurrent-{i}',
                'ip_address': f'192.168.1.{210 + i}',
                'os': 'Windows 10',
                'version': '1.0.0'
            }
            agents.append(agent_data)
            
        # Execute commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=agent_count * commands_per_agent) as executor:
            futures = []
            for agent in agents:
                for cmd_index in range(commands_per_agent):
                    future = executor.submit(execute_command, agent['id'], cmd_index)
                    futures.append(future)
                    
            start_time = time.time()
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
            
        # Analyze results
        successful_commands = [r for r in results if r.get('success')]
        failed_commands = [r for r in results if not r.get('success')]
        
        if successful_commands:
            response_times = [r['response_time'] for r in successful_commands]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            
            self.add_metric(
                "Concurrent command avg response time",
                avg_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['command_execution_time']
            )
            
            self.add_metric(
                "Concurrent command P95 response time",
                p95_response_time,
                "seconds",
                PERF_CONFIG['performance_thresholds']['command_execution_time'] * 1.5
            )
            
        success_rate = len(successful_commands) / len(results) * 100
        self.add_metric(
            "Concurrent command success rate",
            success_rate,
            "%",
            90.0  # 90% success rate threshold
        )
        
        total_duration = end_time - start_time
        commands_per_second = len(results) / total_duration
        self.add_metric(
            "Commands per second",
            commands_per_second,
            "cmd/s"
        )
        
        self.assert_performance_thresholds()

class TestSystemResourceUsage(PerformanceTestBase):
    """Test system resource usage under load"""
    
    def test_memory_usage_under_load(self):
        """Test memory usage during high load"""
        
        import psutil
        import threading
        
        memory_measurements = []
        stop_monitoring = threading.Event()
        
        def monitor_memory():
            while not stop_monitoring.is_set():
                memory_usage = psutil.virtual_memory().used / 1024 / 1024  # MB
                memory_measurements.append(memory_usage)
                time.sleep(0.5)
                
        # Start memory monitoring
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.start()
        
        try:
            # Generate load by making many API requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for _ in range(100):
                    future = executor.submit(
                        self.session.get,
                        f"{PERF_CONFIG['backend_url']}/api/v1/agents"
                    )
                    futures.append(future)
                    
                # Wait for all requests to complete
                for future in concurrent.futures.as_completed(futures):
                    future.result()
                    
        finally:
            stop_monitoring.set()
            monitor_thread.join()
            
        if memory_measurements:
            avg_memory = statistics.mean(memory_measurements)
            max_memory = max(memory_measurements)
            
            self.add_metric(
                "Average memory usage",
                avg_memory,
                "MB",
                PERF_CONFIG['performance_thresholds']['memory_usage_mb']
            )
            
            self.add_metric(
                "Peak memory usage",
                max_memory,
                "MB",
                PERF_CONFIG['performance_thresholds']['memory_usage_mb'] * 1.2
            )
            
        self.assert_performance_thresholds()

# Load test runner
class LoadTestRunner:
    """Run comprehensive load tests"""
    
    def __init__(self):
        self.results: List[LoadTestResult] = []
        
    def run_load_test(self, test_name: str, test_func, duration: int = 60) -> LoadTestResult:
        """Run a load test for specified duration"""
        
        start_time = time.time()
        end_time = start_time + duration
        
        results = []
        errors = []
        
        def worker():
            while time.time() < end_time:
                try:
                    result = test_func()
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))
                    
        # Run load test with multiple threads
        threads = []
        for _ in range(10):  # 10 concurrent threads
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        actual_duration = time.time() - start_time
        
        # Calculate metrics
        successful_requests = len([r for r in results if r.get('success', True)])
        failed_requests = len(results) - successful_requests
        
        if results:
            response_times = [r.get('response_time', 0) for r in results if 'response_time' in r]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max_response_time
                p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max_response_time
            else:
                avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
            
        requests_per_second = len(results) / actual_duration if actual_duration > 0 else 0
        
        load_test_result = LoadTestResult(
            test_name=test_name,
            duration=actual_duration,
            total_requests=len(results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            errors=errors
        )
        
        self.results.append(load_test_result)
        return load_test_result

# Async test runner for WebSocket tests
def test_websocket_latency():
    """Wrapper for async WebSocket latency test"""
    test_instance = TestWebSocketPerformance()
    test_instance.setup_method()
    asyncio.run(test_instance.test_websocket_latency())

def test_concurrent_websockets():
    """Wrapper for async concurrent WebSocket test"""
    test_instance = TestWebSocketPerformance()
    test_instance.setup_method()
    asyncio.run(test_instance.test_concurrent_websocket_connections())

# Test runner
if __name__ == '__main__':
    import sys
    
    # Run with pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short', '-m', 'not slow']))