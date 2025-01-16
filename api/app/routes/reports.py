from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.settings import ReportTemplate, ReportTemplateVersion, SharedTemplate
from app.schemas.report import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    TemplateVersionCreate,
    TemplateVersionResponse,
    ShareTemplateRequest,
    SharedTemplateResponse
)
from app.utils.report_generator import ReportGenerator

router = APIRouter(
    prefix="/reports/templates",
    tags=["reports"],
)

@router.post("", response_model=ReportTemplateResponse)
async def create_template(
    template: ReportTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建报告模板"""
    db_template = ReportTemplate(
        **template.model_dump(),
        owner_id=current_user.id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("", response_model=List[ReportTemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的报告模板列表"""
    templates = db.query(ReportTemplate).filter(
        ReportTemplate.owner_id == current_user.id
    ).all()
    return templates

@router.get("/default", response_model=List[ReportTemplateResponse])
async def list_default_templates(
    db: Session = Depends(get_db)
):
    """获取默认报告模板列表"""
    templates = db.query(ReportTemplate).filter(
        ReportTemplate.is_default == True
    ).all()
    return templates

@router.put("/{template_id}", response_model=ReportTemplateResponse)
async def update_template(
    template_id: int,
    template: ReportTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新报告模板"""
    db_template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        ReportTemplate.owner_id == current_user.id
    ).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template.model_dump().items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除报告模板"""
    db_template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        ReportTemplate.owner_id == current_user.id
    ).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return {"status": "success"}

@router.get("/{template_id}/preview")
async def preview_template(
    template_id: int,
    sample_data: bool = Query(True, description="Use sample data for preview"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """预览报告模板"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        (ReportTemplate.owner_id == current_user.id) |
        (ReportTemplate.is_default == True)
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 生成示例数据或使用真实数据
    if sample_data:
        sample = generate_sample_data()
        return ReportGenerator.generate_report(**sample, template=template)
    else:
        # 使用用户最新的真实数据
        pet = db.query(Pet).filter(Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=404, detail="No pet found for preview")
        
        # 获取最近的记录
        weight_records = db.query(WeightRecord).filter(
            WeightRecord.pet_id == pet.id
        ).order_by(WeightRecord.date.desc()).limit(10).all()
        
        medical_records = db.query(MedicalVisit).filter(
            MedicalVisit.pet_id == pet.id
        ).order_by(MedicalVisit.date.desc()).limit(5).all()
        
        reminders = []  # 获取提醒
        
        return ReportGenerator.generate_report(
            pet=pet,
            weight_records=weight_records,
            medical_records=medical_records,
            reminders=reminders,
            template=template
        )

@router.post("/{template_id}/versions", response_model=TemplateVersionResponse)
async def create_template_version(
    template_id: int,
    version: TemplateVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建模板新版本"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        ReportTemplate.owner_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db_version = ReportTemplateVersion(
        template_id=template_id,
        **version.model_dump()
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

@router.get("/{template_id}/versions", response_model=List[TemplateVersionResponse])
async def list_template_versions(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取模板版本历史"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        ReportTemplate.owner_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    versions = db.query(ReportTemplateVersion).filter(
        ReportTemplateVersion.template_id == template_id
    ).order_by(ReportTemplateVersion.created_at.desc()).all()
    
    return versions

@router.post("/{template_id}/share", response_model=SharedTemplateResponse)
async def share_template(
    template_id: int,
    share_request: ShareTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分享模板给其他用户"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id,
        ReportTemplate.owner_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 检查目标用户是否存在
    target_user = db.query(User).filter(User.id == share_request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    # 检查是否已经分享
    existing_share = db.query(SharedTemplate).filter(
        SharedTemplate.template_id == template_id,
        SharedTemplate.shared_with_id == share_request.user_id
    ).first()
    if existing_share:
        raise HTTPException(status_code=400, detail="Template already shared with this user")
    
    shared = SharedTemplate(
        template_id=template_id,
        shared_with_id=share_request.user_id,
        can_edit=share_request.can_edit
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared

@router.get("/shared", response_model=List[ReportTemplateResponse])
async def list_shared_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分享给当前用户的模板列表"""
    shared_templates = db.query(ReportTemplate).join(
        SharedTemplate,
        SharedTemplate.template_id == ReportTemplate.id
    ).filter(
        SharedTemplate.shared_with_id == current_user.id
    ).all()
    
    return shared_templates 