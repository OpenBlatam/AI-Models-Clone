# Cybersecurity Security Toolkit

A comprehensive Python toolkit for cybersecurity operations including scanning, enumeration, offensive testing, and reporting.

## 🏗️ Module Structure

```
cybersecurity_security/
├── scanners/                  # Security scanning modules
│   ├── __init__.py
│   ├── port_scanner.py        # Port scanning capabilities
│   ├── vulnerability_scanner.py # Vulnerability scanning
│   └── web_scanner.py         # Web application scanning
├── enumerators/               # Service enumeration modules
│   ├── __init__.py
│   ├── dns_enumerator.py      # DNS enumeration
│   ├── smb_enumerator.py      # SMB enumeration
│   └── ssh_enumerator.py      # SSH enumeration
├── attackers/                 # ⚔️ Offensive security testing
│   ├── __init__.py
│   ├── brute_forcers.py       # Brute force attack capabilities
│   └── exploiters.py          # Exploit development & testing
├── reporting/                 # 📋 Comprehensive reporting
│   ├── __init__.py
│   ├── console_reporter.py    # Console-based reporting
│   ├── html_reporter.py       # HTML report generation
│   ├── json_reporter.py       # JSON data export
│   └── report_aggregator.py   # Report aggregation & analysis
├── validators/                # Input validation & sanitization
├── crypto/                    # Cryptographic operations
├── logging/                   # Security logging & monitoring
├── web/                       # Web application security
├── intelligence/              # Threat intelligence
├── testing/                   # Security testing framework
├── examples/                  # Usage examples
│   ├── usage_examples.py
│   ├── scanner_examples.py
│   ├── enumerator_examples.py
│   ├── attacker_examples.py   # ⚔️ Attacker examples
│   └── reporting_examples.py  # 📋 Reporting examples
├── tests/                     # Comprehensive test suite
│   ├── test_validators.py
│   ├── test_network.py
│   ├── test_scanners.py
│   ├── test_enumerators.py
│   ├── test_attackers.py      # ⚔️ Attacker tests
│   └── test_reporting.py      # 📋 Reporting tests
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from cybersecurity_security.scanners import perform_port_scan_async
from cybersecurity_security.enumerators import perform_dns_enumeration_async
from cybersecurity_security.attackers import perform_ssh_brute_force_async
from cybersecurity_security.reporting import generate_html_report_async

async def security_assessment():
    # 1. Port scanning
    port_result = await perform_port_scan_async({
        "target_host": "192.168.1.1",
        "port_range": "1-1000"
    })
    
    # 2. DNS enumeration
    dns_result = await perform_dns_enumeration_async({
        "target_domain": "example.com",
        "record_types": ["A", "MX", "NS"]
    })
    
    # 3. SSH brute force (authorized testing only)
    ssh_result = await perform_ssh_brute_force_async({
        "target_host": "192.168.1.1",
        "username_list": ["admin", "root"],
        "password_list": ["password", "123456"]
    })
    
    # 4. Generate comprehensive report
    report_result = await generate_html_report_async({
        "scan_results": {"scans": [port_result]},
        "enumeration_data": {"dns": dns_result},
        "attack_data": {"ssh_brute_force": ssh_result},
        "template": "modern",
        "include_charts": True
    })
    
    return report_result

# Run assessment
result = asyncio.run(security_assessment())
```

## 📋 Reporting Capabilities

### Console Reporting
```python
from cybersecurity_security.reporting import generate_console_report_async

console_report = await generate_console_report_async({
    "scan_results": scan_data,
    "vulnerability_data": vuln_data,
    "color_output": True,
    "include_details": True
})
```

### HTML Reporting
```python
from cybersecurity_security.reporting import generate_html_report_async

html_report = await generate_html_report_async({
    "scan_results": scan_data,
    "vulnerability_data": vuln_data,
    "template": "modern",
    "include_charts": True,
    "include_timeline": True
})
```

### JSON Reporting
```python
from cybersecurity_security.reporting import generate_json_report_async

json_report = await generate_json_report_async({
    "scan_results": scan_data,
    "vulnerability_data": vuln_data,
    "format": "detailed",
    "include_metadata": True,
    "include_statistics": True
})
```

### Report Aggregation
```python
from cybersecurity_security.reporting import aggregate_reports_async

comprehensive_report = await aggregate_reports_async({
    "scan_results": scan_data,
    "vulnerability_data": vuln_data,
    "enumeration_data": enum_data,
    "attack_data": attack_data,
    "output_format": "comprehensive",
    "include_raw_data": True
})
```

## ⚔️ Attacker Modules

