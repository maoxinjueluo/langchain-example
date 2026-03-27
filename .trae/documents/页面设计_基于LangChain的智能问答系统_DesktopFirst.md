# 页面设计说明（Desktop-First）

## 0. Global Styles（全局）
- Layout：桌面优先，主体容器 `max-width: 1200px` 居中；全局使用 Flexbox + 局部 Grid（列表/卡片）。
- Spacing：8px 基准（8/16/24/32）。
- Typography：正文 14–16px；标题 20/24/28px 分级；等宽字体用于引用片段。
- Color Tokens（示例）：
  - 背景：`#0B1220`（深色）/ `#FFFFFF`（浅色可选）
  - 主色：`#3B82F6`；强调：`#22C55E`；警示：`#EF4444`
  - 边框/分割线：`rgba(148,163,184,0.2)`
- 可访问性：交互元素焦点态清晰（2px outline + offset）；按钮/输入对比度满足 4.5:1。
- Components：Button（primary/secondary/danger）、Input、Select、Modal、Toast、Skeleton、Tag、Table。

## 1. 登录/注册页（/login）
### Meta Information
- Title：登录/注册 - 智能问答系统
- Description：登录后访问知识库问答与对话记录
- OG：标题同上；类型 `website`

### Page Structure
- 两栏布局（Desktop）：左侧产品卖点与示意图区域；右侧卡片式表单。

### Sections & Components
1. 顶部：Logo + 产品名（点击返回首页，若未登录则仍停留登录页）。
2. 表单卡片：
   - Tabs：登录 / 注册
   - 表单项：邮箱、密码（注册可增加“确认密码”）
   - 主按钮：登录/注册（加载态禁用）
   - 次操作：忘记密码（跳转或弹窗说明）
   - 错误提示：表单下方红色文案 + aria-live

## 2. 首页（智能问答）（/）
### Meta Information
- Title：首页 - 智能问答
- Description：选择知识库并发起问答，查看引用来源
- OG：标题同上

### Page Structure
- 顶部导航 + 主体三栏（Desktop）：左侧会话列表、中间聊天区、右侧引用/知识库信息。
- 响应式：>=1024px 三栏；768–1023px 变双栏（隐藏右侧为抽屉）；<768px（未来）变单栏。

### Sections & Components
1. Top Nav（固定）：
   - 左：Logo
   - 中：知识库选择器（Select，下拉展示你可访问的知识库）
   - 右：账户菜单（设置/退出）
2. 左侧栏（Conversations）：
   - 新建会话按钮
   - 会话列表（标题 + 时间）；选中高亮
   - 会话操作：删除（确认弹窗）
3. 中间聊天区（Chat）：
   - 消息列表（user/assistant 气泡区分）
   - assistant 消息块：回答正文 + “引用”折叠面板入口 + 反馈按钮（有用/无用）
   - 输入区：多行输入框 + 发送按钮；Enter 发送、Shift+Enter 换行
4. 右侧栏（Citations & KB）：
   - 当前知识库简介卡片
   - 引用列表：每条显示文档标题、片段摘要、定位按钮（打开片段弹窗）
   - 片段弹窗：展示更长上下文、来源信息（文件名/页码/段落索引等）

## 3. 知识库管理页（/kb、/kb/:id）
### Meta Information
- Title：知识库管理 - 智能问答系统
- Description：创建知识库、上传文档、查看处理状态

### Page Structure
- 标准后台布局：左侧二级导航（知识库/文档）+ 右侧内容区；内容区使用 Table + Drawer/Modal。

### Sections & Components
1. 知识库列表（/kb）：
   - Header：页面标题 + “新建知识库”按钮
   - Table：名称、可见范围、文档数、更新时间、操作（进入/编辑/删除）
2. 知识库详情（/kb/:id）：
   - 顶部：面包屑（知识库管理 / 当前知识库）
   - 配置区（Card）：名称、描述、可见范围（Select）；保存按钮
   - 文档区：
     - 上传组件：拖拽上传 + 选择文件按钮（显示支持格式）
     - 文档表：文件名、状态（Tag）、片段数、更新时间、操作（删除/查看）
     - 状态说明：失败时展示失败原因与重试入口

## 4. 账户与设置页（/settings）
### Meta Information
- Title：账户与设置 - 智能问答系统
- Description：账号信息、角色与数据管理

### Page Structure
- 单列内容 + 分组卡片（Account / Privacy）。

### Sections & Components
1. Account Card：邮箱（只读）、角色（只读）、修改密码入口、退出登录。
2. Privacy Card：
   - 导出对话记录（按钮，提示生成后下载）
   - 删除对话记录（危险操作，二次确认）
3. 说明区：数据使用与知识库答案免责声明（短文）。
