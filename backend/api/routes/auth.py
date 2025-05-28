# backend/api/routes/auth.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..services.auth_service import auth_service
from ..schemas.user import UserCreate, UserResponse, UserLogin, Token
from ..models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    return auth_service.create_user(db, user_create)

@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    return auth_service.login(db, user_login.username, user_login.password)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    user = auth_service.get_current_user(db, credentials)
    return UserResponse.from_orm(user)

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    current_user = auth_service.get_current_user(db, credentials)
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]

# backend/api/routes/workflows.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..services.auth_service import auth_service
from ..services.workflow_service import workflow_service
from ..schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeResponse
)

router = APIRouter()

@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_create: WorkflowCreate,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    return workflow_service.create_workflow(db, workflow_create, current_user.id)

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """List workflows."""
    current_user = auth_service.get_current_user(db, credentials)
    return workflow_service.list_workflows(
        db, current_user.id, skip, limit, status_filter, category
    )

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Get a specific workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    return workflow_service.get_workflow(db, workflow_id, current_user.id)

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_update: WorkflowUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    return workflow_service.update_workflow(db, workflow_id, workflow_update, current_user.id)

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Delete a workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    workflow_service.delete_workflow(db, workflow_id, current_user.id)

@router.post("/{workflow_id}/nodes", response_model=WorkflowNodeResponse)
async def create_workflow_node(
    workflow_id: UUID,
    node_create: WorkflowNodeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """Create a new node in a workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    node_create.workflow_id = workflow_id
    return workflow_service.create_workflow_node(db, node_create, current_user.id)

@router.get("/{workflow_id}/nodes", response_model=List[WorkflowNodeResponse])
async def list_workflow_nodes(
    workflow_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
):
    """List nodes in a workflow."""
    current_user = auth_service.get_current_user(db, credentials)
    return workflow_service.list_workflow_nodes(db, workflow_id, current_user.id)

# backend/api/services/workflow_service.py
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.workflow import Workflow, WorkflowNode, WorkflowConnection
from ..schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeResponse
)

logger = logging.getLogger(__name__)

class WorkflowService:
    def create_workflow(self, db: Session, workflow_create: WorkflowCreate, user_id: UUID) -> Workflow:
        """Create a new workflow."""
        db_workflow = Workflow(
            name=workflow_create.name,
            description=workflow_create.description,
            created_by=user_id,
            status=workflow_create.status,
            definition=workflow_create.definition,
            metadata=workflow_create.metadata,
            is_template=workflow_create.is_template,
            tags=workflow_create.tags,
            category=workflow_create.category
        )
        
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        
        logger.info(f"Created workflow: {db_workflow.name} by user {user_id}")
        return db_workflow
    
    def get_workflow(self, db: Session, workflow_id: UUID, user_id: UUID) -> Workflow:
        """Get a workflow by ID."""
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.created_by == user_id
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return workflow
    
    def list_workflows(
        self, 
        db: Session, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Workflow]:
        """List workflows for a user."""
        query = db.query(Workflow).filter(Workflow.created_by == user_id)
        
        if status_filter:
            query = query.filter(Workflow.status == status_filter)
        
        if category:
            query = query.filter(Workflow.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def update_workflow(
        self, 
        db: Session, 
        workflow_id: UUID, 
        workflow_update: WorkflowUpdate, 
        user_id: UUID
    ) -> Workflow:
        """Update a workflow."""
        workflow = self.get_workflow(db, workflow_id, user_id)
        
        update_data = workflow_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        if update_data:
            workflow.version += 1
        
        db.commit()
        db.refresh(workflow)
        
        logger.info(f"Updated workflow: {workflow.name}")
        return workflow
    
    def delete_workflow(self, db: Session, workflow_id: UUID, user_id: UUID):
        """Delete a workflow."""
        workflow = self.get_workflow(db, workflow_id, user_id)
        
        db.delete(workflow)
        db.commit()
        
        logger.info(f"Deleted workflow: {workflow.name}")
    
    def create_workflow_node(
        self, 
        db: Session, 
        node_create: WorkflowNodeCreate, 
        user_id: UUID
    ) -> WorkflowNode:
        """Create a workflow node."""
        # Verify workflow ownership
        workflow = self.get_workflow(db, node_create.workflow_id, user_id)
        
        db_node = WorkflowNode(
            workflow_id=node_create.workflow_id,
            name=node_create.name,
            type=node_create.type,
            position_x=node_create.position_x,
            position_y=node_create.position_y,
            config=node_create.config,
            metadata=node_create.metadata
        )
        
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        
        logger.info(f"Created node: {db_node.name} in workflow {workflow.name}")
        return db_node
    
    def list_workflow_nodes(
        self, 
        db: Session, 
        workflow_id: UUID, 
        user_id: UUID
    ) -> List[WorkflowNode]:
        """List nodes in a workflow."""
        # Verify workflow ownership
        self.get_workflow(db, workflow_id, user_id)
        
        return db.query(WorkflowNode).filter(
            WorkflowNode.workflow_id == workflow_id
        ).all()

# Global workflow service instance
workflow_service = WorkflowService()
