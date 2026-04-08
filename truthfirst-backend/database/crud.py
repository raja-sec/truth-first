"""
CRUD Operations for Database Models
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import Case, CaseStatus, CaseType
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


async def create_case(
    db: AsyncSession,
    user_name: str,
    user_email: str,
    case_type: CaseType,
    user_phone: str = None,
    user_location: str = None,
    case_source: str = None,
    case_description: str = None,
    file_path: str = None,
    file_name: str = None,
    file_size: int = None,
    content_text: str = None,
) -> Case:
    """
    Create a new case in the database.
    
    Returns:
        Case object with generated ID
    """
    case_id = str(uuid.uuid4())
    
    new_case = Case(
        id=case_id,
        user_name=user_name,
        user_email=user_email,
        user_phone=user_phone,
        user_location=user_location,
        case_type=case_type,
        case_source=case_source,
        case_description=case_description,
        file_path=file_path,
        file_name=file_name,
        file_size=file_size,
        content_text=content_text,
        status=CaseStatus.PENDING,
    )
    
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    
    logger.info(f"✅ Created case: {case_id} ({case_type})")
    
    return new_case


async def get_case_by_id(db: AsyncSession, case_id: str) -> Case | None:
    """
    Retrieve a case by its ID.
    
    Returns:
        Case object or None if not found
    """
    result = await db.execute(select(Case).where(Case.id == case_id, Case.is_deleted == False))
    case = result.scalar_one_or_none()
    
    return case


async def update_case_status(
    db: AsyncSession,
    case_id: str,
    status: CaseStatus,
    analysis_result: dict = None,
) -> Case | None:
    """
    Update case status and optionally store analysis results.
    
    Returns:
        Updated Case object or None if not found
    """
    case = await get_case_by_id(db, case_id)
    
    if not case:
        return None
    
    case.status = status
    case.updated_at = datetime.utcnow()
    
    if analysis_result:
        case.analysis_result = analysis_result
        case.analyzed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(case)
    
    logger.info(f"✅ Updated case {case_id} status to {status}")
    
    return case


async def get_cases_by_email(
    db: AsyncSession,
    email: str,
    limit: int = 10
) -> list[Case]:
    """
    Get all cases for a specific email address.
    
    Returns:
        List of Case objects
    """
    result = await db.execute(
        select(Case)
        .where(Case.user_email == email, Case.is_deleted == False)
        .order_by(Case.created_at.desc())
        .limit(limit)
    )
    
    cases = result.scalars().all()
    return list(cases)


async def soft_delete_case(db: AsyncSession, case_id: str) -> bool:
    """
    Soft delete a case (mark as deleted, don't actually remove).
    
    Returns:
        True if deleted, False if not found
    """
    case = await get_case_by_id(db, case_id)
    
    if not case:
        return False
    
    case.is_deleted = True
    case.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info(f"🗑️  Soft deleted case: {case_id}")
    
    return True