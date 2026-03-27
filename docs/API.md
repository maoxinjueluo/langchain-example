# API 文档（MVP）

## 鉴权与页面

- `GET /register` 注册页
- `POST /register` 注册提交
- `GET /verify?token=...` 邮箱验证
- `GET /login` 登录页
- `POST /login` 登录
- `POST /logout` 登出
- `GET /forgot` 忘记密码页
- `POST /forgot` 发起重置
- `GET /reset?token=...` 重置页
- `POST /reset` 提交新密码

## 知识库管理

- `GET /kb` 知识库列表（支持 `keyword/category/tag`）
- `POST /kb` 新建知识库（name/visibility/description/category/tags）
- `GET /kb/{kb_id}` 知识库详情
- `POST /kb/{kb_id}/update` 更新知识库
- `POST /kb/{kb_id}/delete` 删除知识库
- `POST /kb/{kb_id}/upload` 上传文档（TXT/PDF/DOCX, <=50MB）
- `POST /kb/{kb_id}/documents/{document_id}/delete` 删除文档

## 智能问答

- `GET /chat` 问答页面
- `POST /chat/send` 发送问题（message/knowledge_base_id/conversation_id）
- `POST /chat/favorite` 收藏回答（message_id）
- `POST /chat/feedback` 反馈（message_id/is_helpful/reason）

## 系统

- `GET /health` 服务健康检查

