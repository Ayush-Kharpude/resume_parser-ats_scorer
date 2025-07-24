# Smart Resume Analysis System
# No external API dependencies - fast, reliable, and personalized

def get_resume_suggestions(resume_text, job_text, api_key=None):
    """Get intelligent resume suggestions using smart rule-based analysis"""
    return generate_smart_suggestions(resume_text, job_text)

def generate_smart_suggestions(resume_text, job_text):
    """Generate intelligent suggestions by analyzing resume vs job description"""
    
    resume_lower = resume_text.lower()
    job_lower = job_text.lower()
    
    suggestions = []
    
    # 1. CONTENT IMPROVEMENTS
    suggestions.append("## 📝 Content Improvements")
    
    # Check for quantifiable achievements
    has_numbers = any(char.isdigit() for char in resume_text)
    if not has_numbers or resume_text.count('%') < 2:
        suggestions.append("• **Add quantifiable achievements**: Include specific numbers, percentages, and metrics (e.g., 'Improved performance by 25%', 'Managed team of 5 developers')")
    
    # Check for project mentions
    project_keywords = ['project', 'built', 'developed', 'created', 'implemented']
    project_mentions = sum(1 for keyword in project_keywords if keyword in resume_lower)
    if project_mentions < 3:
        suggestions.append("• **Highlight more projects**: Add 2-3 relevant projects that demonstrate your technical skills")
    
    # Check for leadership/teamwork
    leadership_keywords = ['led', 'managed', 'coordinated', 'collaborated', 'team']
    leadership_mentions = sum(1 for keyword in leadership_keywords if keyword in resume_lower)
    if leadership_mentions < 2:
        suggestions.append("• **Emphasize teamwork**: Include examples of collaboration, leadership, or team projects")
    
    # 2. SKILLS ENHANCEMENT
    suggestions.append("\n## 🛠️ Skills Enhancement")
    
    # Find job-required skills missing from resume
    job_skills = extract_skills_from_text(job_text)
    resume_skills = extract_skills_from_text(resume_text)
    missing_skills = [skill for skill in job_skills if skill not in [rs.lower() for rs in resume_skills]]
    
    if missing_skills:
        suggestions.append(f"• **Learn these in-demand skills**: {', '.join(missing_skills[:5])}")
    
    # Check for certifications
    cert_keywords = ['certified', 'certification', 'certificate']
    has_certs = any(keyword in resume_lower for keyword in cert_keywords)
    if not has_certs:
        suggestions.append("• **Add relevant certifications**: Consider getting certified in technologies mentioned in the job description")
    
    # 3. KEYWORDS & OPTIMIZATION
    suggestions.append("\n## 🔍 Keywords & ATS Optimization")
    
    # Find important job keywords missing from resume
    important_job_words = extract_important_keywords(job_text)
    missing_keywords = [word for word in important_job_words if word.lower() not in resume_lower]
    
    if missing_keywords:
        suggestions.append(f"• **Include these job keywords**: {', '.join(missing_keywords[:6])}")
    
    # Check for action verbs
    action_verbs = ['developed', 'implemented', 'designed', 'optimized', 'managed', 'created']
    action_verb_count = sum(1 for verb in action_verbs if verb in resume_lower)
    if action_verb_count < 4:
        suggestions.append("• **Use more action verbs**: Start bullet points with strong verbs like 'Developed', 'Implemented', 'Optimized'")
    
    # 4. FORMATTING & STRUCTURE
    suggestions.append("\n## 📋 Formatting & Structure")
    
    # Check resume length
    word_count = len(resume_text.split())
    if word_count < 200:
        suggestions.append("• **Expand content**: Your resume seems short. Add more details about your experience and projects")
    elif word_count > 800:
        suggestions.append("• **Condense content**: Keep it concise - aim for 1-2 pages maximum")
    
    # Check for bullet points
    bullet_count = resume_text.count('•') + resume_text.count('-') + resume_text.count('*')
    if bullet_count < 5:
        suggestions.append("• **Use bullet points**: Format achievements and responsibilities as bullet points for better readability")
    
    # 5. SPECIFIC RECOMMENDATIONS
    suggestions.append("\n## 🎯 Specific Recommendations for This Role")
    
    # Role-specific suggestions based on job description
    if 'full stack' in job_lower or 'fullstack' in job_lower:
        suggestions.append("• **Highlight full-stack projects**: Showcase projects that demonstrate both frontend and backend skills")
    
    if 'senior' in job_lower or 'lead' in job_lower:
        suggestions.append("• **Emphasize leadership**: Add examples of mentoring, code reviews, or technical decision-making")
    
    if 'startup' in job_lower or 'fast-paced' in job_lower:
        suggestions.append("• **Show adaptability**: Highlight experience with rapid development, multiple technologies, or wearing multiple hats")
    
    if 'remote' in job_lower:
        suggestions.append("• **Mention remote experience**: If you have remote work experience, highlight your self-management and communication skills")
    
    # 6. FINAL TIPS
    suggestions.append("\n## 💡 Pro Tips")
    suggestions.append("• **Tailor for each application**: Customize your resume for each job by emphasizing relevant skills")
    suggestions.append("• **Use consistent formatting**: Ensure dates, fonts, and spacing are uniform throughout")
    suggestions.append("• **Proofread carefully**: Check for typos and grammatical errors")
    suggestions.append("• **Include a summary**: Add a 2-3 line professional summary at the top")
    
    return '\n'.join(suggestions)

