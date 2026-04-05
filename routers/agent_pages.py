from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import json
from datetime import datetime
import uuid
import asyncio

from database import get_session
from services.kb.ingest_service import KBIngestService

router = APIRouter()

# 存储执行记录的内存存储（生产环境建议使用数据库）
execution_store = {}

@router.get("/agent/kb-qa", response_class=HTMLResponse)
async def kb_qa_page():
    """智能助手页面"""
    with open("templates/agent/kb_qa.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

@router.post("/api/agent/kb-qa")
async def kb_qa(
    request: Dict[str, Any],
    session: AsyncSession = Depends(get_session)
):
    """提交知识库问答请求"""
    question = request.get("question")
    knowledge_bases = request.get("knowledge_bases", [])
    use_web_search = request.get("use_web_search", False)
    
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    if not knowledge_bases:
        raise HTTPException(status_code=400, detail="至少选择一个知识库")
    
    # 生成执行ID
    execution_id = str(uuid.uuid4())
    
    # 创建执行记录
    execution_store[execution_id] = {
        "id": execution_id,
        "status": "running",
        "steps": [],
        "result": None,
        "sources": []
    }
    
    # 启动异步任务
    asyncio.create_task(process_kb_qa(execution_id, question, knowledge_bases, use_web_search, session))
    
    return {"execution_id": execution_id, "status": "running"}

async def process_kb_qa(execution_id: str, question: str, knowledge_bases: List[str], use_web_search: bool, session: AsyncSession):
    """处理知识库问答请求"""
    execution = execution_store.get(execution_id)
    if not execution:
        return
    
    try:
        # 步骤1：分析用户问题
        execution["steps"].append({
            "id": 1,
            "type": "think",
            "content": "分析用户问题，确定需要查询的信息",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # 步骤2：调用知识库查询工具
        execution["steps"].append({
            "id": 2,
            "type": "tool",
            "content": "调用知识库查询工具",
            "tool_info": {
                "name": "kb_search",
                "params": {
                    "query": question,
                    "knowledge_bases": knowledge_bases
                },
                "result": "正在查询知识库..."
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # 模拟知识库查询结果
        kb_service = KBIngestService(session)
        kb_results = []
        for kb_id in knowledge_bases:
            kb = await kb_service.get_kb(kb_id)
            if kb:
                kb_results.append({
                    "kb_id": kb_id,
                    "kb_name": kb.name,
                    "result": f"从知识库 {kb.name} 中查询到关于 '{question}' 的相关信息..."
                })
        
        # 更新工具调用结果
        execution["steps"][1]["tool_info"]["result"] = str(kb_results)
        
        # 步骤3：调用网络搜索工具（如果启用）
        web_results = []
        if use_web_search:
            execution["steps"].append({
                "id": 3,
                "type": "tool",
                "content": "调用网络搜索工具",
                "tool_info": {
                    "name": "web_search",
                    "params": {
                        "query": question
                    },
                    "result": "正在搜索网络..."
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # 模拟网络搜索结果
            web_results = [
                {
                    "url": "https://example.com/langchain-agent",
                    "title": "LangChain Agent官方文档",
                    "content": "LangChain在2026年推出了新的Agent功能，包括多工具协同、任务规划等..."
                }
            ]
            
            # 更新工具调用结果
            execution["steps"][2]["tool_info"]["result"] = str(web_results)
        
        # 步骤4：整合信息
        execution["steps"].append({
            "id": len(execution["steps"]) + 1,
            "type": "think",
            "content": "整合知识库和网络搜索的信息",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # 步骤5：生成回答
        # 模拟生成回答
        answer = f"关于 '{question}' 的回答：\n\n"
        answer += "基于知识库和网络搜索的信息，我为您整理了以下内容：\n\n"
        answer += "1. 知识库信息：\n"
        for result in kb_results:
            answer += f"   - {result['kb_name']}: {result['result']}\n"
        
        if web_results:
            answer += "\n2. 网络搜索信息：\n"
            for result in web_results:
                answer += f"   - {result['title']}: {result['content']}\n"
        
        answer += "\n以上信息仅供参考，希望对您有所帮助！"
        
        # 更新执行状态
        execution["result"] = answer
        execution["status"] = "completed"
        
        # 构建信息源
        sources = []
        for result in kb_results:
            sources.append({
                "type": "knowledge_base",
                "id": result["kb_id"],
                "title": result["kb_name"]
            })
        
        for result in web_results:
            sources.append({
                "type": "web",
                "url": result["url"],
                "title": result["title"]
            })
        
        execution["sources"] = sources
    except Exception as e:
        # 处理错误
        execution["status"] = "failed"
        execution["steps"].append({
            "id": len(execution["steps"]) + 1,
            "type": "error",
            "content": f"执行失败: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

@router.get("/api/agent/execution/{execution_id}")
async def get_execution(execution_id: str):
    """获取执行状态"""
    execution = execution_store.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    
    return execution

@router.get("/api/agent/knowledge-bases")
async def get_knowledge_bases(session: AsyncSession = Depends(get_session)):
    """获取可用的知识库列表"""
    service = KBIngestService(session)
    kbs = await service.list_kbs()
    
    knowledge_bases = []
    for kb in kbs:
        knowledge_bases.append({
            "id": str(kb.id),
            "name": kb.name,
            "description": kb.description or ""
        })
    
    return {"knowledge_bases": knowledge_bases}