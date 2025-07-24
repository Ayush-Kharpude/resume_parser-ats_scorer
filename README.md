# 🧠 Smart Resume Analyzer

A comprehensive AI-powered ATS (Applicant Tracking System) built with Streamlit that helps both job seekers and recruiters optimize the hiring process.

![Smart Resume Analyzer](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge)

## ✨ Features

### 📄 For Job Seekers
- **Resume Classification** - Instant job role prediction
- **ATS Score Analysis** - Get match scores against job descriptions
- **Skill Gap Analysis** - Identify missing skills for target roles
- **AI-Powered Suggestions** - Personalized resume improvement recommendations
- **Domain-Aware Matching** - Smart cross-field compatibility detection

### 🏢 For Recruiters
- **Batch Resume Processing** - Upload and analyze multiple resumes simultaneously
- **Advanced Filtering** - Sort candidates by score, skills, and other criteria
- **Candidate Shortlisting** - Manage and export shortlisted candidates
- **Analytics Dashboard** - Comprehensive hiring insights and trends
- **Export Capabilities** - Download results in CSV format

### 📊 Analytics & History
- **Prediction History** - Track all resume analyses with advanced filtering
- **Visual Analytics** - Charts showing role distribution and daily activity
- **Export Options** - Multiple export formats for data analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-resume-analyzer.git
   cd smart-resume-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv ats-env
   source ats-env/bin/activate  # On Windows: ats-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file and add your Supabase credentials
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

5. **Run the application**
   ```bash
   streamlit run app/app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS/HTML
- **Backend**: Python with FastAPI (optional)
- **AI/ML**: Sentence Transformers, Scikit-learn
- **Database**: Supabase (PostgreSQL)
- **PDF Processing**: PyMuPDF, pdfplumber
- **Data Analysis**: Pandas, NumPy

## 📁 Project Structure

```
ats/
├── app/
│   └── app.py              # Main Streamlit application
├── backend/
│   ├── matcher.py          # Resume-job matching logic
│   ├── resume_parser.py    # Resume data extraction
│   └── job_parser.py       # Job description processing
├── utils/
│   ├── gemini_helper.py    # AI suggestions and skill analysis
│   └── supabase_client.py  # Database connection
├── auth/
│   └── auth_handler.py     # Authentication logic
├── models/
│   └── model.py            # ML model loading
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🎯 Key Features Explained

### Smart Matching Algorithm
- Uses sentence transformers for semantic similarity
- Domain-aware penalties for cross-field mismatches
- Skill-based compatibility scoring

### Comprehensive Skill Analysis
- 100+ skills across 5 major domains (Tech, Business, Finance, HR, Design)
- Intelligent fallback for general requirements
- Personalized skill gap identification

### Advanced Analytics
- Real-time dashboard with visual charts
- Historical trend analysis
- Export capabilities for further analysis

## 🔧 Configuration

### Database Setup
1. Create a Supabase project
2. Create a `resumes` table with columns:
   - `id` (primary key)
   - `filename` (text)
   - `predicted_label` (text)
   - `original_text` (text)
   - `user_email` (text)
   - `created_at` (timestamp)

### Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

## 📊 Usage Examples

### Individual Resume Analysis
1. Go to "ATS Score Generator" tab
2. Upload your resume (PDF)
3. Upload job description (PDF/TXT)
4. Get instant match score and recommendations

### Bulk Candidate Screening
1. Go to "Recruiter Dashboard" tab
2. Enter job requirements
3. Upload multiple resumes
4. Review, filter, and shortlist candidates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Hugging Face for sentence transformers
- Supabase for the database infrastructure
- All contributors and users of this project

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the documentation
- Contact the maintainers

---

**Made with ❤️ for better hiring experiences**
