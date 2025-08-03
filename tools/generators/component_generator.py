#!/usr/bin/env python3
"""
DexAgent Component Generator
Generate React components, API endpoints, and other code scaffolding
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

class ComponentGenerator:
    """Generate code components for DexAgent"""
    
    def __init__(self):
        """Initialize generator"""
        self.root_dir = Path(__file__).parent.parent.parent
        self.templates_dir = Path(__file__).parent / "templates"
        self.apps_dir = self.root_dir / "apps"
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(exist_ok=True)
    
    def generate_react_component(self, name: str, type_: str = "functional", with_test: bool = True):
        """Generate React component"""
        print(f"🔨 Generating React component: {name}")
        
        frontend_dir = self.apps_dir / "frontend"
        components_dir = frontend_dir / "components"
        
        if not components_dir.exists():
            print(f"❌ Components directory not found: {components_dir}")
            return
        
        # Component file
        component_file = components_dir / f"{name}.tsx"
        component_content = self._get_react_component_template(name, type_)
        
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        print(f"✅ Created component: {component_file}")
        
        # Test file
        if with_test:
            test_dir = frontend_dir / "tests" / "unit"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / f"{name}.test.tsx"
            test_content = self._get_react_test_template(name)
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            print(f"✅ Created test: {test_file}")
    
    def _get_react_component_template(self, name: str, type_: str) -> str:
        """Get React component template"""
        if type_ == "class":
            return f'''import React, {{ Component }} from 'react';

interface {name}Props {{
  // Define props here
}}

interface {name}State {{
  // Define state here
}}

class {name} extends Component<{name}Props, {name}State> {{
  constructor(props: {name}Props) {{
    super(props);
    this.state = {{
      // Initialize state here
    }};
  }}

  render() {{
    return (
      <div className="{name.lower()}">
        <h1>{name}</h1>
        <p>This is the {name} component.</p>
      </div>
    );
  }}
}}

export default {name};
'''
        else:  # functional
            return f'''import React from 'react';

interface {name}Props {{
  // Define props here
}}

const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div className="{name.lower()}">
      <h1>{name}</h1>
      <p>This is the {name} component.</p>
    </div>
  );
}};

export default {name};
'''
    
    def _get_react_test_template(self, name: str) -> str:
        """Get React test template"""
        return f'''import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import '@testing-library/jest-dom';
import {name} from '../{name}';

describe('{name}', () => {{
  it('renders without crashing', () => {{
    render(<{name} />);
    expect(screen.getByText('{name}')).toBeInTheDocument();
  }});

  it('displays correct content', () => {{
    render(<{name} />);
    expect(screen.getByText('This is the {name} component.')).toBeInTheDocument();
  }});
}});
'''
    
    def generate_api_endpoint(self, name: str, methods: list = None):
        """Generate FastAPI endpoint"""
        if methods is None:
            methods = ["GET", "POST"]
        
        print(f"🔨 Generating API endpoint: {name}")
        
        backend_dir = self.apps_dir / "backend"
        api_dir = backend_dir / "app" / "api" / "v1"
        
        if not api_dir.exists():
            print(f"❌ API directory not found: {api_dir}")
            return
        
        # Endpoint file
        endpoint_file = api_dir / f"{name.lower()}.py"
        endpoint_content = self._get_api_endpoint_template(name, methods)
        
        with open(endpoint_file, 'w') as f:
            f.write(endpoint_content)
        
        print(f"✅ Created endpoint: {endpoint_file}")
        
        # Test file
        test_dir = backend_dir / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_{name.lower()}.py"
        test_content = self._get_api_test_template(name, methods)
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Created test: {test_file}")
    
    def _get_api_endpoint_template(self, name: str, methods: list) -> str:
        """Get API endpoint template"""
        class_name = name.title()
        
        template = f'''from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.{name.lower()} import {class_name}Create, {class_name}Update, {class_name}Response
from app.models.{name.lower()} import {class_name}
from app.core.auth import get_current_user

router = APIRouter()

'''
        
        if "GET" in methods:
            template += f'''@router.get("/{name.lower()}", response_model=List[{class_name}Response])
async def get_{name.lower()}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all {name.lower()}s"""
    {name.lower()}s = db.query({class_name}).offset(skip).limit(limit).all()
    return {name.lower()}s

