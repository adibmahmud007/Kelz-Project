from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ImpactLevel(str, Enum):
    """Enumeration for impact assessment levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    NOT_SPECIFIED = "Not specified"

class DeviationTheme(str, Enum):
    """Enumeration for deviation themes."""
    MANUFACTURING = "Manufacturing"
    QUALITY_CONTROL = "Quality Control"
    DOCUMENTATION = "Documentation"
    EQUIPMENT = "Equipment"
    PERSONNEL = "Personnel"
    ENVIRONMENTAL = "Environmental"
    SUPPLIER = "Supplier"
    PACKAGING = "Packaging"
    VALIDATION = "Validation"
    OTHER = "Other"

class TriageStatus(str, Enum):
    """Enumeration for triage response options."""
    YES = "Yes"
    NO = "No"
    NOT_APPLICABLE = "Not applicable"

class DeviationTriageData(BaseModel):
    """Schema for deviation triage assessment data."""
    deviation_theme: str = Field(..., description="Primary theme/category of the deviation")
    impact_assessment: ImpactLevel = Field(..., description="Overall impact assessment level")
    product_quality: ImpactLevel = Field(..., description="Impact on product quality")
    patient_safety: ImpactLevel = Field(..., description="Impact on patient safety")
    regulatory_impact: ImpactLevel = Field(..., description="Regulatory compliance impact")
    validation_impact: ImpactLevel = Field(..., description="Impact on validation status")
    criticality: ImpactLevel = Field(..., description="Overall criticality assessment")
    
    class Config:
        use_enum_values = True

class DiscussionData(BaseModel):
    """Schema for investigation discussion section."""
    timeline: str = Field(..., description="Detailed timeline of events")
    affected_systems: List[str] = Field(default_factory=list, description="Systems affected by the deviation")
    initial_findings: str = Field(..., description="Initial investigation findings")

class RootCauseAnalysis(BaseModel):
    """Schema for root cause analysis section."""
    primary_cause: str = Field(..., description="Primary root cause identified")
    contributing_factors: List[str] = Field(default_factory=list, description="Contributing factors")
    methodology: str = Field(..., description="Root cause analysis methodology used")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")

class FinalAssessment(BaseModel):
    """Schema for final assessment section."""
    impact_analysis: str = Field(..., description="Detailed impact analysis")
    risk_evaluation: str = Field(..., description="Risk evaluation and classification")
    compliance_implications: str = Field(..., description="Regulatory compliance implications")
    recurrence_probability: str = Field(..., description="Assessment of recurrence likelihood")

class CAPARecommendations(BaseModel):
    """Schema for CAPA recommendations section."""
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate corrective actions")
    long_term_actions: List[str] = Field(default_factory=list, description="Long-term preventive actions")
    responsible_parties: List[str] = Field(default_factory=list, description="Responsible parties/departments")
    timeline: str = Field(..., description="Recommended implementation timeline")

class AIGeneratedInsights(BaseModel):
    """Schema for AI-generated insights section."""
    pattern_analysis: str = Field(..., description="Analysis of similar incidents or patterns")
    risk_mitigation: str = Field(..., description="Additional risk mitigation suggestions")
    process_improvements: List[str] = Field(default_factory=list, description="Process improvement recommendations")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Ongoing monitoring recommendations")

class InvestigationData(BaseModel):
    """Schema for complete investigation analysis data."""
    background_summary: str = Field(..., description="Concise summary of incident background")
    discussion: DiscussionData = Field(..., description="Investigation discussion details")
    root_cause_analysis: RootCauseAnalysis = Field(..., description="Root cause analysis results")
    final_assessment: FinalAssessment = Field(..., description="Final assessment and conclusions")
    capa_recommendations: CAPARecommendations = Field(..., description="CAPA recommendations")
    ai_generated_insights: AIGeneratedInsights = Field(..., description="AI-generated insights and recommendations")

class InvestigationRequest(BaseModel):
    """Schema for investigation processing request."""
    investigation_id: Optional[str] = Field(None, description="Unique investigation identifier")
    incident_description: str = Field(..., description="Description of the incident from transcription or text")
    background_details: str = Field(..., description="Background details from deviation report")
    deviation_triage: DeviationTriageData = Field(..., description="Triage assessment data")
    attachments: Optional[List[str]] = Field(None, description="List of attachment file paths")
    
    class Config:
        schema_extra = {
            "example": {
                "investigation_id": "INV-2024-001",
                "incident_description": "Temperature excursion observed in storage area during weekend shift",
                "background_details": "Product stored in controlled temperature environment showed temperature readings above specification",
                "deviation_triage": {
                    "deviation_theme": "Environmental",
                    "impact_assessment": "High",
                    "product_quality": "High",
                    "patient_safety": "Medium",
                    "regulatory_impact": "High",
                    "validation_impact": "Low",
                    "criticality": "High"
                },
                "attachments": ["path/to/temperature_log.pdf", "path/to/storage_procedure.docx"]
            }
        }

class InvestigationResponse(BaseModel):
    """Schema for investigation processing response."""
    status: str = Field(..., description="Processing status (success/error)")
    investigation_id: str = Field(..., description="Unique investigation identifier")
    data: InvestigationData = Field(..., description="Complete investigation analysis")
    transcription: Optional[str] = Field(None, description="Audio transcription if applicable")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "investigation_id": "INV-2024-001",
                "data": {
                    "background_summary": "Temperature excursion in controlled storage area affecting pharmaceutical products",
                    "discussion": {
                        "timeline": "Event occurred during weekend shift between 14:00-16:00 on Saturday",
                        "affected_systems": ["HVAC System", "Temperature Monitoring", "Storage Area B"],
                        "initial_findings": "HVAC malfunction caused temperature to rise above 25°C specification"
                    },
                    "root_cause_analysis": {
                        "primary_cause": "HVAC system component failure due to lack of preventive maintenance",
                        "contributing_factors": ["Delayed maintenance schedule", "Weekend staffing limitations"],
                        "methodology": "5 Why Analysis and Fishbone Diagram",
                        "evidence": ["HVAC maintenance logs", "Temperature monitoring data", "Staff interviews"]
                    },
                    "final_assessment": {
                        "impact_analysis": "Potential impact on product stability and efficacy",
                        "risk_evaluation": "High risk due to temperature-sensitive products",
                        "compliance_implications": "Requires regulatory notification and product assessment",
                        "recurrence_probability": "Medium without corrective actions"
                    },
                    "capa_recommendations": {
                        "immediate_actions": ["Product quarantine", "HVAC system repair", "Temperature validation"],
                        "long_term_actions": ["Preventive maintenance program revision", "Backup HVAC system installation"],
                        "responsible_parties": ["Engineering", "Quality Assurance", "Maintenance"],
                        "timeline": "Immediate actions: 24 hours, Long-term: 90 days"
                    },
                    "ai_generated_insights": {
                        "pattern_analysis": "Similar HVAC-related deviations occurred 3 times in past year",
                        "risk_mitigation": "Consider redundant cooling systems for critical storage areas",
                        "process_improvements": ["Automated alert systems", "Remote monitoring capabilities"],
                        "monitoring_recommendations": ["Continuous temperature monitoring", "HVAC performance trending"]
                    }
                }
            }
        }

class InvestigationSummaryResponse(BaseModel):
    """Schema for investigation summary response."""
    investigation_id: str = Field(..., description="Unique investigation identifier")
    status: str = Field(..., description="Investigation status")
    summary: str = Field(..., description="Brief investigation summary")
    primary_cause: str = Field(..., description="Primary root cause identified")
    impact_level: str = Field(..., description="Overall impact assessment")
    immediate_actions_count: int = Field(..., description="Number of immediate actions required")
    long_term_actions_count: int = Field(..., description="Number of long-term actions required")
    created_at: str = Field(..., description="Investigation creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "investigation_id": "INV-2024-001",
                "status": "completed",
                "summary": "HVAC system failure caused temperature excursion in storage area",
                "primary_cause": "Component failure due to inadequate preventive maintenance",
                "impact_level": "High",
                "immediate_actions_count": 3,
                "long_term_actions_count": 2,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T14:45:00Z"
            }
        }

class ValidationResult(BaseModel):
    """Schema for triage validation results."""
    is_valid: bool = Field(..., description="Whether triage data is complete and valid")
    missing_fields: List[str] = Field(default_factory=list, description="List of missing required fields")
    recommendations: List[str] = Field(default_factory=list, description="Validation recommendations")
    risk_level: str = Field(..., description="Assessed risk level based on triage data")
    
    class Config:
        schema_extra = {
            "example": {
                "is_valid": True,
                "missing_fields": [],
                "recommendations": ["High-priority investigation recommended due to safety concerns"],
                "risk_level": "high"
            }
        }

class AttachmentInfo(BaseModel):
    """Schema for attachment information."""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type/extension")
    file_size: int = Field(..., description="File size in bytes")
    content_preview: Optional[str] = Field(None, description="Preview of file content")
    extraction_status: str = Field(..., description="Text extraction status")

class DeviationReportAnalysisResponse(BaseModel):
    """Schema for comprehensive deviation report analysis response."""
    status: str = Field(..., description="Processing status")
    investigation_id: str = Field(..., description="Generated investigation ID")
    incident_description: str = Field(..., description="Processed incident description")
    investigation_data: InvestigationData = Field(..., description="Complete investigation analysis")
    form_data: Optional[Dict[str, Any]] = Field(None, description="Original form data for reference")
    attachments_processed: List[AttachmentInfo] = Field(default_factory=list, description="Information about processed attachments")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "investigation_id": "deviation_report_12345",
                "incident_description": "Temperature monitoring system showed readings above specification limits",
                "investigation_data": {
                    "background_summary": "Environmental control deviation in pharmaceutical storage facility"
                },
                "form_data": {
                    "incident_source": "audio",
                    "background_details": "Controlled storage environment failure",
                    "triage_assessment": {
                        "deviation_theme": "Environmental",
                        "impact_assessment": "High",
                        "criticality": "High"
                    },
                    "attachments_count": 2
                },
                "attachments_processed": [
                    {
                        "filename": "temperature_log.pdf",
                        "file_type": "pdf",
                        "file_size": 2048576,
                        "content_preview": "Temperature monitoring data from storage area...",
                        "extraction_status": "success"
                    }
                ]
            }
        }

# Additional utility schemas for specific use cases

class InvestigationMetrics(BaseModel):
    """Schema for investigation performance metrics."""
    total_investigations: int = Field(..., description="Total number of investigations")
    completed_investigations: int = Field(..., description="Number of completed investigations")
    pending_investigations: int = Field(..., description="Number of pending investigations")
    average_processing_time: float = Field(..., description="Average processing time in hours")
    high_risk_investigations: int = Field(..., description="Number of high-risk investigations")
    
class InvestigationFilter(BaseModel):
    """Schema for filtering investigation queries."""
    date_from: Optional[datetime] = Field(None, description="Filter investigations from this date")
    date_to: Optional[datetime] = Field(None, description="Filter investigations to this date")
    deviation_theme: Optional[DeviationTheme] = Field(None, description="Filter by deviation theme")
    criticality: Optional[ImpactLevel] = Field(None, description="Filter by criticality level")
    status: Optional[str] = Field(None, description="Filter by investigation status")
    responsible_party: Optional[str] = Field(None, description="Filter by responsible party")

class BulkInvestigationRequest(BaseModel):
    """Schema for processing multiple investigations."""
    investigations: List[InvestigationRequest] = Field(..., description="List of investigations to process")
    processing_options: Optional[Dict[str, Any]] = Field(None, description="Bulk processing options")
    
class InvestigationUpdateRequest(BaseModel):
    """Schema for updating existing investigations."""
    investigation_id: str = Field(..., description="Investigation ID to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")
    update_reason: str = Field(..., description="Reason for the update")
    updated_by: str = Field(..., description="User making the update")

# Error response schemas

class InvestigationError(BaseModel):
    """Schema for investigation error responses."""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error_code": "INVESTIGATION_PROCESSING_FAILED",
                "error_message": "Failed to process investigation due to missing required data",
                "details": {
                    "missing_fields": ["incident_description"],
                    "validation_errors": ["Triage data is incomplete"]
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }