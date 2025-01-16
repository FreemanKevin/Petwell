from app.db.session import SessionLocal
from app.models.settings import ReportTemplate

def init_default_templates():
    db = SessionLocal()
    try:
        # 检查是否已存在默认模板
        if db.query(ReportTemplate).filter(ReportTemplate.is_default == True).first():
            return
        
        # 创建默认HTML模板
        default_html = ReportTemplate(
            name="Default HTML Template",
            description="Default health report template in HTML format",
            template_type="html",
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ pet.name }}'s Health Report</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .container { max-width: 800px; margin: 0 auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{{ pet.name }}'s Health Report</h1>
                    <!-- 其他内容 -->
                </div>
            </body>
            </html>
            """,
            is_default=True
        )
        
        # 创建默认Markdown模板
        default_markdown = ReportTemplate(
            name="Default Markdown Template",
            description="Default health report template in Markdown format",
            template_type="markdown",
            content="""
            # {{ pet.name }}'s Health Report
            
            Generated on: {{ generated_date }}
            
            ## Basic Information
            
            - Name: {{ pet.name }}
            - Species: {{ pet.species }}
            - Age: {{ pet_age }}
            
            ## Health Summary
            
            {{ health_summary }}
            """,
            is_default=True
        )
        
        db.add(default_html)
        db.add(default_markdown)
        db.commit()
        
    finally:
        db.close() 