### Brute Force Attacks
```python
from cybersecurity_security.attackers import perform_ssh_brute_force_async

ssh_attack = await perform_ssh_brute_force_async({
    "target_host": "192.168.1.1",
    "username_list": ["admin", "root"],
    "password_list": ["password", "123456"],
    "max_concurrent_attempts": 5
})
```

### Exploit Development
```python
from cybersecurity_security.attackers import perform_sql_injection_exploit_async

sql_exploit = await perform_sql_injection_exploit_async({
    "target_url": "http://192.168.1.1/vulnerable.php",
    "parameter": "id",
    "injection_type": "union",
    "payload": "' UNION SELECT 1,2,3--"
})
```

## 🔍 Scanner Modules

### Port Scanning
```python
from cybersecurity_security.scanners import perform_port_scan_async

port_scan = await perform_port_scan_async({
    "target_host": "192.168.1.1",
    "port_range": "1-1000",
    "scan_type": "tcp",
    "timeout": 10.0
})
```

### Vulnerability Scanning
```python
from cybersecurity_security.scanners import perform_vulnerability_scan_async

vuln_scan = await perform_vulnerability_scan_async({
    "target_url": "http://192.168.1.1",
    "scan_types": ["sql_injection", "xss", "csrf"],
    "custom_payloads": True
})
```

### Web Application Scanning
```python
from cybersecurity_security.scanners import perform_web_scan_async

web_scan = await perform_web_scan_async({
    "target_url": "http://192.168.1.1",
    "scan_options": {
        "directory_enumeration": True,
        "robots_txt": True,
        "security_headers": True,
        "ssl_certificate": True
    }
})
```

## 🔍 Enumerator Modules

### DNS Enumeration
```python
from cybersecurity_security.enumerators import perform_dns_enumeration_async

dns_enum = await perform_dns_enumeration_async({
    "target_domain": "example.com",
    "record_types": ["A", "MX", "NS", "TXT"],
    "subdomain_enumeration": True,
    "zone_transfer": True
})
```

### SMB Enumeration
```python
from cybersecurity_security.enumerators import perform_smb_enumeration_async

smb_enum = await perform_smb_enumeration_async({
    "target_host": "192.168.1.1",
    "enumeration_types": ["shares", "users", "policies"],
    "null_session": True
})
```

### SSH Enumeration
```python
from cybersecurity_security.enumerators import perform_ssh_enumeration_async

ssh_enum = await perform_ssh_enumeration_async({
    "target_host": "192.168.1.1",
    "enumeration_types": ["version", "algorithms", "key_exchange"],
    "brute_force": False
})
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest cybersecurity_security/tests/ -v
```

### Test Coverage
- **Validators**: Input validation and sanitization
- **Network**: Network operations and connectivity
- **Scanners**: Port, vulnerability, and web scanning
- **Enumerators**: DNS, SMB, and SSH enumeration
- **Attackers**: Brute force and exploit testing
- **Reporting**: Console, HTML, JSON, and aggregation

## 📊 Report Types

| Report Type | Format | Features | Use Case |
|-------------|--------|----------|----------|
| **Console** | Text | Colored output, real-time | Command line analysis |
| **HTML** | Web | Interactive charts, modern UI | Executive presentations |
| **JSON** | Data | Structured export, APIs | Integration & automation |
| **Aggregated** | Comprehensive | Multi-source analysis | Complete assessments |

## ⚠️ Security & Ethical Considerations

- **Authorized Use Only**: This toolkit is for authorized security testing only
- **Rate Limiting**: Built-in delays to prevent overwhelming targets
- **Responsible Disclosure**: Follow responsible disclosure practices
- **Legal Compliance**: Ensure compliance with local laws and regulations
- **Ethical Usage**: Use only for legitimate security assessments

## 🔧 Configuration

### Environment Variables
```bash
export CYBERSECURITY_TIMEOUT=30
export CYBERSECURITY_MAX_CONCURRENT=10
export CYBERSECURITY_RATE_LIMIT=1.0
```

### Custom Settings
```python
from cybersecurity_security.config import SecurityConfig

config = SecurityConfig(
    timeout=30.0,
    max_concurrent_operations=10,
    rate_limit_delay=1.0,
    enable_logging=True
)
```

## 📈 Performance Metrics

- **Async Operations**: All I/O operations use async/await
- **Concurrent Processing**: Configurable concurrency limits
- **Rate Limiting**: Respectful scanning with built-in delays
- **Memory Efficient**: Streaming data processing for large datasets
- **Scalable**: Horizontal scaling support for distributed assessments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the examples directory

---

**⚠️ WARNING**: This toolkit is for authorized security testing only. Always ensure you have proper authorization before conducting any security assessments. 