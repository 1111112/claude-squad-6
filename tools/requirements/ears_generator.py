"""
Claude Squad 5 - EARS Requirements Generator
Easy Approach to Requirements Syntax for clear, testable requirements
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

class RequirementType(Enum):
    UBIQUITOUS = "SHALL"      # Always active
    EVENT_DRIVEN = "WHEN"      # Triggered by event
    UNWANTED = "IF THEN"       # Prevent unwanted behavior
    STATE_DRIVEN = "WHILE"     # Active in certain state
    OPTIONAL = "WHERE"         # Feature variation
    COMPLEX = "WHEN WHILE"     # Combination

@dataclass
class Requirement:
    id: str
    type: RequirementType
    system: str
    action: str
    trigger: Optional[str] = None
    condition: Optional[str] = None
    constraint: Optional[str] = None
    rationale: Optional[str] = None
    acceptance_criteria: List[str] = None
    
    def __post_init__(self):
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
    
    def to_ears(self) -> str:
        """Convert to EARS format string"""
        if self.type == RequirementType.UBIQUITOUS:
            base = f"The {self.system} SHALL {self.action}"
            
        elif self.type == RequirementType.EVENT_DRIVEN:
            base = f"WHEN {self.trigger}, the {self.system} SHALL {self.action}"
            
        elif self.type == RequirementType.UNWANTED:
            base = f"IF {self.trigger}, THEN the {self.system} SHALL {self.action}"
            
        elif self.type == RequirementType.STATE_DRIVEN:
            base = f"WHILE {self.condition}, the {self.system} SHALL {self.action}"
            
        elif self.type == RequirementType.OPTIONAL:
            base = f"WHERE {self.condition}, the {self.system} SHALL {self.action}"
            
        elif self.type == RequirementType.COMPLEX:
            base = f"WHEN {self.trigger}, WHILE {self.condition}, the {self.system} SHALL {self.action}"
        
        # Add constraints if present
        if self.constraint:
            base += f" {self.constraint}"
            
        return base

class EARSGenerator:
    """Generate well-formed requirements in EARS format"""
    
    def __init__(self):
        self.requirements: List[Requirement] = []
        self.id_counter = 1
        
    def create_requirement(
        self,
        req_type: RequirementType,
        system: str,
        action: str,
        **kwargs
    ) -> Requirement:
        """Create a new requirement"""
        req_id = f"REQ-{self.id_counter:03d}"
        self.id_counter += 1
        
        req = Requirement(
            id=req_id,
            type=req_type,
            system=system,
            action=action,
            **kwargs
        )
        
        # Auto-generate acceptance criteria if not provided
        if not req.acceptance_criteria:
            req.acceptance_criteria = self._generate_acceptance_criteria(req)
            
        self.requirements.append(req)
        return req
    
    def _generate_acceptance_criteria(self, req: Requirement) -> List[str]:
        """Auto-generate basic acceptance criteria"""
        criteria = []
        
        # Basic positive test
        criteria.append(f"GIVEN the system is operational, WHEN {req.action} is triggered, THEN the expected behavior occurs")
        
        # Negative test
        criteria.append(f"GIVEN invalid input, WHEN {req.action} is attempted, THEN appropriate error handling occurs")
        
        # Performance criterion if applicable
        if "response" in req.action.lower() or "process" in req.action.lower():
            criteria.append(f"GIVEN normal load, WHEN {req.action} executes, THEN response time is under 200ms")
            
        return criteria
    
    def create_ubiquitous(self, system: str, action: str, **kwargs) -> Requirement:
        """Create a ubiquitous (always active) requirement"""
        return self.create_requirement(
            RequirementType.UBIQUITOUS,
            system,
            action,
            **kwargs
        )
    
    def create_event_driven(self, system: str, trigger: str, action: str, **kwargs) -> Requirement:
        """Create an event-driven requirement"""
        return self.create_requirement(
            RequirementType.EVENT_DRIVEN,
            system,
            action,
            trigger=trigger,
            **kwargs
        )
    
    def create_state_driven(self, system: str, condition: str, action: str, **kwargs) -> Requirement:
        """Create a state-driven requirement"""
        return self.create_requirement(
            RequirementType.STATE_DRIVEN,
            system,
            action,
            condition=condition,
            **kwargs
        )
    
    def create_unwanted_behavior(self, system: str, trigger: str, action: str, **kwargs) -> Requirement:
        """Create a requirement to prevent unwanted behavior"""
        return self.create_requirement(
            RequirementType.UNWANTED,
            system,
            action,
            trigger=trigger,
            **kwargs
        )
    
    def generate_from_user_story(self, story: str) -> List[Requirement]:
        """Generate requirements from a user story"""
        # Parse user story format: "As a <role>, I want <feature>, so that <benefit>"
        pattern = r"As a (.+), I want (.+), so that (.+)"
        match = re.match(pattern, story, re.IGNORECASE)
        
        if not match:
            raise ValueError("User story must follow format: 'As a <role>, I want <feature>, so that <benefit>'")
            
        role, feature, benefit = match.groups()
        requirements = []
        
        # Generate primary requirement
        primary = self.create_ubiquitous(
            system="system",
            action=f"provide {feature} for {role}",
            rationale=benefit
        )
        requirements.append(primary)
        
        # Add common supplementary requirements
        # Security
        requirements.append(self.create_event_driven(
            system="system",
            trigger=f"{role} attempts to access {feature}",
            action="verify authentication and authorization"
        ))
        
        # Error handling
        requirements.append(self.create_unwanted_behavior(
            system="system",
            trigger=f"invalid input is provided for {feature}",
            action="display clear error message and log the attempt"
        ))
        
        return requirements
    
    def export_requirements(self, format: str = "markdown") -> str:
        """Export all requirements in specified format"""
        if format == "markdown":
            return self._export_markdown()
        elif format == "csv":
            return self._export_csv()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self) -> str:
        """Export as markdown document"""
        lines = ["# Requirements Document", ""]
        
        # Group by type
        by_type = {}
        for req in self.requirements:
            if req.type not in by_type:
                by_type[req.type] = []
            by_type[req.type].append(req)
        
        for req_type, reqs in by_type.items():
            lines.append(f"## {req_type.name.replace('_', ' ').title()} Requirements")
            lines.append("")
            
            for req in reqs:
                lines.append(f"### {req.id}")
                lines.append(f"**Requirement:** {req.to_ears()}")
                
                if req.rationale:
                    lines.append(f"**Rationale:** {req.rationale}")
                    
                if req.acceptance_criteria:
                    lines.append("**Acceptance Criteria:**")
                    for criterion in req.acceptance_criteria:
                        lines.append(f"- {criterion}")
                        
                lines.append("")
                
        return "\n".join(lines)
    
    def _export_csv(self) -> str:
        """Export as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["ID", "Type", "Requirement", "Rationale", "Acceptance Criteria"])
        
        # Data
        for req in self.requirements:
            writer.writerow([
                req.id,
                req.type.name,
                req.to_ears(),
                req.rationale or "",
                "; ".join(req.acceptance_criteria)
            ])
            
        return output.getvalue()

# Example usage functions
def generate_feature_requirements(feature_description: str) -> str:
    """Generate complete requirements for a feature"""
    generator = EARSGenerator()
    
    # Parse feature description
    # This is simplified - in real use would have more sophisticated parsing
    
    # Example requirements for a login feature
    if "login" in feature_description.lower():
        # Functional requirements
        generator.create_event_driven(
            system="authentication system",
            trigger="user submits login credentials",
            action="validate credentials against user database",
            constraint="within 2 seconds"
        )
        
        generator.create_unwanted_behavior(
            system="authentication system",
            trigger="invalid credentials are submitted",
            action="increment failed login counter and display generic error message"
        )
        
        generator.create_state_driven(
            system="authentication system",
            condition="user has failed 3 login attempts",
            action="lock account for 15 minutes"
        )
        
        # Security requirements
        generator.create_ubiquitous(
            system="authentication system",
            action="hash all passwords using bcrypt with minimum 10 rounds"
        )
        
        generator.create_ubiquitous(
            system="authentication system",
            action="use HTTPS for all authentication endpoints"
        )
    
    return generator.export_requirements()