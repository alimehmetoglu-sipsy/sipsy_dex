# DexAgent Monitoring Infrastructure

This directory contains the complete monitoring infrastructure for DexAgent, including Prometheus metrics collection, Grafana dashboards, and alerting configuration.

## Architecture

```
monitoring/
├── prometheus/         # Prometheus configuration
│   ├── config/        # Main Prometheus config
│   └── rules/         # Alerting rules
├── grafana/           # Grafana dashboards and provisioning
│   └── provisioning/  # Automated dashboard/datasource setup
├── alerts/            # Alertmanager configuration
└── docker-compose.monitoring.yml  # Monitoring services
```

## Services

### Prometheus (Port 9090)
- **Purpose**: Metrics collection and storage
- **Config**: `prometheus/config/prometheus.yml`
- **Retention**: 15 days
- **Targets**: Backend API, Frontend, Database, System metrics

### Grafana (Port 3001)
- **Purpose**: Visualization and dashboards
- **Login**: admin/admin123
- **Dashboards**: DexAgent Overview, System Metrics
- **Auto-provisioning**: Dashboards and datasources

### AlertManager (Port 9093)
- **Purpose**: Alert handling and routing
- **Config**: `alerts/alertmanager.yml`
- **Channels**: Slack, Email notifications

### Exporters
- **Node Exporter** (9100): System metrics (CPU, memory, disk, network)
- **cAdvisor** (8080): Container metrics
- **Postgres Exporter** (9187): Database metrics
- **Nginx Exporter** (9113): Web server metrics

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start monitoring services
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Verify all services are running
docker-compose -f monitoring/docker-compose.monitoring.yml ps
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

### 3. View Metrics

- **DexAgent Backend**: http://localhost:8080/api/v1/metrics
- **System Health**: http://localhost:8080/api/v1/health
- **Statistics**: http://localhost:8080/api/v1/stats

## Dashboards

### DexAgent Overview
- Service status indicators (Backend, Frontend, Database)
- Connected agents count
- API request rate and response times
- CPU and memory usage
- **Access**: Grafana → Dashboards → DexAgent Overview

### System Metrics
- Detailed memory usage breakdown
- Disk usage by mount point
- Network I/O statistics
- Disk I/O operations
- **Access**: Grafana → Dashboards → System Metrics

## Metrics Collected

### Application Metrics
```
# Service availability
up{job="dexagent-backend"}
up{job="dexagent-frontend"}
up{job="postgres"}

# API performance
http_requests_total{method, path, status}
http_request_duration_seconds{method, path}

# Agent metrics
agents_online_total
agents_offline_total
agent_last_seen_timestamp{agent_id}
agent_command_failures_total{agent_id}
```

### System Metrics
```
# CPU
node_cpu_seconds_total{mode, cpu}
system_cpu_usage_percent

# Memory
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
system_memory_usage_percent

# Disk
node_filesystem_size_bytes{device, fstype, mountpoint}
node_filesystem_avail_bytes{device, fstype, mountpoint}
system_disk_usage_percent

# Network
node_network_receive_bytes_total{device}
node_network_transmit_bytes_total{device}
```

### Container Metrics
```
# Container resources
container_cpu_usage_seconds_total{name, image}
container_memory_usage_bytes{name, image}
container_spec_memory_limit_bytes{name, image}
```

## Alerting Rules

### Critical Alerts
- **DexAgent Backend Down**: Backend service unavailable > 1 minute
- **PostgreSQL Down**: Database unavailable > 1 minute
- **Low Disk Space**: Disk usage > 90%

### Warning Alerts
- **High CPU Usage**: CPU usage > 80% for 5 minutes
- **High Memory Usage**: Memory usage > 85% for 5 minutes
- **High API Error Rate**: 5xx errors > 10% for 5 minutes
- **Slow API Response**: 95th percentile > 2 seconds
- **Disconnected Agents**: Agents offline > 5 minutes
- **Failed Commands**: Command failure rate > 10%

### Container Alerts
- **Container High CPU**: Container CPU > 80%
- **Container High Memory**: Container memory > 85%

## Alert Channels

### Slack Integration
```yaml
# Configure in alerts/alertmanager.yml
slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#dexagent-alerts'
```

### Email Notifications
```yaml
# Configure in alerts/alertmanager.yml
email_configs:
  - to: 'admin@example.com'
    subject: '[CRITICAL] DexAgent Alert'
```

## Configuration

### Adding New Metrics

1. **Backend Metrics**: Add to `apps/backend/app/api/metrics.py`
2. **Prometheus Config**: Update `prometheus/config/prometheus.yml`
3. **Dashboard Queries**: Modify Grafana dashboard JSON files

### Custom Dashboards

1. Create dashboard in Grafana UI
2. Export JSON from Grafana
3. Save to `grafana/provisioning/dashboards/files/`
4. Restart Grafana service

### Alert Rules

1. Edit `prometheus/rules/dexagent.yml`
2. Add new alert rules following existing patterns
3. Restart Prometheus service

## Troubleshooting

### Common Issues

**Prometheus Targets Down**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check service logs
docker-compose -f monitoring/docker-compose.monitoring.yml logs prometheus
```

**Grafana Dashboard Not Loading**
```bash
# Check Grafana logs
docker-compose -f monitoring/docker-compose.monitoring.yml logs grafana

# Verify provisioning
docker exec dexagent-grafana ls -la /etc/grafana/provisioning/
```

**Missing Metrics**
```bash
# Test metrics endpoint
curl http://localhost:8080/api/v1/metrics

# Check backend logs
docker-compose logs backend
```

### Performance Tuning

**Prometheus Storage**
- Default retention: 15 days
- Adjust in docker-compose.monitoring.yml: `--storage.tsdb.retention.time=30d`

**Grafana Performance**
- Reduce dashboard refresh rates for better performance
- Use time range limits on queries

**Scrape Intervals**
- Default: 15s for most targets
- Adjust based on load and requirements

## Security Considerations

### Access Control
- Grafana admin credentials: Change default admin/admin123
- Network access: Restrict monitoring ports in production
- API authentication: Secure metrics endpoints if needed

### Data Retention
- Prometheus data: 15 days default
- Grafana logs: Rotate regularly
- Alert history: Configure retention in AlertManager

## Maintenance

### Regular Tasks
- **Weekly**: Review alert rules and thresholds
- **Monthly**: Check disk usage and retention policies
- **Quarterly**: Update monitoring stack versions

### Backup
```bash
# Backup Grafana dashboards
docker exec dexagent-grafana grafana-cli admin export-dashboard

# Backup Prometheus config
cp -r monitoring/prometheus/ backup/prometheus-$(date +%Y%m%d)
```

### Updates
```bash
# Update monitoring stack
docker-compose -f monitoring/docker-compose.monitoring.yml pull
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

## Integration with CI/CD

Monitoring stack is integrated with the main development workflow:

- **Make Commands**: `make monitor-up`, `make monitor-down`, `make monitor-logs`
- **GitHub Actions**: Automated monitoring validation
- **Health Checks**: Integrated with deployment pipeline

For more information, see the main project documentation.