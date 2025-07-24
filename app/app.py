import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import base64
import requests
import re
from backend.resume_parser import extract_resume_data
from backend.job_parser import extract_job_description
from backend.matcher import generate_match_score
from auth.auth_handler import check_auth
from utils.supabase_client import supabase
from utils.gemini_helper import get_resume_suggestions, analyze_skill_gaps

def classify_resume_role(resume_text):
    """Simple rule-based resume classifier"""
    resume_lower = resume_text.lower()
    
    # Define role keywords
    role_keywords = {
        'Software Developer': [
            'python', 'javascript', 'java', 'programming', 'coding', 'software development',
            'web development', 'react', 'node.js', 'html', 'css', 'git', 'github',
            'api', 'database', 'sql', 'frontend', 'backend', 'fullstack'
        ],
        'Data Scientist': [
            'machine learning', 'data science', 'python', 'pandas', 'numpy', 'tensorflow',
            'pytorch', 'scikit-learn', 'data analysis', 'statistics', 'ml', 'ai',
            'artificial intelligence', 'deep learning', 'neural networks'
        ],
        'Web Designer': [
            'web design', 'ui/ux', 'photoshop', 'illustrator', 'figma', 'adobe',
            'graphic design', 'css', 'html', 'responsive design', 'wireframes',
            'prototyping', 'user interface', 'user experience'
        ],
        'Business Analyst': [
            'business analysis', 'requirements', 'stakeholder', 'process improvement',
            'business intelligence', 'analytics', 'reporting', 'excel', 'powerbi',
            'tableau', 'project management', 'agile', 'scrum'
        ],
        'Marketing Specialist': [
            'marketing', 'digital marketing', 'social media', 'seo', 'content marketing',
            'advertising', 'campaigns', 'brand', 'promotion', 'market research',
            'google analytics', 'facebook ads', 'email marketing'
        ],
        'Sales Representative': [
            'sales', 'business development', 'client relations', 'crm', 'lead generation',
            'negotiation', 'revenue', 'targets', 'customer service', 'account management',
            'b2b', 'b2c', 'sales funnel'
        ]
    }
    
    # Count keyword matches for each role
    role_scores = {}
    for role, keywords in role_keywords.items():
        score = sum(1 for keyword in keywords if keyword in resume_lower)
        role_scores[role] = score
    
    # Find the role with highest score
    if max(role_scores.values()) > 0:
        predicted_role = max(role_scores, key=role_scores.get)
    else:
        predicted_role = "General"  # Default if no specific role detected
    
    return predicted_role

# ✅ Page Config
st.set_page_config(page_title="AI Resume Tool", layout="wide", page_icon="🧠")

# 🔒 Auth Check
if not check_auth():
    st.warning("Please log in to use the app.")
    st.stop()

