from typing import List, Dict, Any, Union, Optional
import jinja2
import markdown
from datetime import datetime
from app.models.records import WeightRecord, MedicalVisit, VaccineRecord, Deworming
import plotly.io as pio
from io import BytesIO
import pandas as pd
from PIL import Image
import base64
from app.models.settings import ReportTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportGenerator:
    # HTML 模板
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ pet.name }}'s Health Report</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .chart { margin: 20px 0; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; border: 1px solid #ddd; }
            th { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{{ pet.name }}'s Health Report</h1>
            <p>Generated on: {{ generated_date }}</p>
            
            <h2>Basic Information</h2>
            <table>
                <tr><th>Name</th><td>{{ pet.name }}</td></tr>
                <tr><th>Species</th><td>{{ pet.species }}</td></tr>
                <tr><th>Age</th><td>{{ pet_age }}</td></tr>
            </table>

            <h2>Weight Trend</h2>
            <div class="chart">{{ weight_chart | safe }}</div>
            
            <h2>Health Summary</h2>
            {{ health_summary | safe }}
            
            <h2>Recent Medical Records</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Symptoms</th>
                    <th>Diagnosis</th>
                    <th>Treatment</th>
                </tr>
                {% for record in medical_records %}
                <tr>
                    <td>{{ record.date.strftime('%Y-%m-%d') }}</td>
                    <td>{{ record.symptoms }}</td>
                    <td>{{ record.diagnosis }}</td>
                    <td>{{ record.treatment }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>Upcoming Reminders</h2>
            <table>
                <tr><th>Type</th><th>Due Date</th><th>Details</th></tr>
                {% for reminder in reminders %}
                <tr>
                    <td>{{ reminder.type }}</td>
                    <td>{{ reminder.due_date.strftime('%Y-%m-%d') }}</td>
                    <td>{{ reminder.details }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """

    @classmethod
    def generate_report(
        cls,
        pet,
        weight_records: List[WeightRecord],
        medical_records: List[MedicalVisit],
        reminders: List[Dict],
        template: Optional[ReportTemplate] = None,
        format: str = "html"
    ) -> Union[bytes, BytesIO]:
        """生成健康报告"""
        # 准备数据
        weight_chart = create_weight_chart(weight_records)
        weight_chart_html = pio.to_html(weight_chart, full_html=False)
        
        # 使用自定义模板或默认模板
        template_content = template.content if template else cls.HTML_TEMPLATE
        
        # 渲染模板
        template = jinja2.Template(template_content)
        html_content = template.render(
            pet=pet,
            generated_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            pet_age=cls._calculate_pet_age(pet),
            weight_chart=weight_chart_html,
            health_summary=cls._generate_health_summary(weight_records, medical_records),
            medical_records=medical_records[-5:],
            reminders=reminders,
            # 添加更多可用的模板变量
            weight_records=weight_records,
            all_medical_records=medical_records,
            stats=cls._generate_stats(weight_records, medical_records)
        )
        
        # 根据格式返回不同内容
        if format == "html":
            return html_content.encode()
        
        elif format == "markdown":
            # 将HTML转换为Markdown
            from html2text import HTML2Text
            h2t = HTML2Text()
            h2t.ignore_links = False
            markdown_content = h2t.handle(html_content)
            return markdown_content.encode()
        
        elif format == "pdf":
            return cls._generate_pdf(
                pet=pet,
                weight_records=weight_records,
                medical_records=medical_records,
                reminders=reminders
            )
        
        elif format == "excel":
            return cls._generate_excel(
                pet,
                weight_records,
                medical_records,
                reminders
            )
        
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _calculate_pet_age(pet) -> str:
        """计算宠物年龄"""
        if not pet.birth_date:
            return "Unknown"
        
        days = (datetime.utcnow() - pet.birth_date).days
        years = days // 365
        months = (days % 365) // 30
        
        if years > 0:
            return f"{years} years {months} months"
        return f"{months} months"

    @staticmethod
    def _generate_health_summary(weight_records, medical_records) -> str:
        """生成健康总结"""
        summary = []
        
        # 分析体重趋势
        if weight_records:
            latest_weight = weight_records[-1].weight
            if len(weight_records) > 1:
                weight_change = latest_weight - weight_records[-2].weight
                if abs(weight_change) > 0.1:
                    summary.append(
                        f"Weight {'increased' if weight_change > 0 else 'decreased'} "
                        f"by {abs(weight_change):.1f}kg"
                    )
        
        # 分析健康问题
        if medical_records:
            recent_issues = [r.symptoms for r in medical_records[-3:]]
            if recent_issues:
                summary.append("Recent health issues:")
                summary.extend([f"- {issue}" for issue in recent_issues])
        
        return "<br>".join(summary) if summary else "No significant health issues."

    @staticmethod
    def _generate_stats(weight_records, medical_records) -> Dict[str, Any]:
        """生成统计数据"""
        stats = {
            "weight": {
                "current": weight_records[-1].weight if weight_records else None,
                "min": min([r.weight for r in weight_records]) if weight_records else None,
                "max": max([r.weight for r in weight_records]) if weight_records else None,
            },
            "medical": {
                "total_visits": len(medical_records),
                "recent_visits": len([
                    r for r in medical_records
                    if (datetime.utcnow() - r.date).days <= 90
                ])
            }
        }
        return stats

    @staticmethod
    def _generate_excel(pet, weight_records, medical_records, reminders) -> BytesIO:
        """生成Excel报告"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 基本信息sheet
            pd.DataFrame([{
                'Name': pet.name,
                'Species': pet.species,
                'Birth Date': pet.birth_date,
                'Status': pet.status
            }]).to_excel(
                writer,
                sheet_name='Basic Info',
                index=False
            )
            
            # 体重记录sheet
            pd.DataFrame([{
                'Date': r.date,
                'Weight': r.weight,
                'Notes': r.notes
            } for r in weight_records]).to_excel(
                writer,
                sheet_name='Weight Records',
                index=False
            )
            
            # 就医记录sheet
            pd.DataFrame([{
                'Date': r.date,
                'Symptoms': r.symptoms,
                'Diagnosis': r.diagnosis,
                'Treatment': r.treatment,
                'Follow-up Date': r.follow_up_date,
                'Notes': r.notes
            } for r in medical_records]).to_excel(
                writer,
                sheet_name='Medical Records',
                index=False
            )
            
            # 提醒sheet
            pd.DataFrame([{
                'Type': r['type'],
                'Due Date': r['due_date'],
                'Details': r['details']
            } for r in reminders]).to_excel(
                writer,
                sheet_name='Reminders',
                index=False
            )
            
            # 获取workbook和worksheet对象
            workbook = writer.book
            
            # 添加图表
            chart_sheet = workbook.add_worksheet('Weight Chart')
            chart = workbook.add_chart({'type': 'line'})
            
            # 配置图表数据
            weight_data = pd.DataFrame([{
                'Date': r.date,
                'Weight': r.weight
            } for r in weight_records])
            
            weight_data.to_excel(
                writer,
                sheet_name='Weight Chart',
                startrow=1,
                index=False
            )
            
            chart.add_series({
                'name': 'Weight',
                'categories': '=Weight Chart!$A$2:$A$' + str(len(weight_data) + 1),
                'values': '=Weight Chart!$B$2:$B$' + str(len(weight_data) + 1),
            })
            
            chart.set_title({'name': 'Weight Trend'})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Weight (kg)'})
            
            chart_sheet.insert_chart('D2', chart)
        
        output.seek(0)
        return output 