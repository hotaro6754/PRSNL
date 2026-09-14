import re

def patch_correlation_engine():
    with open('backend/correlation/engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace dict key type hint
    content = content.replace('self.cases: Dict[str, CyberCase] = {} # Keyed by primary_entity',
                              'self.cases: Dict[str, CyberCase] = {} # Keyed by org_id:primary_entity')

    # Update ingest_alert logic
    orig_entity = '''        entity = alert.primary_entity or alert.source_ip
        if not entity or entity == "UNKNOWN":
            return None'''
            
    new_entity = '''        entity = alert.primary_entity or alert.source_ip
        if not entity or entity == "UNKNOWN":
            return None
            
        org_id = getattr(alert, "organization_id", "default_org")
        correlation_key = f"{org_id}:{entity}"'''
        
    content = content.replace(orig_entity, new_entity)
    
    # Replace entity usage with correlation_key
    content = content.replace('if entity not in self.cases and len(self.cases) >= self.max_cases:',
                              'if correlation_key not in self.cases and len(self.cases) >= self.max_cases:')
                              
    content = content.replace('if entity not in self.cases:',
                              'if correlation_key not in self.cases:')
                              
    content = content.replace('self.cases[entity] = case',
                              'self.cases[correlation_key] = case')
                              
    content = content.replace('case = self.cases[entity]',
                              'case = self.cases[correlation_key]')

    # Add organization_id to CyberCase instantiation
    orig_case = '''            case = CyberCase(
                case_id=uuid.uuid4(),
                primary_entity=entity,'''
                
    new_case = '''            case = CyberCase(
                case_id=uuid.uuid4(),
                organization_id=org_id,
                primary_entity=entity,'''
                
    content = content.replace(orig_case, new_case)
    
    with open('backend/correlation/engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Correlation Engine patched successfully!")

patch_correlation_engine()
