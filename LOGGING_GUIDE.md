# 📋 FastAPI Enterprise MVP - 企业级日志系统指南

## 🎯 概述

本项目实现了一个企业级的日志系统，提供结构化日志、性能监控、安全审计和错误追踪等功能。

## 🏗️ 日志架构

### 核心组件

1. **日志配置模块** (`app/core/logging_config.py`)
   - 统一的日志配置管理
   - 多种格式化器（彩色、JSON、详细格式）
   - 环境特定的配置

2. **日志中间件** (`app/middleware/logging_middleware.py`)
   - 请求/响应日志记录
   - 性能监控
   - 安全事件记录
   - 错误追踪

3. **日志装饰器** (`app/utils/logging_decorators.py`)
   - 函数调用日志
   - 性能监控装饰器
   - 错误处理装饰器

4. **专用日志器**
   - 性能日志器
   - 安全日志器
   - 结构化日志器

## 🚀 快速开始

### 1. 基础使用

```python
from app.core.logging_config import get_logger

# 获取日志器
logger = get_logger("my_module")

# 基础日志记录
logger.info("应用启动")
logger.warning("配置项缺失")
logger.error("处理失败", exc_info=True)
```

### 2. 结构化日志

```python
from app.core.logging_config import get_structured_logger

# 获取结构化日志器
logger = get_structured_logger("api")

# 结构化日志记录
logger.info("用户登录", 
           user_id="12345", 
           ip_address="192.168.1.100",
           user_agent="Mozilla/5.0...")
```

### 3. 使用装饰器

```python
from app.utils.logging_decorators import log_function_call, log_performance

@log_function_call(logger_name="services.user")
@log_performance(threshold_ms=100.0)
async def create_user(user_data: dict):
    # 函数实现
    pass
```

## 📊 日志类型和格式

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息记录
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志格式

#### 1. 详细格式 (Development)
```
2024-01-15 10:30:45 [INFO    ] app.main                     : Application started [main.py:25]
```

#### 2. 彩色格式 (Console)
```
10:30:45 [INFO    ] app.main            : Application started
```

#### 3. JSON格式 (Production)
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "Application started",
  "module": "main",
  "function": "startup",
  "line": 25
}
```

## 📁 日志文件结构

```
logs/
├── app.log              # 主应用日志
├── error.log            # 错误日志
├── app.json             # JSON格式日志
├── performance.log      # 性能日志
├── security.log         # 安全日志
└── *.log.1, *.log.2     # 轮转的历史日志
```

## 🔧 配置管理

### 环境配置

#### Development
```python
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "colored"
LOG_TO_FILE = True
```

#### Production
```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"
LOG_TO_FILE = True
LOG_JSON_FORMAT = True
```

#### Testing
```python
LOG_LEVEL = "WARNING"
LOG_TO_FILE = False
```

### 自定义配置

```python
from app.core.config import settings

# 修改日志级别
settings.LOG_LEVEL = "DEBUG"

# 启用性能日志
settings.ENABLE_PERFORMANCE_LOGGING = True

# 启用安全日志
settings.ENABLE_SECURITY_LOGGING = True
```

## 🛡️ 安全日志

### 登录尝试记录

```python
from app.core.logging_config import security_logger

security_logger.log_login_attempt(
    username="alice",
    success=True,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)
```

### 权限拒绝记录

```python
security_logger.log_permission_denied(
    user_id="12345",
    resource="admin_panel",
    action="read"
)
```

### 可疑活动记录

```python
security_logger.log_suspicious_activity(
    description="Multiple failed login attempts",
    user_id="12345",
    ip_address="192.168.1.100"
)
```

## ⚡ 性能日志

### 请求性能记录

```python
from app.core.logging_config import performance_logger

performance_logger.log_request(
    method="POST",
    path="/api/v1/users",
    status_code=201,
    duration_ms=45.2,
    user_id="12345"
)
```

### 数据库查询性能

```python
performance_logger.log_database_query(
    query="SELECT * FROM users WHERE active = true",
    duration_ms=23.5,
    rows_affected=150
)
```

### 外部API调用性能

```python
performance_logger.log_external_api(
    service="payment_gateway",
    endpoint="/api/v1/charge",
    status_code=200,
    duration_ms=1250.0
)
```

## 🔍 日志管理工具

### 使用日志管理脚本

```bash
# 查看所有日志文件
./scripts/log-manager.sh list

