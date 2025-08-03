#!/usr/bin/env python3
"""
Generate performance test reports
"""

import json
import os
import datetime
from typing import Dict, List, Any
from pathlib import Path

def load_performance_data() -> Dict[str, Any]:
    """Load performance test data"""
    results_dir = Path("tests/results")
    performance_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'test_results': [],
        'summary': {}
    }
    
    # Look for performance test results
    for result_file in results_dir.glob("performance_*.json"):
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
                performance_data['test_results'].append(data)
        except Exception as e:
            print(f"Error loading {result_file}: {e}")
    
    return performance_data

def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate HTML performance report"""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DexAgent Performance Test Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .test-section {
            margin-bottom: 30px;
        }
        .test-title {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warning { color: #ffc107; }
        .chart-container {
            margin: 20px 0;
            height: 300px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DexAgent Performance Test Report</h1>
            <p>Generated on: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="metric-value">{total_tests}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="metric-value">{passed_tests}</div>
                <div class="metric-label">Passed Tests</div>
            </div>
            <div class="summary-card">
                <div class="metric-value">{avg_response_time:.2f}ms</div>
                <div class="metric-label">Avg Response Time</div>
            </div>
            <div class="summary-card">
                <div class="metric-value">{requests_per_second:.1f}</div>
                <div class="metric-label">Requests/Second</div>
            </div>
        </div>
        
        {test_sections}
    </div>
</body>
</html>
"""
    
    # Calculate summary metrics
    total_tests = len(data['test_results'])
    passed_tests = sum(1 for test in data['test_results'] if test.get('passed', False))
    avg_response_time = sum(test.get('avg_response_time', 0) for test in data['test_results']) / max(total_tests, 1) * 1000
    requests_per_second = sum(test.get('requests_per_second', 0) for test in data['test_results']) / max(total_tests, 1)
    
    # Generate test sections
    test_sections = ""
    for test in data['test_results']:
        test_sections += f"""
        <div class="test-section">
            <h2 class="test-title">{test.get('test_name', 'Unknown Test')}</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Response Time (avg)</td>
                    <td>{test.get('avg_response_time', 0) * 1000:.2f}ms</td>
                    <td class="{'pass' if test.get('avg_response_time', 0) < 2 else 'fail'}">
                        {'✓' if test.get('avg_response_time', 0) < 2 else '✗'}
                    </td>
                </tr>
                <tr>
                    <td>Success Rate</td>
                    <td>{test.get('success_rate', 0):.1f}%</td>
                    <td class="{'pass' if test.get('success_rate', 0) > 95 else 'fail'}">
                        {'✓' if test.get('success_rate', 0) > 95 else '✗'}
                    </td>
                </tr>
                <tr>
                    <td>Requests/Second</td>
                    <td>{test.get('requests_per_second', 0):.1f}</td>
                    <td class="pass">✓</td>
                </tr>
            </table>
        </div>
        """
    
    return html_template.format(
        timestamp=data['timestamp'],
        total_tests=total_tests,
        passed_tests=passed_tests,
        avg_response_time=avg_response_time,
        requests_per_second=requests_per_second,
        test_sections=test_sections
    )

def main():
    """Main function"""
    print("Generating performance test report...")
    
    # Load performance data
    data = load_performance_data()
    
    if not data['test_results']:
        print("No performance test data found.")
        return
    
    # Generate HTML report
    html_report = generate_html_report(data)
    
    # Save report
    report_path = Path("tests/results/performance_report.html")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(html_report)
    
    print(f"Performance report generated: {report_path}")
    
    # Generate JSON summary
    summary = {
        'timestamp': data['timestamp'],
        'total_tests': len(data['test_results']),
        'passed_tests': sum(1 for test in data['test_results'] if test.get('passed', False)),
        'avg_response_time': sum(test.get('avg_response_time', 0) for test in data['test_results']) / max(len(data['test_results']), 1),
        'requests_per_second': sum(test.get('requests_per_second', 0) for test in data['test_results']) / max(len(data['test_results']), 1)
    }
    
    summary_path = Path("tests/results/performance_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Performance summary generated: {summary_path}")

if __name__ == '__main__':
    main()