# 🎨 Enhanced Modern UI CSS
st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #0f1419 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main Title */
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
        }
        
        .subtitle {
            font-size: 1.2rem;
            text-align: center;
            color: #8b949e;
            margin-bottom: 3rem;
            font-weight: 400;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(22, 27, 34, 0.8);
            border-radius: 12px;
            padding: 8px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(48, 54, 61, 0.5);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 8px;
            color: #8b949e;
            font-weight: 500;
            padding: 12px 20px;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Card Styling */
        .feature-card {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 16px;
            padding: 2rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
            border-color: rgba(102, 126, 234, 0.3);
        }
        
        /* Upload Area */
        .upload-area {
            background: rgba(22, 27, 34, 0.6);
            border: 2px dashed rgba(102, 126, 234, 0.4);
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: rgba(102, 126, 234, 0.8);
            background: rgba(102, 126, 234, 0.05);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Metrics */
        [data-testid="metric-container"] {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Success/Error Messages */
        .stSuccess {
            background: rgba(46, 160, 67, 0.1);
            border: 1px solid rgba(46, 160, 67, 0.3);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .stError {
            background: rgba(248, 81, 73, 0.1);
            border: 1px solid rgba(248, 81, 73, 0.3);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .stInfo {
            background: rgba(56, 139, 253, 0.1);
            border: 1px solid rgba(56, 139, 253, 0.3);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: rgba(22, 27, 34, 0.8);
            border-radius: 12px;
            border: 1px solid rgba(48, 54, 61, 0.5);
        }
        
        /* Progress Bar */
        .stProgress > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: rgba(13, 17, 23, 0.95);
            backdrop-filter: blur(10px);
        }
        
        /* Text Input */
        .stTextInput > div > div > input {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 12px;
            color: #f0f6fc;
            backdrop-filter: blur(10px);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: rgba(102, 126, 234, 0.8);
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        /* Text Area */
        .stTextArea > div > div > textarea {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 12px;
            color: #f0f6fc;
            backdrop-filter: blur(10px);
        }
        
        /* Select Box */
        .stSelectbox > div > div {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        /* File Uploader */
        .stFileUploader > div {
            background: rgba(22, 27, 34, 0.6);
            border: 2px dashed rgba(102, 126, 234, 0.4);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 4rem 2rem;
            background: rgba(22, 27, 34, 0.3);
            border-radius: 20px;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(48, 54, 61, 0.3);
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #8b949e;
            margin-bottom: 2rem;
            font-weight: 400;
            line-height: 1.6;
        }
        
        /* Feature Icons */
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        /* Glassmorphism Effect */
        .glass-card {
            background: rgba(22, 27, 34, 0.25);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Animation */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-section animate-fade-in">
        <div class="hero-title">Smart Resume Analyzer</div>
        <div class="hero-subtitle">
            Get instant ATS scores, skill analysis, and personalized recommendations to make your resume stand out in today's competitive job market.
        </div>
    </div>
""", unsafe_allow_html=True)

# Feature Cards Section
st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 3rem 0;">
        <div class="glass-card animate-fade-in">
            <div class="feature-icon">⚡</div>
            <h3 style="color: #667eea; margin-bottom: 1rem;">Instant Analysis</h3>
            <p style="color: #8b949e; line-height: 1.6;">Get detailed resume analysis and ATS scores in seconds</p>
        </div>
        <div class="glass-card animate-fade-in">
            <div class="feature-icon">🤖</div>
            <h3 style="color: #667eea; margin-bottom: 1rem;">AI-Powered Insights</h3>
            <p style="color: #8b949e; line-height: 1.6;">Advanced AI analyzes your resume against industry standards</p>
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Resume Classifier (Instant Role Prediction)",
    "🤖 ATS Score Generator", 
    "🏢 Recruiter Dashboard",
    "⭐ Shortlisted Candidates",
    "📊 Prediction History"
])

# ============================
# 🧠 TAB 1: Resume Classifier
# ============================
with tab1:
    st.markdown("<div class='big-title'>📄 Resume Classifier</div>", unsafe_allow_html=True)
    st.markdown("#### Upload your resume and get predicted job role instantly!")

    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

    if uploaded_file:
        st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
        
        try:
            # Extract resume data directly in Streamlit
            with st.spinner("🔍 Analyzing your resume..."):
                resume_text, resume_data = extract_resume_data(uploaded_file)
                
                # For now, we'll use a simple rule-based classifier
                # You can replace this with your trained model later
                predicted_label = classify_resume_role(resume_text)
                
                # Save to database
                try:
                    supabase.table("resumes").insert({
                        "filename": uploaded_file.name,
                        "predicted_label": predicted_label,
                        "original_text": resume_text[:1000],  # Limit text length for database
                        "user_email": "user@example.com"  # You can add user authentication later
                    }).execute()
                    
                    # Trigger refresh for Prediction History tab
                    if 'refresh_trigger' not in st.session_state:
                        st.session_state.refresh_trigger = 0
                    st.session_state.refresh_trigger += 1
                    
                    st.success(f"🎯 Predicted Role: **{predicted_label}**")
                    st.info("✅ Prediction saved to history!")
                    
                except Exception as db_error:
                    st.success(f"🎯 Predicted Role: **{predicted_label}**")
                    st.warning(f"⚠️ Could not save to database: {str(db_error)}")
                
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

# ============================
# 📌 TAB 2: ATS Score Generator
# ============================
with tab2:
    st.markdown("### 🤖 ATS Score Generator")
    resume_file = st.file_uploader("Upload Resume", type=["pdf"], key="resume")
    job_file = st.file_uploader("Upload Job Description", type=["pdf", "txt"], key="job")

    def clean_text(text):
        text = re.sub(r"\(cid:\d+\)", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    if st.button("Generate ATS Score"):
        if resume_file and job_file:
            resume_text, resume_data = extract_resume_data(resume_file)
            job_text = extract_job_description(job_file)
            
            # Clean the resume text
            cleaned_resume_text = clean_text(resume_text)
            
            score, reasoning = generate_match_score(cleaned_resume_text, job_text)

            # Display match score
            st.success(f"✅ Match Score: {score:.2f}%")
            
            # Display resume insights
            st.markdown("## 🧾 Resume Insights")
            
            # Contact Info Section
            st.markdown("### 📧 Contact Info")
            name = resume_data.get('name', 'Not Found')
            email = resume_data.get('email', 'Not Found') 
            phone = resume_data.get('phone', 'Not Found')
            
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Phone:** {phone}")
            
            # Skills Section
            st.markdown("### 🛠️ Skills")
            skills = resume_data.get('skills', [])
            if skills:
                st.write(", ".join(skills))
            else:
                st.write("No skills found.")
            
            # Resume Text Snippet Section
            st.markdown("### 📄 Resume Text Snippet")
            text_snippet = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            st.write(text_snippet)
            
            # Matching Reasoning Section
            st.markdown("### 🤔 Matching Reasoning")
            st.write(reasoning)
            
            # Skill Gap Analysis Section
            st.markdown("## 🎯 Skill Gap Analysis")
            skill_analysis = analyze_skill_gaps(skills, job_text)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Skills You Have")
                if skill_analysis["matching_skills"]:
                    for skill in skill_analysis["matching_skills"]:
                        st.write(f"• {skill}")
                else:
                    st.write("No matching skills found")
            
            with col2:
                st.markdown("#### ❌ Skills You're Missing")
                if skill_analysis["missing_skills"]:
                    for skill in skill_analysis["missing_skills"]:
                        st.write(f"• {skill}")
                else:
                    st.write("No missing skills - Great job!")
            
            # Skill match percentage
            skill_match_percent = skill_analysis["match_percentage"]
            st.metric("🎯 Skill Match Rate", f"{skill_match_percent:.1f}%")
            
            if skill_match_percent < 50:
                st.warning("⚠️ Low skill match. Consider learning the missing skills to improve your chances.")
            elif skill_match_percent < 75:
                st.info("📈 Good skill match. Learning a few more skills could boost your profile.")
            else:
                st.success("🎉 Excellent skill match! You're well-qualified for this role.")
            
            # AI Resume Suggestions Section
            st.markdown("## 🤖 AI Resume Improvement Suggestions")
            
            # Get intelligent suggestions automatically
            with st.spinner("🤖 AI is analyzing your resume..."):
                suggestions = get_resume_suggestions(cleaned_resume_text, job_text)
            
            st.markdown("### 💡 Personalized Suggestions")
            st.markdown(suggestions)
        else:
            st.warning("Please upload both files to generate score.")

# ============================
# 🏢 TAB 3: Recruiter Dashboard
# ============================
with tab3:
    st.markdown("### 🏢 Recruiter Dashboard - Batch Resume Processing")
    st.markdown("Upload multiple resumes and compare them against your job requirements")
    
    # Job Description Section
    st.markdown("## 📋 Step 1: Job Requirements")
    
    # Job Title
    job_title = st.text_input("Job Title", placeholder="e.g., Senior Full Stack Developer")
    
    # Job Description Input Options
    st.markdown("#### Choose Job Description Input Method:")
    input_method = st.radio(
        "How would you like to provide the job description?",
        ["📝 Type/Paste Text", "📁 Upload TXT File"],
        horizontal=True
    )
    
    job_description_text = ""
    
    if input_method == "📝 Type/Paste Text":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_description_text = st.text_area(
                "Job Description", 
                height=200,
                placeholder="Paste your complete job description here..."
            )
        
        with col2:
            st.markdown("#### Quick Templates")
            if st.button("🔧 Tech Role Template"):
                job_description_text = """We are looking for a Senior Full Stack Developer to join our team.

Requirements:
- 3+ years of experience in web development
- Proficiency in JavaScript, React, Node.js
- Experience with databases (MySQL, MongoDB)
- Knowledge of REST APIs and microservices
- Familiarity with cloud platforms (AWS, Azure)
- Strong problem-solving skills
- Experience with Git and version control

Responsibilities:
- Develop and maintain web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Troubleshoot and debug applications"""
                st.rerun()
            
            if st.button("💼 Business Role Template"):
                job_description_text = """We are seeking a Business Development Manager to drive growth.

Requirements:
- 2+ years in sales or business development
- Strong communication and negotiation skills
- Experience with CRM systems
- Knowledge of market research and analysis
- Bachelor's degree in Business or related field
- Proven track record of meeting targets

Responsibilities:
- Identify new business opportunities
- Build and maintain client relationships
- Develop sales strategies
- Conduct market research
- Prepare proposals and presentations"""
                st.rerun()
    
    else:  # Upload TXT File
        uploaded_job_file = st.file_uploader(
            "Upload Job Description (TXT file)", 
            type=["txt"],
            key="job_description_file"
        )
        
        if uploaded_job_file:
            try:
                # Read the uploaded file
                job_description_text = uploaded_job_file.read().decode("utf-8")
                st.success(f"✅ Job description loaded from {uploaded_job_file.name}")
                
                # Show preview
                with st.expander("📄 Job Description Preview"):
                    st.text(job_description_text[:500] + "..." if len(job_description_text) > 500 else job_description_text)
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                job_description_text = ""
    
    # Resume Upload Section
    st.markdown("## 📁 Step 2: Upload Resumes")
    uploaded_resumes = st.file_uploader(
        "Upload Multiple Resumes (PDF only)", 
        type=["pdf"], 
        accept_multiple_files=True,
        key="batch_resumes"
    )
    
    if uploaded_resumes:
        st.success(f"✅ {len(uploaded_resumes)} resumes uploaded successfully!")
        
        # Display uploaded files
        with st.expander("📋 Uploaded Files"):
            for i, resume in enumerate(uploaded_resumes, 1):
                st.write(f"{i}. {resume.name} ({resume.size} bytes)")
    
    # Process Button
    if st.button("🚀 Process All Resumes", disabled=not (job_description_text and uploaded_resumes)):
        if job_description_text and uploaded_resumes:
            
            # Initialize results storage
            if 'batch_results' not in st.session_state:
                st.session_state.batch_results = []
            
            st.session_state.batch_results = []  # Clear previous results
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process each resume
            for i, resume_file in enumerate(uploaded_resumes):
                status_text.text(f"Processing {resume_file.name}...")
                
                try:
                    # Extract resume data
                    resume_text, resume_data = extract_resume_data(resume_file)
                    cleaned_resume_text = clean_text(resume_text)
                    
                    # Generate match score
                    score, reasoning = generate_match_score(cleaned_resume_text, job_description_text)
                    
                    # Analyze skills
                    skills = resume_data.get('skills', [])
                    skill_analysis = analyze_skill_gaps(skills, job_description_text)
                    
                    # Store results
                    result = {
                        'filename': resume_file.name,
                        'name': resume_data.get('name', 'Not Found'),
                        'email': resume_data.get('email', 'Not Found'),
                        'phone': resume_data.get('phone', 'Not Found'),
                        'match_score': score,
                        'reasoning': reasoning,
                        'skills': skills,
                        'matching_skills': skill_analysis["matching_skills"],
                        'missing_skills': skill_analysis["missing_skills"],
                        'skill_match_percent': skill_analysis["match_percentage"],
                        'resume_text': resume_text[:300] + "..." if len(resume_text) > 300 else resume_text
                    }
                    
                    st.session_state.batch_results.append(result)
                    
                except Exception as e:
                    st.error(f"Error processing {resume_file.name}: {str(e)}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_resumes))
            
            status_text.text("✅ Processing complete!")
            st.success(f"🎉 Successfully processed {len(st.session_state.batch_results)} resumes!")
    
    # Display Results
    if 'batch_results' in st.session_state and st.session_state.batch_results:
        st.markdown("## 📊 Results Dashboard")
        
        # Summary Statistics
        results = st.session_state.batch_results
        avg_score = sum(r['match_score'] for r in results) / len(results)
        top_score = max(r['match_score'] for r in results)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Candidates", len(results))
        with col2:
            st.metric("📈 Average Score", f"{avg_score:.1f}%")
        with col3:
            st.metric("🏆 Top Score", f"{top_score:.1f}%")
        with col4:
            qualified_count = len([r for r in results if r['match_score'] >= 50])
            st.metric("✅ Qualified (≥50%)", qualified_count)
        
        # Filtering Options
        st.markdown("### 🔍 Filter & Sort Candidates")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score = st.slider("Minimum Match Score", 0, 100, 0, 5)
        with col2:
            sort_by = st.selectbox("Sort By", ["Match Score (High to Low)", "Match Score (Low to High)", "Name (A-Z)", "Skill Match %"])
        with col3:
            required_skill = st.selectbox("Must Have Skill", ["Any"] + list(set(skill for r in results for skill in r['skills'])))
        
        # Apply filters
        filtered_results = results.copy()
        
        # Filter by minimum score
        filtered_results = [r for r in filtered_results if r['match_score'] >= min_score]
        
        # Filter by required skill
        if required_skill != "Any":
            filtered_results = [r for r in filtered_results if required_skill in r['skills']]
        
        # Sort results
        if sort_by == "Match Score (High to Low)":
            filtered_results.sort(key=lambda x: x['match_score'], reverse=True)
        elif sort_by == "Match Score (Low to High)":
            filtered_results.sort(key=lambda x: x['match_score'])
        elif sort_by == "Name (A-Z)":
            filtered_results.sort(key=lambda x: x['name'])
        elif sort_by == "Skill Match %":
            filtered_results.sort(key=lambda x: x['skill_match_percent'], reverse=True)
        
        st.write(f"**Showing {len(filtered_results)} of {len(results)} candidates**")
        
        # Results Table
        if filtered_results:
            # Create DataFrame for export
            export_data = []
            for result in filtered_results:
                export_data.append({
                    'Rank': filtered_results.index(result) + 1,
                    'Name': result['name'],
                    'Email': result['email'],
                    'Phone': result['phone'],
                    'Match Score (%)': result['match_score'],
                    'Skill Match (%)': result['skill_match_percent'],
                    'Skills': ', '.join(result['skills'][:5]),  # Top 5 skills
                    'Missing Skills': ', '.join(result['missing_skills'][:3]),  # Top 3 missing
                    'Filename': result['filename']
                })
            
            df = pd.DataFrame(export_data)
            
            # Export Options
            col1, col2 = st.columns([3, 1])
            with col2:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv,
                    file_name=f"candidate_analysis_{job_title.replace(' ', '_') if job_title else 'job'}.csv",
                    mime="text/csv"
                )
            
            # Display detailed results
            for i, result in enumerate(filtered_results):
                with st.expander(f"#{i+1} {result['name']} - {result['match_score']:.1f}% Match"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**📧 Email:** {result['email']}")
                        st.write(f"**📱 Phone:** {result['phone']}")
                        st.write(f"**📄 File:** {result['filename']}")
                        
                        st.write(f"**🎯 Match Score:** {result['match_score']:.1f}%")
                        st.write(f"**🛠️ Skill Match:** {result['skill_match_percent']:.1f}%")
                        
                        st.write("**💭 Reasoning:**")
                        st.write(result['reasoning'])
                        
                        st.write("**📄 Resume Preview:**")
                        st.text(result['resume_text'])
                    
                    with col2:
                        if result['matching_skills']:
                            st.write("**✅ Matching Skills:**")
                            for skill in result['matching_skills']:
                                st.write(f"• {skill}")
                        
                        if result['missing_skills']:
                            st.write("**❌ Missing Skills:**")
                            for skill in result['missing_skills'][:5]:
                                st.write(f"• {skill}")
                        
                        # Quick Actions
                        st.write("**🚀 Quick Actions:**")
                        if st.button(f"📧 Shortlist", key=f"shortlist_{i}"):
                            # Initialize shortlist in session state
                            if 'shortlisted_candidates' not in st.session_state:
                                st.session_state.shortlisted_candidates = []
                            
                            # Add candidate to shortlist if not already there
                            candidate_id = f"{result['name']}_{result['email']}"
                            existing_ids = [f"{c['name']}_{c['email']}" for c in st.session_state.shortlisted_candidates]
                            
                            if candidate_id not in existing_ids:
                                shortlist_entry = result.copy()
                                shortlist_entry['shortlisted_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                                shortlist_entry['job_title'] = job_title if job_title else "Unknown Position"
                                st.session_state.shortlisted_candidates.append(shortlist_entry)
                                st.success(f"✅ {result['name']} added to shortlist!")
                            else:
                                st.info(f"ℹ️ {result['name']} is already in shortlist!")
                        
                        if result['match_score'] >= 70:
                            st.success("🌟 Highly Recommended")
                        elif result['match_score'] >= 50:
                            st.info("👍 Good Candidate")
                        elif result['match_score'] >= 30:
                            st.warning("⚠️ Needs Review")
                        else:
                            st.error("❌ Poor Match")
        else:
            st.info("No candidates match your current filters.")

# ============================
# ⭐ TAB 4: Shortlisted Candidates
# ============================
with tab4:
    st.markdown("### ⭐ Shortlisted Candidates")
    st.markdown("Manage and review your shortlisted candidates")
    
    # Initialize shortlist if not exists
    if 'shortlisted_candidates' not in st.session_state:
        st.session_state.shortlisted_candidates = []
    
    shortlisted = st.session_state.shortlisted_candidates
    
    if shortlisted:
        # Summary Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⭐ Total Shortlisted", len(shortlisted))
        
        with col2:
            avg_score = sum(c['match_score'] for c in shortlisted) / len(shortlisted)
            st.metric("📈 Average Score", f"{avg_score:.1f}%")
        
        with col3:
            top_score = max(c['match_score'] for c in shortlisted)
            st.metric("🏆 Top Score", f"{top_score:.1f}%")
        
        with col4:
            unique_positions = len(set(c.get('job_title', 'Unknown') for c in shortlisted))
            st.metric("💼 Positions", unique_positions)
        
        # Action Buttons
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export Shortlist"):
                # Create export data
                export_data = []
                for i, candidate in enumerate(shortlisted, 1):
                    export_data.append({
                        'Rank': i,
                        'Name': candidate['name'],
                        'Email': candidate['email'],
                        'Phone': candidate['phone'],
                        'Position': candidate.get('job_title', 'Unknown'),
                        'Match Score (%)': candidate['match_score'],
                        'Skill Match (%)': candidate['skill_match_percent'],
                        'Skills': ', '.join(candidate['skills'][:5]),
                        'Shortlisted At': candidate.get('shortlisted_at', 'Unknown'),
                        'Filename': candidate['filename']
                    })
                
                df_export = pd.DataFrame(export_data)
                csv_data = df_export.to_csv(index=False)
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"shortlisted_candidates_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📧 Export Email List"):
                email_list = [c['email'] for c in shortlisted if c['email'] != 'Not Found']
                email_text = '\n'.join(email_list)
                
                st.download_button(
                    label="📧 Download Emails",
                    data=email_text,
                    file_name=f"shortlisted_emails_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col3:
            if st.button("🗑️ Clear All Shortlist"):
                st.session_state.shortlisted_candidates = []
                st.success("✅ Shortlist cleared!")
                st.rerun()
        
        # Filtering and Sorting
        st.markdown("### 🔍 Filter & Sort Shortlist")
        col1, col2 = st.columns(2)
        
        with col1:
            # Position filter
            all_positions = ["All Positions"] + list(set(c.get('job_title', 'Unknown') for c in shortlisted))
            selected_position = st.selectbox("💼 Filter by Position", all_positions)
        
        with col2:
            # Sort options
            sort_option = st.selectbox("📊 Sort By", [
                "Match Score (High to Low)",
                "Match Score (Low to High)", 
                "Name (A-Z)",
                "Recently Added"
            ])
        
        # Apply filters
        filtered_shortlist = shortlisted.copy()
        
        if selected_position != "All Positions":
            filtered_shortlist = [c for c in filtered_shortlist if c.get('job_title', 'Unknown') == selected_position]
        
        # Apply sorting
        if sort_option == "Match Score (High to Low)":
            filtered_shortlist.sort(key=lambda x: x['match_score'], reverse=True)
        elif sort_option == "Match Score (Low to High)":
            filtered_shortlist.sort(key=lambda x: x['match_score'])
        elif sort_option == "Name (A-Z)":
            filtered_shortlist.sort(key=lambda x: x['name'])
        elif sort_option == "Recently Added":
            filtered_shortlist.sort(key=lambda x: x.get('shortlisted_at', ''), reverse=True)
        
        st.write(f"**Showing {len(filtered_shortlist)} of {len(shortlisted)} shortlisted candidates**")
        
        # Display shortlisted candidates
        st.markdown("### 📋 Shortlisted Candidates Details")
        
        for i, candidate in enumerate(filtered_shortlist):
            with st.expander(f"⭐ {candidate['name']} - {candidate['match_score']:.1f}% Match ({candidate.get('job_title', 'Unknown Position')})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**📧 Email:** {candidate['email']}")
                    st.write(f"**📱 Phone:** {candidate['phone']}")
                    st.write(f"**📄 File:** {candidate['filename']}")
                    st.write(f"**💼 Position:** {candidate.get('job_title', 'Unknown')}")
                    st.write(f"**⭐ Shortlisted:** {candidate.get('shortlisted_at', 'Unknown')}")
                    
                    st.write(f"**🎯 Match Score:** {candidate['match_score']:.1f}%")
                    st.write(f"**🛠️ Skill Match:** {candidate['skill_match_percent']:.1f}%")
                    
                    st.write("**💭 Reasoning:**")
                    st.write(candidate['reasoning'])
                    
                    st.write("**📄 Resume Preview:**")
                    st.text(candidate['resume_text'])
                
                with col2:
                    if candidate['matching_skills']:
                        st.write("**✅ Matching Skills:**")
                        for skill in candidate['matching_skills']:
                            st.write(f"• {skill}")
                    
                    if candidate['missing_skills']:
                        st.write("**❌ Missing Skills:**")
                        for skill in candidate['missing_skills'][:5]:
                            st.write(f"• {skill}")
                    
                    # Action buttons for individual candidates
                    st.write("**🚀 Actions:**")
                    
                    if st.button(f"📧 Contact", key=f"contact_{i}"):
                        st.info(f"📧 Email: {candidate['email']}")
                        st.info(f"📱 Phone: {candidate['phone']}")
                    
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        # Remove from shortlist
                        candidate_id = f"{candidate['name']}_{candidate['email']}"
                        st.session_state.shortlisted_candidates = [
                            c for c in st.session_state.shortlisted_candidates 
                            if f"{c['name']}_{c['email']}" != candidate_id
                        ]
                        st.success(f"✅ {candidate['name']} removed from shortlist!")
                        st.rerun()
                    
                    # Status indicator
                    if candidate['match_score'] >= 70:
                        st.success("🌟 Highly Recommended")
                    elif candidate['match_score'] >= 50:
                        st.info("👍 Good Candidate")
                    else:
                        st.warning("⚠️ Needs Review")
    
    else:
        # Empty state
        st.info("📝 No candidates shortlisted yet!")
        st.markdown("""
        ### 💡 How to Add Candidates to Shortlist:
        
        1. Go to the **🏢 Recruiter Dashboard** tab
        2. Upload job description and multiple resumes
        3. Process the resumes to get match scores
        4. Click the **📧 Shortlist** button for candidates you're interested in
        5. Return here to manage your shortlisted candidates
        
        ### ✨ Shortlist Features:
        - **Export to CSV** - Download complete candidate data
        - **Export Email List** - Get all candidate emails for bulk communication
        - **Filter & Sort** - Organize candidates by position or score
        - **Individual Actions** - Contact info and remove options
        - **Match Analysis** - See skills and reasoning for each candidate
        """)

# ============================
# 📊 TAB 5: Prediction History
# ============================
with tab5:
    st.markdown("### 📊 Prediction History & Analytics")
    st.markdown("Comprehensive analysis of all resume predictions and system usage")

    # Initialize session state for refresh trigger
    if 'refresh_trigger' not in st.session_state:
        st.session_state.refresh_trigger = 0

    @st.cache_data
    def fetch_predictions(refresh_trigger):
        return supabase.table("resumes").select("*").order("id", desc=True).execute().data

    # Add refresh controls
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.session_state.refresh_trigger += 1
            st.rerun()

    data = fetch_predictions(st.session_state.refresh_trigger)

    if data:
        df = pd.DataFrame(data)

        # Ensure required columns exist
        required_cols = ["filename", "predicted_label", "user_email", "created_at"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = "Not Available"

        # Convert created_at to datetime for better filtering
        if 'created_at' in df.columns:
            try:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['date'] = df['created_at'].dt.date
                df['time'] = df['created_at'].dt.time
            except:
                df['date'] = "Not Available"
                df['time'] = "Not Available"

        # ============================
        # 📈 ANALYTICS DASHBOARD
        # ============================
        st.markdown("## 📈 Analytics Dashboard")
        
        # Summary Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Predictions", len(df))
        
        with col2:
            unique_roles = df['predicted_label'].nunique()
            st.metric("🎯 Unique Job Roles", unique_roles)
        
        with col3:
            unique_users = df['user_email'].nunique()
            st.metric("👥 Unique Users", unique_users)
        
        with col4:
            if 'created_at' in df.columns and df['created_at'].notna().any():
                try:
                    days_active = (df['created_at'].max() - df['created_at'].min()).days + 1
                    st.metric("📅 Days Active", days_active)
                except:
                    st.metric("📅 Days Active", "N/A")
            else:
                st.metric("📅 Days Active", "N/A")

        # Charts Section
        st.markdown("### 📊 Visual Analytics")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Role Distribution Chart
            st.markdown("#### 🎯 Job Role Distribution")
            role_counts = df['predicted_label'].value_counts()
            
            if len(role_counts) > 0:
                # Create a simple bar chart using Streamlit
                chart_data = pd.DataFrame({
                    'Role': role_counts.index,
                    'Count': role_counts.values
                })
                st.bar_chart(chart_data.set_index('Role'))
                
                # Show top roles
                st.write("**Top Predicted Roles:**")
                for i, (role, count) in enumerate(role_counts.head(5).items(), 1):
                    percentage = (count / len(df)) * 100
                    st.write(f"{i}. **{role}**: {count} predictions ({percentage:.1f}%)")
            else:
                st.info("No role data available for chart")
        
        with chart_col2:
            # Daily Activity Chart
            st.markdown("#### 📅 Daily Activity")
            if 'date' in df.columns and df['date'].notna().any():
                try:
                    daily_counts = df['date'].value_counts().sort_index()
                    
                    if len(daily_counts) > 0:
                        chart_data = pd.DataFrame({
                            'Date': daily_counts.index,
                            'Predictions': daily_counts.values
                        })
                        st.line_chart(chart_data.set_index('Date'))
                        
                        # Show recent activity
                        st.write("**Recent Activity:**")
                        for date, count in daily_counts.tail(5).items():
                            st.write(f"• **{date}**: {count} predictions")
                    else:
                        st.info("No daily activity data available")
                except:
                    st.info("Unable to process date data for chart")
            else:
                st.info("No date information available for activity chart")

        # ============================
        # 🔍 ADVANCED FILTERING
        # ============================
        st.markdown("## 🔍 Advanced Filtering & Search")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Role Filter
            all_roles = ["All Roles"] + sorted(df['predicted_label'].unique().tolist())
            selected_role = st.selectbox("🎯 Filter by Job Role", all_roles)
        
        with filter_col2:
            # User Filter
            all_users = ["All Users"] + sorted(df['user_email'].unique().tolist())
            selected_user = st.selectbox("👤 Filter by User", all_users)
        
        with filter_col3:
            # Date Range Filter
            if 'created_at' in df.columns and df['created_at'].notna().any():
                try:
                    min_date = df['created_at'].min().date()
                    max_date = df['created_at'].max().date()
                    
                    date_range = st.date_input(
                        "📅 Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                except:
                    date_range = None
            else:
                st.info("No date filtering available")
                date_range = None

        # Search Box
        search_term = st.text_input("🔍 Search in filenames", placeholder="Enter filename or keyword...")

        # Apply Filters
        filtered_df = df.copy()
        
        # Role filter
        if selected_role != "All Roles":
            filtered_df = filtered_df[filtered_df['predicted_label'] == selected_role]
        
        # User filter
        if selected_user != "All Users":
            filtered_df = filtered_df[filtered_df['user_email'] == selected_user]
        
        # Date filter
        if date_range and len(date_range) == 2 and 'created_at' in filtered_df.columns:
            try:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['created_at'].dt.date >= start_date) & 
                    (filtered_df['created_at'].dt.date <= end_date)
                ]
            except:
                pass
        
        # Search filter
        if search_term:
            filtered_df = filtered_df[
                filtered_df['filename'].str.contains(search_term, case=False, na=False)
            ]

        # ============================
        # 📥 EXPORT OPTIONS
        # ============================
        st.markdown("## 📥 Export Options")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            # Export filtered data
            if len(filtered_df) > 0:
                export_df = filtered_df[required_cols].copy()
                export_df.rename(columns={
                    "filename": "Filename",
                    "predicted_label": "Predicted_Role",
                    "user_email": "User_Email",
                    "created_at": "Upload_DateTime"
                }, inplace=True)
                
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    label="📊 Export Filtered Data (CSV)",
                    data=csv_data,
                    file_name=f"prediction_history_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with export_col2:
            # Export analytics summary
            if len(df) > 0:
                analytics_data = {
                    'Metric': [
                        'Total Predictions',
                        'Unique Job Roles', 
                        'Unique Users',
                        'Most Common Role',
                        'Most Active User'
                    ],
                    'Value': [
                        len(df),
                        df['predicted_label'].nunique(),
                        df['user_email'].nunique(),
                        df['predicted_label'].mode().iloc[0] if len(df['predicted_label'].mode()) > 0 else 'N/A',
                        df['user_email'].mode().iloc[0] if len(df['user_email'].mode()) > 0 else 'N/A'
                    ]
                }
                
                analytics_df = pd.DataFrame(analytics_data)
                analytics_csv = analytics_df.to_csv(index=False)
                
                st.download_button(
                    label="📈 Export Analytics Summary",
                    data=analytics_csv,
                    file_name=f"analytics_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with export_col3:
            # Export role distribution
            if len(df) > 0:
                role_dist = df['predicted_label'].value_counts().reset_index()
                role_dist.columns = ['Job_Role', 'Count']
                role_dist['Percentage'] = (role_dist['Count'] / len(df) * 100).round(2)
                
                role_csv = role_dist.to_csv(index=False)
                st.download_button(
                    label="🎯 Export Role Distribution",
                    data=role_csv,
                    file_name=f"role_distribution_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        # ============================
        # 📋 ENHANCED DATA TABLE
        # ============================
        st.markdown("## 📋 Detailed Prediction Records")
        st.write(f"**Showing {len(filtered_df)} of {len(df)} records**")
        
        if len(filtered_df) > 0:
            # Prepare display dataframe
            display_df = filtered_df[required_cols].copy()
            
            # Format datetime for better display
            if 'created_at' in display_df.columns:
                try:
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            display_df.rename(columns={
                "filename": "📎 Filename",
                "predicted_label": "🔖 Predicted Role",
                "user_email": "👤 Uploaded By",
                "created_at": "🕒 Uploaded At"
            }, inplace=True)

            # Display with pagination
            page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=1)
            
            total_pages = (len(display_df) - 1) // page_size + 1
            
            if total_pages > 1:
                page_num = st.selectbox(f"Page (1 to {total_pages})", range(1, total_pages + 1))
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                page_df = display_df.iloc[start_idx:end_idx]
            else:
                page_df = display_df
            
            st.dataframe(page_df, use_container_width=True)
            
            # Quick Stats for filtered data
            if len(filtered_df) != len(df):
                st.markdown("### 📊 Filtered Data Statistics")
                filt_col1, filt_col2, filt_col3 = st.columns(3)
                
                with filt_col1:
                    st.metric("Filtered Records", len(filtered_df))
                
                with filt_col2:
                    if len(filtered_df) > 0:
                        top_role = filtered_df['predicted_label'].mode().iloc[0] if len(filtered_df['predicted_label'].mode()) > 0 else 'N/A'
                        st.metric("Top Role in Filter", top_role)
                
                with filt_col3:
                    if len(filtered_df) > 0:
                        unique_users_filtered = filtered_df['user_email'].nunique()
                        st.metric("Users in Filter", unique_users_filtered)
        
        else:
            st.info("No records match your current filters. Try adjusting the filter criteria.")

    else:
        st.info("No predictions found in the database.")
        st.markdown("### 💡 How to Get Started")
        st.write("1. Go to the **📄 Resume Classifier** tab")
        st.write("2. Upload a resume to get predictions")
        st.write("3. Return here to see analytics and history")
