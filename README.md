# langchain-example

一个使用 FastAPI 和 LangChain 构建的用户管理系统示例项目。

## 项目简介

本项目是一个基于 FastAPI 框架的后端服务，提供了完整的用户管理功能，包括用户的创建、查询、更新、删除以及批量操作。同时集成了 LangChain 相关库，为后续的 AI 功能扩展做好了准备。

## 技术栈

- **Python** >= 3.10
- **FastAPI**：现代化的 Python Web 框架
- **SQLAlchemy**：异步 ORM 框架
- **SQLite**：轻量级数据库
- **Pydantic V2**：数据验证和序列化
- **LangChain**：LLM 应用开发框架

## 项目结构

```
langchain-example/
├── app.py                 # 应用主入口
├── database.py            # 数据库配置和初始化
├── requirements.txt       # 项目依赖
├── README.md              # 项目说明文档
├── common/                # 通用常量和工具
│   └── const/             # 常量定义
├── db/                    # 数据库文件
├── manager/               # 数据访问层
│   └── user/              # 用户数据访问
├── models/                # ORM 模型
│   ├── base.py            # 基础模型
│   └── user.py            # 用户模型
├── routers/               # API 路由
│   └── user/              # 用户相关路由
│       ├── request_model/ # 请求模型
│       └── response_model/# 响应模型
└── services/              # 业务逻辑层
    └── user/              # 用户业务逻辑
```

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd langchain-example
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:8000` 启动。

## API 文档

启动应用后，可以通过以下地址访问自动生成的 API 文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 主要功能

### 用户管理 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/users | 创建用户 |
| GET | /api/users | 获取用户列表（支持分页和状态过滤） |
| GET | /api/users/{user_id} | 获取单个用户信息 |
| PATCH | /api/users/{user_id} | 更新用户信息 |
| DELETE | /api/users/{user_id} | 删除用户 |
| POST | /api/users/batch | 批量创建用户 |
| POST | /api/users/batch/query | 批量查询用户 |
| DELETE | /api/users/batch | 批量删除用户 |
| PATCH | /api/users/batch | 批量更新用户 |

### 健康检查

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /health | 检查服务健康状态 |

## 数据模型

### 用户模型

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | int | 用户ID（自增） |
| name | str | 姓名 |
| gender | int | 性别 |
| hobbies | str | 爱好 |
| age | int | 年龄 |
| status | int | 状态 |
| json_extend | dict | JSON 扩展字段 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 开发指南

### 代码风格

- 使用 PEP 8 代码风格
- 使用类型提示
- 遵循 FastAPI 最佳实践

### 测试

项目使用 pytest 进行测试。运行测试：

```bash
pytest
```

## 扩展建议

1. **添加认证和授权**：集成 JWT 或 OAuth2
2. **添加更多业务逻辑**：如用户角色管理、权限控制
3. **集成 LangChain 功能**：如基于用户数据的智能问答、推荐系统
4. **添加缓存**：使用 Redis 提高性能
5. **添加日志和监控**：使用 ELK 或 Prometheus + Grafana

## 许可证

MIT
