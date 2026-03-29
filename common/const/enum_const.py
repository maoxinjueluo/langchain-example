from enum import Enum, auto


class UserRole(Enum):
    """用户角色枚举"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class KBVisibility(Enum):
    """知识库可见性枚举"""
    PRIVATE = "private"
    PUBLIC = "public"


class KBDocumentStatus(Enum):
    """知识库文档状态枚举"""
    UPLOADED = "uploaded"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    READY = "ready"
    FAILED = "failed"


class KBProcessingStatus(Enum):
    """知识库处理状态枚举"""
    UPLOADED = "uploaded"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    READY = "ready"
    FAILED = "failed"


class MessageRole(Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"


class EmailTemplate(Enum):
    """邮件模板枚举"""
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


class TokenType(Enum):
    """令牌类型枚举"""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    ACCESS = "access"
