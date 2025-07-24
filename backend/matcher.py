from models.model import load_model_and_tokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

model, tokenizer = load_model_and_tokenizer()

def generate_match_score(resume_text, job_text):
    # Get base semantic similarity
    resume_vec = model.encode(resume_text)
    job_vec = model.encode(job_text)
    base_score = cosine_similarity([resume_vec], [job_vec])[0][0] * 100
    
    # Apply domain-aware adjustments
    adjusted_score, reasoning = apply_domain_matching(resume_text, job_text, base_score)
    
    return adjusted_score, reasoning

def apply_domain_matching(resume_text, job_text, base_score):
    """Apply domain-aware matching to penalize cross-field mismatches"""
    
    resume_lower = resume_text.lower()
    job_lower = job_text.lower()
    
    # Define domain-specific keywords
    tech_keywords = [
        'programming', 'software', 'developer', 'engineer', 'coding', 'python', 
        'javascript', 'java', 'react', 'node.js', 'database', 'api', 'frontend', 
        'backend', 'fullstack', 'web development', 'mobile app', 'algorithm',
        'data structure', 'git', 'github', 'docker', 'aws', 'cloud', 'devops',
        'machine learning', 'ai', 'artificial intelligence', 'html', 'css',
        'framework', 'library', 'debugging', 'testing', 'deployment'
    ]
    
    commerce_keywords = [
        'sales', 'marketing', 'business', 'commerce', 'retail', 'customer service',
        'accounting', 'finance', 'economics', 'trade', 'procurement', 'supply chain',
        'inventory', 'merchandising', 'e-commerce', 'business development',
        'market research', 'advertising', 'promotion', 'brand', 'revenue',
        'profit', 'budget', 'financial analysis', 'crm', 'lead generation'
    ]
    
    hr_keywords = [
        'human resources', 'recruitment', 'hiring', 'talent acquisition',
        'employee relations', 'payroll', 'benefits', 'training', 'onboarding',
        'performance management', 'hr policies', 'compliance', 'workforce'
    ]
    
    healthcare_keywords = [
        'medical', 'healthcare', 'hospital', 'patient', 'clinical', 'nursing',
        'doctor', 'physician', 'treatment', 'diagnosis', 'pharmaceutical',
        'medical device', 'health', 'medicine', 'therapy'
    ]
    
    # Count domain keywords in resume and job
    resume_tech_count = sum(1 for keyword in tech_keywords if keyword in resume_lower)
    resume_commerce_count = sum(1 for keyword in commerce_keywords if keyword in resume_lower)
    resume_hr_count = sum(1 for keyword in hr_keywords if keyword in resume_lower)
    resume_healthcare_count = sum(1 for keyword in healthcare_keywords if keyword in resume_lower)
    
    job_tech_count = sum(1 for keyword in tech_keywords if keyword in job_lower)
    job_commerce_count = sum(1 for keyword in commerce_keywords if keyword in job_lower)
    job_hr_count = sum(1 for keyword in hr_keywords if keyword in job_lower)
    job_healthcare_count = sum(1 for keyword in healthcare_keywords if keyword in job_lower)
    
    # Determine dominant domains
    resume_domain = get_dominant_domain(resume_tech_count, resume_commerce_count, 
                                      resume_hr_count, resume_healthcare_count)
    job_domain = get_dominant_domain(job_tech_count, job_commerce_count, 
                                   job_hr_count, job_healthcare_count)
    
    # Apply domain matching logic
    if resume_domain == job_domain and resume_domain != 'general':
        # Same domain - boost score slightly
        adjusted_score = min(base_score * 1.1, 100)
        reasoning = f"Strong domain match ({resume_domain}) with semantic similarity analysis."
    
    elif resume_domain != job_domain and resume_domain != 'general' and job_domain != 'general':
        # Different domains - severe penalty
        penalty_factor = 0.15  # Reduce score to 15% of original (more strict)
        adjusted_score = base_score * penalty_factor
        reasoning = f"Significant domain mismatch: Resume is {resume_domain}-focused while job requires {job_domain} expertise. Very low compatibility."
    
    elif resume_domain == 'general' or job_domain == 'general':
        # One is general - moderate penalty
        penalty_factor = 0.7  # Reduce score to 70% of original
        adjusted_score = base_score * penalty_factor
        reasoning = "Mixed domain match with semantic similarity analysis."
    
    else:
        # Default case
        adjusted_score = base_score
        reasoning = "Semantic similarity based on content analysis."
    
    return round(adjusted_score, 2), reasoning

def get_dominant_domain(tech_count, commerce_count, hr_count, healthcare_count):
    """Determine the dominant domain based on keyword counts"""
    
    domain_counts = {
        'technology': tech_count,
        'commerce': commerce_count,
        'hr': hr_count,
        'healthcare': healthcare_count
    }
    
    max_count = max(domain_counts.values())
    
    # Need at least 3 keywords to be considered domain-specific
    if max_count >= 3:
        return max(domain_counts, key=domain_counts.get)
    else:
        return 'general'
