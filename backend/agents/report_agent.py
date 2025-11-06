from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, List
import json

class ReportAgent(BaseAgent):
    """Agent for generating analytics and reports"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Generate a report based on data"""
        self._log(f"Generating report: {input_data.context.get('report_type', 'unknown')}")
        
        try:
            report = await self._generate_report(input_data.context)
            
            return AgentOutput(
                success=True,
                result=report,
                metadata={"report_type": input_data.context.get('report_type')}
            )
        except Exception as e:
            self._log(f"Report generation failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytical report"""
        
        report_type = context.get('report_type', 'summary')
        data = context.get('data', {})
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a data analyst for a hiring platform. Generate insightful reports.
                
                For {report_type} reports, provide:
                - Key metrics and trends
                - Insights and patterns
                - Actionable recommendations
                - Visual data suggestions
                
                Return JSON:
                {{
                  "title": "report title",
                  "summary": "executive summary",
                  "key_metrics": [{{"metric": "name", "value": value, "trend": "up/down/stable"}}],
                  "insights": ["insight1", "insight2"],
                  "recommendations": ["recommendation1", "recommendation2"],
                  "charts": [{{"type": "bar/line/pie", "title": "chart title", "data": {{}}}}]
                }}
                """
            },
            {
                "role": "user",
                "content": f"""Generate a {report_type} report from this data:
                
                {json.dumps(data, indent=2)}
                
                Additional context:
                {json.dumps(context.get('additional_context', {}), indent=2)}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.5)
        return result
