# user_rules.md

这些是 Trae「个人规则」文件（对所有项目生效）。

来源：
- 个人自定义 UI/UX 基础规则
- GitHub：PatrickJS/awesome-cursorrules（Stars 35121；近 6 个月内有活跃推送）

## UI/UX（基础）

- 可访问性：正文文本与背景对比度至少 4.5:1（大字 3:1），必要时使用对比度工具校验。
- 可访问性：所有可交互元素必须有清晰可见的焦点样式，焦点顺序符合交互逻辑。
- 触摸目标：触摸目标至少 44×44pt（iOS）或 48×48dp（Android），小图标用更大的可点击区域扩展。
- 性能：优先避免卡顿/延迟；优化图片与资源加载；减少布局抖动与重排。
- 响应式：移动优先；使用断点体系；在多尺寸屏幕上验证布局与可用性。

## 通用开发规范（导入规则摘要）

### Code Guidelines

- 在生成/修改代码前，先快速阅读项目中 3–5 个代表性文件，总结命名、结构、错误处理、导入风格、测试方式等，再按既有风格落地。

### Code Style Consistency

- 保持格式化与风格一致；优先使用项目已有的格式化/校验工具与约定。

### Optimize DRY & SOLID Principles

- 遵循 DRY/KISS/SOLID 等原则；优先可读性与可维护性；抽象要“少而准”，避免过度设计。

### Git Conventional Commits

- 提交信息遵循 Conventional Commits：`<type>(<scope>)?: <description>`，必要时包含 body/footer，破坏性变更用 `!` 或 `BREAKING CHANGE:`。

### GitHub Code Quality

- 避免无依据的假设；重要信息应可验证。
- 需要改多文件时，按文件逐个给出改动点，便于审阅。
- 不要输出“抱歉/理解了/总结一下”之类的冗余话术。

### How To Documentation

- 为“怎么做”类文档提供可执行步骤、前置条件、预期结果与失败排查；面向非技术读者时使用清晰语言。

### PR Template

- 提交 PR 时包含：变更目的、范围、风险、测试方式、回滚方案、截图/录屏（如涉及 UI）。

### Engineering Ticket Template

- 需求/工单描述包含：背景、目标、非目标、验收标准、约束条件、边界情况与数据/接口影响。

### Jest Unit Testing

- 新功能/修复需要补充单元测试；覆盖关键路径、边界条件与失败场景。

### Vitest Unit Testing

- 使用 Vitest 时保持测试独立、可重复；避免依赖外部状态；必要时使用 mock/stub。

### Gherkin Style Testing

- 端到端/行为测试用 Given/When/Then 描述用户可感知行为，覆盖关键业务流。

### Web App Optimization

- 优先 Core Web Vitals：避免 CLS；关键资源优先加载；对图片/字体/第三方脚本做优化；避免主线程阻塞。

### Python Developer

- Python 代码尽量清晰、模块化；优先可读性与正确的错误处理；对文件系统/命令行操作保持谨慎。

### Python FastAPI Best Practices

- FastAPI 优先类型标注与 Pydantic 校验；异步 I/O 用 `async`；错误用明确的 HTTP 响应；尽量用 lifespan 替代旧的 startup/shutdown 事件。

### TypeScript Code Convention

- TypeScript 优先严格类型与一致的目录/文件命名；错误处理与验证要明确；性能与可维护性同等重要。

### TypeScript React

- React 组件优先函数组件与 hooks；对 props/state 建立明确类型；需要时用 memo/useMemo/useCallback 控制渲染。

### Go Backend Scalability

- 后端接口与数据层要关注性能、可观测性与可扩展性；缓存/限流/超时/重试策略要明确。

### Java General Purpose

- Java 代码优先清晰的结构与边界；避免过度抽象；对异常与资源释放保持严格。

### C++ Programming Guidelines

- C++ 代码遵循一致的命名与头文件组织；避免魔法数字；必要时使用 Doxygen 注释；关注 ODR 与资源管理。

