# 数据库设计（SQLite）

数据库文件：`db/app.db`

## 通用字段（BaseModel）

- `id`: 主键 UUID 字符串
- `created_at`
- `updated_at`
- `status`（1=有效, 0=删除）
- `json_extend`

## 认证模块

- `auth_users`
  - `email`（唯一）
  - `name`
  - `password_hash`
  - `role`（user/admin/superadmin）
  - `is_email_verified`
- `email_verification_tokens`
  - `user_id`, `token_hash`, `expires_at`, `used_at`
- `password_reset_tokens`
  - `user_id`, `token_hash`, `expires_at`, `used_at`
- `user_sessions`
  - `user_id`, `token_hash`, `remember_me`, `expires_at`, `user_agent`

## 知识库模块

- `knowledge_bases`
  - `name`, `description`, `category`
  - `visibility`（private/org）
  - `owner_user_id`, `version`, `permission_level`
- `kb_documents`
  - `knowledge_base_id`
  - `title`, `storage_path`, `md5`, `size_bytes`
  - `processing_status`（uploaded/chunking/embedding/ready/failed）
  - `version`, `file_ext`, `mime_type`, `error_message`
  - 唯一约束：`(knowledge_base_id, md5)`
- `kb_tags`
  - `name`（唯一）
- `knowledge_base_tags`
  - `knowledge_base_id`, `tag_id`
- `doc_chunks`
  - `knowledge_base_id`, `document_id`, `chunk_index`
  - `content`, `embedding`（可空，主向量在 Chroma）
  - `metadata`

## 问答模块

- `conversations`
  - `user_id`, `knowledge_base_id`, `title`
- `messages`
  - `conversation_id`, `role`, `content`
  - `citations`（JSON）, `confidence`
- `favorite_questions`
  - `user_id`, `message_id`
- `answer_feedback`
  - `message_id`, `is_helpful`, `reason`

## 向量存储

- Chroma 持久化目录：`db/chroma`
- Collection 命名：`kb_{knowledge_base_id}`
- Document metadata：`chunk_id/document_id/knowledge_base_id/title/snippet`