def extract_skills_from_text(text):
    """Extract technical skills from text"""
    skills = [
        'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'Express.js', 
        'MongoDB', 'MySQL', 'PostgreSQL', 'AWS', 'Docker', 'Git', 'HTML', 
        'CSS', 'TypeScript', 'Angular', 'Vue.js', 'Django', 'Flask', 'REST API',
        'GraphQL', 'Kubernetes', 'Jenkins', 'Azure', 'GCP', 'Redis', 'Postman'
    ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def extract_important_keywords(job_text):
    """Extract important keywords from job description"""
    # Common important job keywords
    keywords = [
        'experience', 'development', 'software', 'application', 'system',
        'design', 'implementation', 'testing', 'deployment', 'maintenance',
        'collaboration', 'agile', 'scrum', 'problem-solving', 'optimization',
        'scalable', 'performance', 'security', 'architecture', 'integration'
    ]
    
    found_keywords = []
    job_lower = job_text.lower()
    for keyword in keywords:
        if keyword in job_lower:
            found_keywords.append(keyword.title())
    
    return found_keywords[:8]  # Return top 8 most relevant

def analyze_skill_gaps(resume_skills, job_text):
    """Analyze skill gaps between resume and job requirements"""
    # Comprehensive skill categories covering multiple domains
    all_skills = {
        # Technology Skills
        "tech": [
            "Python", "JavaScript", "Java", "TypeScript", "C++", "C#", "PHP", "Ruby",
            "React", "Angular", "Vue.js", "HTML", "CSS", "Bootstrap", "Tailwind",
            "Node.js", "Express.js", "Django", "Flask", "Spring", "Laravel",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
            "REST API", "GraphQL", "Postman", "Jenkins", "CI/CD"
        ],
        
        # Business & Commerce Skills
        "business": [
            "Sales", "Marketing", "Business Development", "Account Management",
            "Customer Service", "CRM", "Lead Generation", "Negotiation",
            "Market Research", "Business Analysis", "Project Management",
            "Excel", "PowerBI", "Tableau", "Analytics", "Reporting",
            "E-commerce", "Digital Marketing", "SEO", "SEM", "Social Media",
            "Content Marketing", "Email Marketing", "Brand Management"
        ],
        
        # Finance & Accounting Skills
        "finance": [
            "Accounting", "Financial Analysis", "Budgeting", "Forecasting",
            "Tax Preparation", "Audit", "Compliance", "Risk Management",
            "Investment Analysis", "Portfolio Management", "Banking",
            "QuickBooks", "SAP", "Oracle", "Financial Modeling"
        ],
        
        # HR & Management Skills
        "hr": [
            "Human Resources", "Recruitment", "Talent Acquisition", "Hiring",
            "Employee Relations", "Performance Management", "Training",
            "Onboarding", "Payroll", "Benefits Administration", "HR Policies",
            "Leadership", "Team Management", "Coaching", "Mentoring"
        ],
        
        # Design & Creative Skills
        "design": [
            "Graphic Design", "UI/UX Design", "Web Design", "Photoshop",
            "Illustrator", "Figma", "Sketch", "InDesign", "After Effects",
            "Branding", "Typography", "Color Theory", "Wireframing", "Prototyping"
        ]
    }
    
    job_text_lower = job_text.lower()
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    
    # Find all skills mentioned in job description across all categories
    job_required_skills = []
    for category, skills in all_skills.items():
        for skill in skills:
            if skill.lower() in job_text_lower:
                job_required_skills.append(skill)
    
    # Remove duplicates and limit to top 10 most important
    job_required_skills = list(dict.fromkeys(job_required_skills))[:10]
    
    # If no specific skills found, extract general requirements from job text
    if not job_required_skills:
        # Look for general skill patterns in job description
        general_requirements = extract_general_requirements(job_text)
        job_required_skills = general_requirements[:5]
    
    # Find missing skills
    missing_skills = []
    for skill in job_required_skills:
        if skill.lower() not in resume_skills_lower:
            missing_skills.append(skill)
    
    # Limit missing skills to top 5 most critical
    missing_skills = missing_skills[:5]
    
    # Find matching skills
    matching_skills = []
    for skill in job_required_skills:
        if skill.lower() in resume_skills_lower:
            matching_skills.append(skill)
    
    return {
        "job_required_skills": job_required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": (len(matching_skills) / len(job_required_skills) * 100) if job_required_skills else 0
    }

def extract_general_requirements(job_text):
    """Extract general requirements when specific skills aren't found"""
    job_lower = job_text.lower()
    
    # Common requirement patterns
    general_requirements = []
    
    # Look for experience requirements
    if 'experience' in job_lower:
        if any(word in job_lower for word in ['sales', 'selling', 'revenue']):
            general_requirements.append("Sales Experience")
        if any(word in job_lower for word in ['marketing', 'promotion', 'campaign']):
            general_requirements.append("Marketing Experience")
        if any(word in job_lower for word in ['management', 'leadership', 'team']):
            general_requirements.append("Management Experience")
        if any(word in job_lower for word in ['customer', 'client', 'service']):
            general_requirements.append("Customer Service")
    
    # Look for education requirements
    if any(word in job_lower for word in ['degree', 'bachelor', 'master', 'education']):
        general_requirements.append("Relevant Degree")
    
    # Look for communication requirements
    if any(word in job_lower for word in ['communication', 'presentation', 'writing']):
        general_requirements.append("Communication Skills")
    
    # Look for analytical requirements
    if any(word in job_lower for word in ['analysis', 'analytical', 'data', 'report']):
        general_requirements.append("Analytical Skills")
    
    # Look for software requirements
    if any(word in job_lower for word in ['software', 'computer', 'microsoft', 'excel']):
        general_requirements.append("Computer Skills")
    
    return general_requirements if general_requirements else ["Domain Knowledge", "Professional Experience"]