# 实时跟踪日志
./scripts/log-manager.sh follow app

# 搜索日志
./scripts/log-manager.sh search "ERROR" app 5

# 分析日志
./scripts/log-manager.sh analyze

# 清理旧日志
./scripts/log-manager.sh clean 7

# 归档日志
./scripts/log-manager.sh archive
```

### 常用命令

```bash
# 查看最近的错误
tail -f logs/error.log

# 查看JSON格式日志
tail -f logs/app.json | jq .

# 搜索特定用户的日志
grep "user_id.*12345" logs/app.log

# 查看性能问题
grep "slow\|timeout" logs/app.log
```

## 📈 监控和告警

### 日志监控指标

1. **错误率**: ERROR级别日志的频率
2. **响应时间**: 请求处理时间分布
3. **安全事件**: 失败登录、权限拒绝等
4. **系统健康**: 应用启动、停止事件

### 告警规则示例

```bash
# 错误率过高告警
if error_count_per_minute > 10:
    send_alert("High error rate detected")

# 响应时间过长告警
if avg_response_time > 2000:
    send_alert("Slow response time detected")

# 安全事件告警
if failed_login_attempts > 5:
    send_alert("Multiple failed login attempts")
```

## 🎨 最佳实践

### 1. 日志内容

✅ **推荐做法**:
```python
logger.info("User created successfully", 
           extra={"user_id": "12345", "username": "alice"})
```

❌ **避免做法**:
```python
logger.info(f"User {password} created")  # 不要记录敏感信息
```

### 2. 日志级别选择

- **DEBUG**: 详细的调试信息，仅在开发环境使用
- **INFO**: 重要的业务事件（用户登录、订单创建等）
- **WARNING**: 可恢复的错误或异常情况
- **ERROR**: 需要关注的错误
- **CRITICAL**: 系统级严重错误

### 3. 结构化日志

```python
# 好的结构化日志
logger.info("Payment processed", extra={
    "payment_id": "pay_123",
    "amount": 99.99,
    "currency": "USD",
    "user_id": "user_456",
    "status": "success"
})
```

### 4. 性能考虑

```python
# 避免在循环中记录过多日志
for item in large_list:
    if len(large_list) > 1000 and item_index % 100 == 0:
        logger.debug(f"Processed {item_index} items")
```

### 5. 敏感信息处理

```python
# 自动过滤敏感信息
safe_data = {k: "[REDACTED]" if k in ["password", "token", "secret"] 
             else v for k, v in user_data.items()}
logger.info("User data processed", extra=safe_data)
```

## 🔧 故障排除

### 常见问题

#### 1. 日志文件未创建
```bash
# 检查目录权限
ls -la logs/
chmod 755 logs/

# 检查磁盘空间
df -h
```

#### 2. 日志级别过高
```python
# 临时降低日志级别
import logging
logging.getLogger("app").setLevel(logging.DEBUG)
```

#### 3. 性能影响
```python
# 在生产环境中避免DEBUG级别
if settings.ENVIRONMENT == "production":
    settings.LOG_LEVEL = "INFO"
```

### 调试技巧

```python
# 临时启用详细日志
logger.setLevel(logging.DEBUG)

# 添加临时日志点
logger.debug(f"Variable value: {variable}")

# 使用结构化日志进行调试
logger.debug("Debug checkpoint", extra={
    "function": "process_data",
    "step": "validation",
    "data_size": len(data)
})
```

## 📚 扩展阅读

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structlog Documentation](https://www.structlog.org/)
- [FastAPI Logging Best Practices](https://fastapi.tiangolo.com/tutorial/logging/)
- [JSON Logging with Python](https://github.com/madzak/python-json-logger)

---

**🎯 记住**: 好的日志系统是应用监控和故障排除的基础。合理使用日志可以大大提高应用的可维护性和可观测性。
