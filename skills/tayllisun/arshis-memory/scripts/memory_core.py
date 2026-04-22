#!/usr/bin/env python3
"""
memory-pro-custom - Phase 1: 基础记忆功能
支持：
- 调用 Jina / SiliconFlow API 获取嵌入向量
- 存储到 LanceDB
- 向量 + BM25 混合检索
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import numpy as np

# 尝试导入 lancedb 和 bm25
try:
    import lancedb
    HAS_LANCEDB = True
except ImportError:
    HAS_LANCEDB = False
    print("WARNING: lancedb not installed, using JSON fallback")

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("WARNING: rank_bm25 not installed, BM25 disabled")


class MemoryAPI:
    """记忆 API 核心类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embedding_config = config.get('embedding', {})
        self.retrieval_config = config.get('retrieval', {})
        self.llm_config = config.get('llm', {})
        self.db_path = config.get('dbPath', '~/.openclaw/data/memory-custom')
        self.db_path = os.path.expanduser(self.db_path)
        
        # Rerank 配置
        self.rerank_enabled = self.retrieval_config.get('rerank', 'none') != 'none'
        self.rerank_provider = self.retrieval_config.get('rerankProvider', 'siliconflow')
        self.rerank_model = self.retrieval_config.get('rerankModel', 'BAAI/bge-reranker-v2-m3')
        # 优先使用 rerankApiKey，否则使用 embedding 的 apiKey
        self.rerank_api_key = self.retrieval_config.get('rerankApiKey') or self.embedding_config.get('apiKey', '')
        # base_url 不包含 /rerank，调用时再拼接
        self.rerank_base_url = self.retrieval_config.get('rerankEndpoint', 'https://api.siliconflow.cn/v1').rstrip('/')
        
        # 初始化数据库
        self.db = None
        self.table = None
        self.bm25 = None
        self.documents = []
        
        # 强制使用 JSON 模式（LanceDB schema 问题待修复）
        global HAS_LANCEDB
        HAS_LANCEDB = False
        
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        if HAS_LANCEDB:
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)
            
            # 检查表是否存在
            try:
                table_names = self.db.list_tables()
            except:
                table_names = []
            
            # 尝试打开表，不存在则创建
            try:
                self.table = self.db.open_table('memories')
            except:
                # 创建新表 - 使用 pa.schema 定义向量维度
                import pyarrow as pa
                
                schema = pa.schema([
                    pa.field('id', pa.string()),
                    pa.field('text', pa.string()),
                    pa.field('vector', pa.list_(pa.float32(), self.embedding_config.get('dimensions', 1024))),
                    pa.field('metadata', pa.string()),
                    pa.field('created_at', pa.int64()),
                    pa.field('importance', pa.float64()),
                    pa.field('category', pa.string()),
                    pa.field('memory_range', pa.string())
                ])
                
                self.table = self.db.create_table('memories', schema=schema)
        else:
            # JSON fallback
            self.db_file = os.path.join(self.db_path, 'memories.json')
            self._load_json_db()
    
    def _load_json_db(self):
        """加载 JSON 数据库"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        else:
            self.documents = []
        
        # 初始化 BM25
        if HAS_BM25 and self.documents:
            texts = [doc.get('text', '') for doc in self.documents]
            tokenized = [text.split() for text in texts]
            self.bm25 = BM25Okapi(tokenized)
    
    def _save_json_db(self):
        """保存 JSON 数据库"""
        os.makedirs(self.db_path, exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取嵌入向量"""
        provider = self.embedding_config.get('provider', 'jina')
        api_key = self.embedding_config.get('apiKey', os.environ.get('JINA_API_KEY', ''))
        model = self.embedding_config.get('model', 'jina-embeddings-v5-text-small')
        base_url = self.embedding_config.get('baseURL', 'https://api.jina.ai/v1')
        dimensions = self.embedding_config.get('dimensions', 1024)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'input': [text]
        }
        
        # Jina 特有参数
        if provider == 'jina':
            payload['task'] = 'retrieval.passage'
            payload['dimensions'] = dimensions
        
        response = requests.post(
            f'{base_url}/embeddings',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f'Embedding API error: {response.status_code} - {response.text}')
        
        result = response.json()
        embedding = result['data'][0]['embedding']
        
        # 确保维度正确
        if len(embedding) != dimensions:
            print(f"WARNING: Expected {dimensions} dims, got {len(embedding)}")
        
        return embedding
    
    def _generate_id(self, text: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def store(self, text: str, metadata: Optional[Dict] = None, importance: float = 0.5, category: str = '其他') -> Dict[str, Any]:
        """存储记忆"""
        mem_id = self._generate_id(text)
        embedding = self._get_embedding(text)
        
        # 确保向量是 float32 列表
        vector_float32 = [float(x) for x in embedding]
        
        # 根据重要性确定记忆范围
        if importance >= 0.7:
            memory_range = 'core'
        elif importance >= 0.4:
            memory_range = 'working'
        else:
            memory_range = 'peripheral'
        
        memory = {
            'id': mem_id,
            'text': text,
            'vector': vector_float32,
            'metadata': json.dumps(metadata or {}),
            'created_at': int(time.time()),
            'importance': importance,
            'category': category,
            'memory_range': memory_range,
            'recall_count': 0  # 被检索次数
        }
        
        if HAS_LANCEDB and self.table:
            self.table.add([memory])
        else:
            # JSON fallback - 检查是否已存在
            existing = next((i for i, doc in enumerate(self.documents) if doc['id'] == mem_id), None)
            if existing is not None:
                self.documents[existing] = memory
            else:
                self.documents.append(memory)
            # 只有初始化了 db_file 才保存
            if hasattr(self, 'db_file'):
                self._save_json_db()
        
        return {'id': mem_id, 'status': 'stored', 'text': text[:50] + '...'}
    
    def recall(self, query: str, limit: int = 5, memory_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        检索记忆
        
        Args:
            query: 搜索关键词
            limit: 返回数量限制
            memory_range: 记忆范围过滤 (core/working/peripheral/None)
        """
        # 获取查询向量
        query_embedding = self._get_embedding(query)
        
        if HAS_LANCEDB and self.table:
            # LanceDB 向量搜索
            search_result = self.table.search(query_embedding).limit(limit * 3)  # 多取一些用于过滤
            results = search_result.to_list()
            # LanceDB 返回的 score 可能是 distance（越小越好），需要转换
            for r in results:
                if '_distance' in r:
                    r['score'] = 1.0 / (1.0 + r['_distance'])
                elif '_score' in r:
                    r['score'] = r['_score']
                else:
                    r['score'] = 0.0
            
            # 按记忆范围过滤
            if memory_range:
                results = [r for r in results if r.get('memory_range') == memory_range]
        else:
            # 计算余弦相似度
            results = []
            for doc in self.documents:
                doc_vector = np.array(doc['vector'])
                query_vec = np.array(query_embedding)
                
                # 余弦相似度
                similarity = np.dot(doc_vector, query_vec) / (
                    np.linalg.norm(doc_vector) * np.linalg.norm(query_vec)
                )
                
                results.append({
                    **doc,
                    'score': float(similarity)
                })
            
            # 排序并取前 limit 个
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:limit]
        
        # 混合检索：如果有 BM25，可以融合分数
        if HAS_BM25 and self.documents and self.retrieval_config.get('mode') == 'hybrid':
            # BM25 分数
            tokenized_query = query.split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # 融合分数（简单加权）
            vector_weight = self.retrieval_config.get('vectorWeight', 0.7)
            bm25_weight = self.retrieval_config.get('bm25Weight', 0.3)
            
            for result in results:
                # 找到对应的 BM25 分数
                doc_idx = next((i for i, doc in enumerate(self.documents) if doc['id'] == result['id']), None)
                if doc_idx is not None:
                    result['bm25_score'] = float(bm25_scores[doc_idx])
                    result['score'] = vector_weight * result['score'] + bm25_weight * result['bm25_score']
        
        # 按 score 排序并限制数量
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Rerank 重排序（如果启用）
        if self.rerank_enabled:
            results = self._rerank(query, results, limit * 2)  # rerank 后多取一些
        
        results = results[:limit]
        
        # 增加检索次数（使用频率增强）
        for r in results:
            r['recall_count'] = r.get('recall_count', 0) + 1
            # 更新存储中的检索次数（JSON 模式）
            if not HAS_LANCEDB:
                for doc in self.documents:
                    if doc['id'] == r['id']:
                        doc['recall_count'] = r['recall_count']
                self._save_json_db()
        
        # 格式化结果
        formatted = []
        for r in results:
            formatted.append({
                'id': r['id'],
                'text': r['text'],
                'score': r.get('score', 0),
                'metadata': r.get('metadata', {}),
                'created_at': r.get('created_at', 0),
                'importance': r.get('importance', 0.5),
                'memory_range': r.get('memory_range', 'working'),
                'recall_count': r.get('recall_count', 0)
            })
        
        return formatted
    
    def _rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        使用 Cross-Encoder Rerank 重排序
        
        Args:
            query: 查询文本
            results: 候选结果列表
            top_k: 返回前 K 个结果
        
        Returns:
            重排序后的结果
        """
        if not self.rerank_enabled or len(results) == 0:
            return results[:top_k]
        
        try:
            # 准备 rerank 请求
            headers = {
                'Authorization': f'Bearer {self.rerank_api_key}',
                'Content-Type': 'application/json'
            }
            
            documents = [r['text'] for r in results]
            
            payload = {
                'model': self.rerank_model,
                'query': query,
                'documents': documents,
                'top_n': len(documents)  # 先全部 rerank，再截断
            }
            
            response = requests.post(
                f'{self.rerank_base_url}/rerank',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Rerank API 错误：{response.status_code}")
                return results[:top_k]
            
            rerank_result = response.json()
            reranked = rerank_result.get('results', [])
            
            # 将 rerank 分数合并到原结果
            for item in reranked:
                index = item.get('index', 0)
                score = item.get('relevance_score', 0)  # SiliconFlow 返回 relevance_score
                if index < len(results):
                    # 综合分数：60% rerank + 40% 原向量分数
                    original_score = results[index].get('score', 0)
                    results[index]['rerank_score'] = score
                    results[index]['score'] = 0.6 * score + 0.4 * original_score
            
            # 按新分数排序
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Rerank 失败：{e}，使用原结果")
            return results[:top_k]
    
    def delete(self, memory_id: str) -> Dict[str, Any]:
        """删除记忆"""
        if HAS_LANCEDB and self.table:
            self.table.delete(f"id = '{memory_id}'")
        else:
            self.documents = [d for d in self.documents if d['id'] != memory_id]
            self._save_json_db()
        
        return {'id': memory_id, 'status': 'deleted'}
    
    def list_memories(self, limit: int = 20) -> List[Dict[str, Any]]:
        """列出所有记忆"""
        if HAS_LANCEDB and self.table:
            results = self.table.search([0] * 1024).limit(limit).to_list()
        else:
            results = self.documents[:limit]
        
        return [{
            'id': r['id'],
            'text': r['text'][:100] + '...',
            'created_at': r.get('created_at', 0)
        } for r in results]
    
    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        if HAS_LANCEDB and self.table:
            count = self.table.count_rows()
        else:
            count = len(self.documents)
        
        return {
            'total_memories': count,
            'db_path': self.db_path,
            'embedding_model': self.embedding_config.get('model', 'unknown'),
            'lancedb_enabled': HAS_LANCEDB,
            'bm25_enabled': HAS_BM25
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python memory_core.py <command> [args]")
        print("Commands: store, recall, delete, list, stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 从环境变量或配置文件加载配置
    config = {
        'embedding': {
            'provider': os.environ.get('MEMORY_EMBEDDING_PROVIDER', 'jina'),
            'apiKey': os.environ.get('JINA_API_KEY', ''),
            'model': os.environ.get('MEMORY_EMBEDDING_MODEL', 'jina-embeddings-v5-text-small'),
            'baseURL': os.environ.get('MEMORY_EMBEDDING_BASEURL', 'https://api.jina.ai/v1'),
            'dimensions': int(os.environ.get('MEMORY_EMBEDDING_DIMS', '1024'))
        },
        'retrieval': {
            'mode': 'hybrid',
            'vectorWeight': 0.7,
            'bm25Weight': 0.3
        },
        'dbPath': os.environ.get('MEMORY_DB_PATH', '~/.openclaw/data/memory-custom')
    }
    
    # 尝试从配置文件加载
    config_file = os.path.expanduser('~/.openclaw/data/memory-custom-config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
            # 合并配置
            for key in ['embedding', 'retrieval']:
                if key in file_config:
                    config[key].update(file_config[key])
            if 'dbPath' in file_config:
                config['dbPath'] = file_config['dbPath']
    
    api = MemoryAPI(config)
    
    if command == 'store':
        text = sys.argv[2] if len(sys.argv) > 2 else ''
        importance = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        category = sys.argv[4] if len(sys.argv) > 4 else '其他'
        if not text:
            print("Error: store requires text argument")
            sys.exit(1)
        result = api.store(text, importance=importance, category=category)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'recall':
        query = sys.argv[2] if len(sys.argv) > 2 else ''
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        memory_range = sys.argv[4] if len(sys.argv) > 4 else None
        if not query:
            print("Error: recall requires query argument")
            sys.exit(1)
        results = api.recall(query, limit, memory_range)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif command == 'delete':
        memory_id = sys.argv[2] if len(sys.argv) > 2 else ''
        if not memory_id:
            print("Error: delete requires memory_id argument")
            sys.exit(1)
        result = api.delete(memory_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        results = api.list_memories(limit)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif command == 'stats':
        result = api.stats()
        # 添加范围统计
        memories = api.list_memories(1000)
        range_counts = {'core': 0, 'working': 0, 'peripheral': 0}
        for mem in memories:
            range_counts[mem.get('memory_range', 'working')] += 1
        result['memory_ranges'] = range_counts
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
