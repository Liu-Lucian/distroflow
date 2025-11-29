"""
SEO监测与优化模块
功能：性能追踪 → 优化机会识别 → AI建议生成
"""

import os
import json
from typing import Dict, List
from datetime import datetime, timedelta
from openai import OpenAI

class SEOMonitor:
    """SEO监测与持续优化工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def generate_performance_report(self, published_content: List[Dict]) -> Dict:
        """
        生成性能报告

        指标：
        - 总内容数
        - 平均字数
        - 覆盖关键词数
        - 内链密度
        """
        if not published_content:
            return {}

        total_content = len(published_content)
        total_words = sum(
            len(item.get('content', '').split())
            for item in published_content
        )
        avg_words = total_words // total_content if total_content > 0 else 0

        # 统计关键词
        all_keywords = set()
        for item in published_content:
            keywords = item.get('topic', {}).get('keywords', [])
            all_keywords.update(keywords)

        report = {
            'total_content': total_content,
            'total_words': total_words,
            'avg_words_per_article': avg_words,
            'unique_keywords_covered': len(all_keywords),
            'content_by_type': self._group_by_type(published_content),
            'content_by_funnel_stage': self._group_by_funnel(published_content),
            'generated_at': datetime.now().isoformat()
        }

        return report

    def find_optimization_opportunities(self, published_content: List[Dict]) -> List[Dict]:
        """
        识别优化机会

        机会类型：
        1. 内容刷新（旧内容需要更新）
        2. 内容扩展（短内容可以加长）
        3. 关键词机会（可以targeting更多关键词）
        4. 技术优化（缺少Schema等）
        """
        opportunities = []

        for item in published_content:
            # 检查内容长度
            content = item.get('content', '')
            word_count = len(content.split())

            if word_count < 1000:
                opportunities.append({
                    'type': 'content_expansion',
                    'content_id': item.get('id', ''),
                    'title': item.get('topic', {}).get('title', ''),
                    'current_words': word_count,
                    'recommendation': f'Expand to 1500-2000 words',
                    'priority': 'medium'
                })

            # 检查Schema
            if not item.get('schema'):
                opportunities.append({
                    'type': 'technical_seo',
                    'content_id': item.get('id', ''),
                    'title': item.get('topic', {}).get('title', ''),
                    'recommendation': 'Add Schema.org markup',
                    'priority': 'high'
                })

            # 检查发布日期（简化版）
            published_at = item.get('published_at', '')
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at)
                    if datetime.now() - pub_date > timedelta(days=180):
                        opportunities.append({
                            'type': 'content_refresh',
                            'content_id': item.get('id', ''),
                            'title': item.get('topic', {}).get('title', ''),
                            'published_date': published_at,
                            'recommendation': 'Update with latest information and current year',
                            'priority': 'high'
                        })
                except:
                    pass

        return opportunities

    def generate_optimization_suggestions(self, opportunities: List[Dict]) -> List[Dict]:
        """
        AI生成优化建议

        为每个机会生成具体的行动步骤
        """
        suggestions = []

        for opp in opportunities[:10]:  # 限制前10个
            prompt = f"""You are an SEO optimization expert. Generate specific action steps for this optimization opportunity:

**Type**: {opp['type']}
**Content**: {opp['title']}
**Recommendation**: {opp['recommendation']}

Provide:
1. 3-5 specific action steps
2. Estimated time required
3. Expected impact (low/medium/high)
4. Resources needed

Return ONLY valid JSON:
{{
  "action_steps": ["step1", "step2", ...],
  "estimated_hours": 2,
  "expected_impact": "medium",
  "resources": ["tool1", "tool2"],
  "notes": "Additional context..."
}}
"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an SEO expert. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )

                response_text = response.choices[0].message.content.strip()
                response_text = self._extract_json(response_text)
                suggestion = json.loads(response_text)

                # 合并机会信息
                suggestion.update(opp)
                suggestions.append(suggestion)

            except Exception as e:
                print(f"   ⚠️  Suggestion generation failed for {opp['title']}: {e}")
                continue

        return suggestions

    def _group_by_type(self, content: List[Dict]) -> Dict[str, int]:
        """按内容类型分组"""
        types = {}
        for item in content:
            content_type = item.get('topic', {}).get('content_type', 'unknown')
            types[content_type] = types.get(content_type, 0) + 1
        return types

    def _group_by_funnel(self, content: List[Dict]) -> Dict[str, int]:
        """按漏斗阶段分组"""
        stages = {}
        for item in content:
            funnel_stage = item.get('topic', {}).get('funnel_stage', 'unknown')
            stages[funnel_stage] = stages.get(funnel_stage, 0) + 1
        return stages

    def _extract_json(self, text: str) -> str:
        """提取JSON"""
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        return text
