def generate_sample_data():
    """生成用于模板预览的示例数据"""
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    
    # 创建示例宠物
    pet = type('Pet', (), {
        'name': 'Sample Pet',
        'species': 'Dog',
        'birth_date': now - timedelta(days=365*2)
    })
    
    # 创建示例体重记录
    weight_records = [
        type('WeightRecord', (), {
            'date': now - timedelta(days=i*30),
            'weight': 10 + i*0.5,
            'notes': f'Sample weight record {i}'
        }) for i in range(5)
    ]
    
    # 创建示例就医记录
    medical_records = [
        type('MedicalVisit', (), {
            'date': now - timedelta(days=i*60),
            'symptoms': 'Sample symptoms',
            'diagnosis': 'Sample diagnosis',
            'treatment': 'Sample treatment',
            'notes': f'Sample medical record {i}'
        }) for i in range(3)
    ]
    
    # 创建示例提醒
    reminders = [
        {
            'type': 'Vaccine',
            'due_date': now + timedelta(days=30),
            'details': 'Sample vaccine reminder'
        },
        {
            'type': 'Deworming',
            'due_date': now + timedelta(days=45),
            'details': 'Sample deworming reminder'
        }
    ]
    
    return {
        'pet': pet,
        'weight_records': weight_records,
        'medical_records': medical_records,
        'reminders': reminders
    } 