@router.get("/{name.lower()}/{{item_id}}", response_model={class_name}Response)
async def get_{name.lower()}(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific {name.lower()}"""
    {name.lower()} = db.query({class_name}).filter({class_name}.id == item_id).first()
    if not {name.lower()}:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return {name.lower()}

'''
        
        if "POST" in methods:
            template += f'''@router.post("/{name.lower()}", response_model={class_name}Response)
async def create_{name.lower()}(
    {name.lower()}: {class_name}Create,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new {name.lower()}"""
    db_{name.lower()} = {class_name}(**{name.lower()}.dict())
    db.add(db_{name.lower()})
    db.commit()
    db.refresh(db_{name.lower()})
    return db_{name.lower()}

'''
        
        if "PUT" in methods:
            template += f'''@router.put("/{name.lower()}/{{item_id}}", response_model={class_name}Response)
async def update_{name.lower()}(
    item_id: int,
    {name.lower()}_update: {class_name}Update,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update {name.lower()}"""
    {name.lower()} = db.query({class_name}).filter({class_name}.id == item_id).first()
    if not {name.lower()}:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    
    for field, value in {name.lower()}_update.dict(exclude_unset=True).items():
        setattr({name.lower()}, field, value)
    
    db.commit()
    db.refresh({name.lower()})
    return {name.lower()}

'''
        
        if "DELETE" in methods:
            template += f'''@router.delete("/{name.lower()}/{{item_id}}")
async def delete_{name.lower()}(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete {name.lower()}"""
    {name.lower()} = db.query({class_name}).filter({class_name}.id == item_id).first()
    if not {name.lower()}:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    
    db.delete({name.lower()})
    db.commit()
    return {{"message": "{class_name} deleted successfully"}}
'''
        
        return template
    
    def _get_api_test_template(self, name: str, methods: list) -> str:
        """Get API test template"""
        return f'''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class Test{name.title()}API:
    """Test {name} API endpoints"""
    
    def test_create_{name.lower()}(self):
        """Test creating {name.lower()}"""
        {name.lower()}_data = {{
            # Add test data here
        }}
        
        response = client.post("/{name.lower()}", json={name.lower()}_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
    
    def test_get_{name.lower()}s(self):
        """Test getting all {name.lower()}s"""
        response = client.get("/{name.lower()}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_{name.lower()}_by_id(self):
        """Test getting specific {name.lower()}"""
        # First create a {name.lower()}
        {name.lower()}_data = {{
            # Add test data here
        }}
        create_response = client.post("/{name.lower()}", json={name.lower()}_data)
        {name.lower()}_id = create_response.json()["id"]
        
        # Then get it
        response = client.get(f"/{name.lower()}/{{{}name.lower()}_id}}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == {name.lower()}_id
    
    def test_update_{name.lower()}(self):
        """Test updating {name.lower()}"""
        # First create a {name.lower()}
        {name.lower()}_data = {{
            # Add test data here
        }}
        create_response = client.post("/{name.lower()}", json={name.lower()}_data)
        {name.lower()}_id = create_response.json()["id"]
        
        # Then update it
        update_data = {{
            # Add update data here
        }}
        response = client.put(f"/{name.lower()}/{{{}name.lower()}_id}}", json=update_data)
        assert response.status_code == 200
    
    def test_delete_{name.lower()}(self):
        """Test deleting {name.lower()}"""
        # First create a {name.lower()}
        {name.lower()}_data = {{
            # Add test data here
        }}
        create_response = client.post("/{name.lower()}", json={name.lower()}_data)
        {name.lower()}_id = create_response.json()["id"]
        
        # Then delete it
        response = client.delete(f"/{name.lower()}/{{{}name.lower()}_id}}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/{name.lower()}/{{{}name.lower()}_id}}")
        assert get_response.status_code == 404
'''
    
    def generate_database_model(self, name: str, fields: Dict[str, str]):
        """Generate SQLAlchemy database model"""
        print(f"🔨 Generating database model: {name}")
        
        backend_dir = self.apps_dir / "backend"
        models_dir = backend_dir / "app" / "models"
        
        if not models_dir.exists():
            print(f"❌ Models directory not found: {models_dir}")
            return
        
        # Model file
        model_file = models_dir / f"{name.lower()}.py"
        model_content = self._get_model_template(name, fields)
        
        with open(model_file, 'w') as f:
            f.write(model_content)
        
        print(f"✅ Created model: {model_file}")
        
        # Schema file
        schemas_dir = backend_dir / "app" / "schemas"
        schema_file = schemas_dir / f"{name.lower()}.py"
        schema_content = self._get_schema_template(name, fields)
        
        with open(schema_file, 'w') as f:
            f.write(schema_content)
        
        print(f"✅ Created schema: {schema_file}")
    
    def _get_model_template(self, name: str, fields: Dict[str, str]) -> str:
        """Get SQLAlchemy model template"""
        class_name = name.title()
        
        template = f'''from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class {class_name}(Base):
    """
    {class_name} model
    """
    __tablename__ = "{name.lower()}s"
    
    id = Column(Integer, primary_key=True, index=True)
'''
        
        for field_name, field_type in fields.items():
            if field_type.lower() in ['string', 'str']:
                template += f'    {field_name} = Column(String, index=True)\n'
            elif field_type.lower() in ['text', 'longtext']:
                template += f'    {field_name} = Column(Text)\n'
            elif field_type.lower() in ['int', 'integer']:
                template += f'    {field_name} = Column(Integer)\n'
            elif field_type.lower() in ['bool', 'boolean']:
                template += f'    {field_name} = Column(Boolean, default=False)\n'
            elif field_type.lower() in ['datetime', 'timestamp']:
                template += f'    {field_name} = Column(DateTime)\n'
        
        template += '''    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<{class_name}(id={{self.id}})>"
'''
        
        return template
    
    def _get_schema_template(self, name: str, fields: Dict[str, str]) -> str:
        """Get Pydantic schema template"""
        class_name = name.title()
        
        template = f'''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class {class_name}Base(BaseModel):
    """Base {name} schema"""
'''
        
        for field_name, field_type in fields.items():
            if field_type.lower() in ['string', 'str', 'text', 'longtext']:
                template += f'    {field_name}: str\n'
            elif field_type.lower() in ['int', 'integer']:
                template += f'    {field_name}: int\n'
            elif field_type.lower() in ['bool', 'boolean']:
                template += f'    {field_name}: bool = False\n'
            elif field_type.lower() in ['datetime', 'timestamp']:
                template += f'    {field_name}: datetime\n'
        
        template += f'''

class {class_name}Create({class_name}Base):
    """Schema for creating {name}"""
    pass

class {class_name}Update(BaseModel):
    """Schema for updating {name}"""
'''
        
        for field_name, field_type in fields.items():
            if field_type.lower() in ['string', 'str', 'text', 'longtext']:
                template += f'    {field_name}: Optional[str] = None\n'
            elif field_type.lower() in ['int', 'integer']:
                template += f'    {field_name}: Optional[int] = None\n'
            elif field_type.lower() in ['bool', 'boolean']:
                template += f'    {field_name}: Optional[bool] = None\n'
            elif field_type.lower() in ['datetime', 'timestamp']:
                template += f'    {field_name}: Optional[datetime] = None\n'
        
        template += f'''

class {class_name}Response({class_name}Base):
    """Schema for {name} response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
'''
        
        return template

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DexAgent Component Generator")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # React component generator
    react_parser = subparsers.add_parser('react', help='Generate React component')
    react_parser.add_argument('name', help='Component name')
    react_parser.add_argument('--type', choices=['functional', 'class'], default='functional',
                             help='Component type')
    react_parser.add_argument('--no-test', action='store_true', help='Skip test file')
    
    # API endpoint generator
    api_parser = subparsers.add_parser('api', help='Generate API endpoint')
    api_parser.add_argument('name', help='Endpoint name')
    api_parser.add_argument('--methods', nargs='+', choices=['GET', 'POST', 'PUT', 'DELETE'],
                           default=['GET', 'POST'], help='HTTP methods')
    
    # Database model generator
    model_parser = subparsers.add_parser('model', help='Generate database model')
    model_parser.add_argument('name', help='Model name')
    model_parser.add_argument('--fields', required=True, 
                             help='Fields in format "name:type,field2:type" (e.g., "title:string,count:int")')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = ComponentGenerator()
    
    if args.command == 'react':
        generator.generate_react_component(
            args.name,
            args.type,
            not args.no_test
        )
    elif args.command == 'api':
        generator.generate_api_endpoint(args.name, args.methods)
    elif args.command == 'model':
        # Parse fields
        fields = {}
        for field_def in args.fields.split(','):
            field_name, field_type = field_def.split(':')
            fields[field_name.strip()] = field_type.strip()
        
        generator.generate_database_model(args.name, fields)

if __name__ == "__main__":
    main()