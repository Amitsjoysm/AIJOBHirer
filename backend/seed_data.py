"""
Seed data script for HireFlow AI
Creates comprehensive test data for production readiness testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from pathlib import Path
from passlib.context import CryptContext
import uuid

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_id() -> str:
    return str(uuid.uuid4())

async def clear_existing_data():
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    await db.users.delete_many({})
    await db.companies.delete_many({})
    await db.jobs.delete_many({})
    await db.applications.delete_many({})
    await db.candidates.delete_many({})
    await db.interviews.delete_many({})
    await db.email_configs.delete_many({})
    print("✅ Existing data cleared")

async def seed_users():
    """Create test users"""
    print("\n👤 Creating users...")
    
    users = [
        {
            "id": "user-1",
            "email": "admin@techcorp.com",
            "full_name": "Alice Johnson",
            "role": "admin",
            "hashed_password": hash_password("password123"),
            "auth_provider": "jwt",
            "oauth_connected": False,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "user-2",
            "email": "hr@innovateai.com",
            "full_name": "Bob Smith",
            "role": "hiring_manager",
            "hashed_password": hash_password("password123"),
            "auth_provider": "jwt",
            "oauth_connected": False,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "user-3",
            "email": "recruiter@greenventures.com",
            "full_name": "Carol Davis",
            "role": "recruiter",
            "hashed_password": hash_password("password123"),
            "auth_provider": "jwt",
            "oauth_connected": False,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.users.insert_many(users)
    print(f"✅ Created {len(users)} users")
    print("   📧 admin@techcorp.com / password123")
    print("   📧 hr@innovateai.com / password123")
    print("   📧 recruiter@greenventures.com / password123")
    return users

async def seed_companies(users):
    """Create test companies"""
    print("\n🏢 Creating companies...")
    
    companies = [
        {
            "id": "company-1",
            "name": "TechCorp Solutions",
            "slug": "techcorp",
            "user_id": users[0]['id'],
            "industry": "Technology",
            "website": "https://techcorp.example.com",
            "description": "Leading provider of enterprise software solutions",
            "persona": {
                "company_mission": "Empowering businesses through innovative technology",
                "company_values": ["Innovation", "Excellence", "Collaboration", "Integrity"],
                "company_culture": "Fast-paced, collaborative, and innovation-driven environment",
                "hiring_style": "We value technical excellence and cultural fit",
                "tone": "professional"
            },
            "branding": {
                "logo_url": "https://via.placeholder.com/200x200/3B82F6/ffffff?text=TechCorp",
                "primary_color": "#3B82F6",
                "secondary_color": "#10B981",
                "header_image_url": "https://via.placeholder.com/1200x400/3B82F6/ffffff?text=TechCorp+Header",
                "about_us": "We are a leading technology company focused on delivering exceptional software solutions."
            },
            "auto_reject_after_hours": 48,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "company-2",
            "name": "InnovateAI",
            "slug": "innovateai",
            "user_id": users[1]['id'],
            "industry": "Artificial Intelligence",
            "website": "https://innovateai.example.com",
            "description": "Pioneering AI solutions for modern businesses",
            "persona": {
                "company_mission": "Making AI accessible to everyone",
                "company_values": ["Innovation", "Transparency", "Impact", "Learning"],
                "company_culture": "Research-driven, collaborative, and cutting-edge",
                "hiring_style": "We seek brilliant minds passionate about AI",
                "tone": "friendly"
            },
            "branding": {
                "logo_url": "https://via.placeholder.com/200x200/8B5CF6/ffffff?text=InnovateAI",
                "primary_color": "#8B5CF6",
                "secondary_color": "#EC4899",
                "header_image_url": "https://via.placeholder.com/1200x400/8B5CF6/ffffff?text=InnovateAI+Header",
                "about_us": "We're building the future of AI-powered applications."
            },
            "auto_reject_after_hours": 72,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "company-3",
            "name": "Green Ventures",
            "slug": "greenventures",
            "user_id": users[2]['id'],
            "industry": "Sustainability",
            "website": "https://greenventures.example.com",
            "description": "Creating sustainable solutions for a better planet",
            "persona": {
                "company_mission": "Building a sustainable future through innovation",
                "company_values": ["Sustainability", "Innovation", "Community", "Impact"],
                "company_culture": "Purpose-driven, collaborative, and eco-conscious",
                "hiring_style": "We value passion for sustainability and innovative thinking",
                "tone": "casual"
            },
            "branding": {
                "logo_url": "https://via.placeholder.com/200x200/10B981/ffffff?text=Green",
                "primary_color": "#10B981",
                "secondary_color": "#14B8A6",
                "header_image_url": "https://via.placeholder.com/1200x400/10B981/ffffff?text=Green+Ventures",
                "about_us": "Join us in making the world a greener place."
            },
            "auto_reject_after_hours": 48,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.companies.insert_many(companies)
    print(f"✅ Created {len(companies)} companies")
    return companies

async def seed_jobs(companies):
    """Create test jobs"""
    print("\n💼 Creating jobs...")
    
    jobs = [
        # TechCorp Jobs
        {
            "id": "job-1",
            "company_id": companies[0]['id'],
            "created_by": companies[0]['user_id'],
            "title": "Senior Full-Stack Developer",
            "department": "Engineering",
            "description": "We're seeking an experienced Full-Stack Developer to join our dynamic team...",
            "requirements": [
                "5+ years of experience with React and Node.js",
                "Strong knowledge of TypeScript and modern JavaScript",
                "Experience with MongoDB and relational databases",
                "Excellent problem-solving skills",
                "Strong communication and teamwork abilities"
            ],
            "nice_to_have": [
                "Experience with AWS or GCP",
                "Knowledge of Docker and Kubernetes",
                "Contributions to open-source projects"
            ],
            "job_type": "full_time",
            "location_type": "remote",
            "location": "United States",
            "experience_level": "senior",
            "salary_min": 120000,
            "salary_max": 180000,
            "salary_currency": "USD",
            "status": "active",
            "screening_questions": [
                {
                    "question": "How many years of experience do you have with React?",
                    "question_type": "text",
                    "required": True,
                    "weight": 1.5
                },
                {
                    "question": "Describe a complex technical challenge you solved recently.",
                    "question_type": "text",
                    "required": True,
                    "weight": 2.0
                },
                {
                    "question": "Are you authorized to work in the United States?",
                    "question_type": "yes_no",
                    "required": True,
                    "weight": 1.0
                }
            ],
            "ai_generated": False,
            "view_count": 245,
            "application_count": 0,
            "created_at": datetime.now(timezone.utc) - timedelta(days=10),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc) - timedelta(days=10)
        },
        {
            "id": "job-2",
            "company_id": companies[0]['id'],
            "created_by": companies[0]['user_id'],
            "title": "DevOps Engineer",
            "department": "Infrastructure",
            "description": "Join our infrastructure team to build and maintain scalable cloud systems...",
            "requirements": [
                "3+ years of DevOps experience",
                "Strong knowledge of AWS, Docker, and Kubernetes",
                "Experience with CI/CD pipelines",
                "Proficiency in scripting (Python, Bash)",
                "Understanding of security best practices"
            ],
            "nice_to_have": [
                "Terraform or CloudFormation experience",
                "Monitoring tools experience (Prometheus, Grafana)",
                "Experience with service mesh (Istio, Linkerd)"
            ],
            "job_type": "full_time",
            "location_type": "hybrid",
            "location": "San Francisco, CA",
            "experience_level": "intermediate",
            "salary_min": 100000,
            "salary_max": 150000,
            "salary_currency": "USD",
            "status": "active",
            "screening_questions": [
                {
                    "question": "Describe your experience with Kubernetes.",
                    "question_type": "text",
                    "required": True,
                    "weight": 2.0
                },
                {
                    "question": "What CI/CD tools have you worked with?",
                    "question_type": "text",
                    "required": True,
                    "weight": 1.5
                }
            ],
            "ai_generated": False,
            "view_count": 180,
            "application_count": 0,
            "created_at": datetime.now(timezone.utc) - timedelta(days=7),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc) - timedelta(days=7)
        },
        # InnovateAI Jobs
        {
            "id": "job-3",
            "company_id": companies[1]['id'],
            "created_by": companies[1]['user_id'],
            "title": "AI/ML Engineer",
            "department": "Research",
            "description": "Looking for a passionate AI/ML engineer to work on cutting-edge projects...",
            "requirements": [
                "Strong background in machine learning and deep learning",
                "Experience with PyTorch or TensorFlow",
                "Knowledge of NLP and computer vision",
                "Python programming expertise",
                "MS or PhD in Computer Science or related field"
            ],
            "nice_to_have": [
                "Published research papers",
                "Experience with LLMs (GPT, BERT, etc.)",
                "Knowledge of MLOps practices"
            ],
            "job_type": "full_time",
            "location_type": "remote",
            "location": "Global",
            "experience_level": "senior",
            "salary_min": 140000,
            "salary_max": 200000,
            "salary_currency": "USD",
            "status": "active",
            "screening_questions": [
                {
                    "question": "Describe your experience with large language models.",
                    "question_type": "text",
                    "required": True,
                    "weight": 2.0
                },
                {
                    "question": "Share links to your research papers or GitHub repos.",
                    "question_type": "text",
                    "required": False,
                    "weight": 1.0
                }
            ],
            "ai_generated": True,
            "view_count": 320,
            "application_count": 0,
            "created_at": datetime.now(timezone.utc) - timedelta(days=5),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc) - timedelta(days=5)
        },
        {
            "id": "job-4",
            "company_id": companies[1]['id'],
            "created_by": companies[1]['user_id'],
            "title": "Product Manager - AI Products",
            "department": "Product",
            "description": "Lead the development of innovative AI-powered products...",
            "requirements": [
                "5+ years of product management experience",
                "Understanding of AI/ML technologies",
                "Strong analytical and strategic thinking",
                "Excellent communication skills",
                "Experience with agile methodologies"
            ],
            "nice_to_have": [
                "Technical background in ML",
                "Experience with B2B SaaS products",
                "MBA or equivalent"
            ],
            "job_type": "full_time",
            "location_type": "hybrid",
            "location": "New York, NY",
            "experience_level": "senior",
            "salary_min": 130000,
            "salary_max": 170000,
            "salary_currency": "USD",
            "status": "active",
            "screening_questions": [
                {
                    "question": "Describe your experience managing AI/ML products.",
                    "question_type": "text",
                    "required": True,
                    "weight": 2.0
                }
            ],
            "ai_generated": False,
            "view_count": 195,
            "application_count": 0,
            "created_at": datetime.now(timezone.utc) - timedelta(days=12),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc) - timedelta(days=12)
        },
        # Green Ventures Jobs
        {
            "id": "job-5",
            "company_id": companies[2]['id'],
            "created_by": companies[2]['user_id'],
            "title": "Sustainability Analyst",
            "department": "Sustainability",
            "description": "Help us measure and improve our environmental impact...",
            "requirements": [
                "2+ years in sustainability or environmental analysis",
                "Knowledge of sustainability metrics and reporting",
                "Data analysis skills",
                "Bachelor's degree in Environmental Science or related field",
                "Passion for sustainability"
            ],
            "nice_to_have": [
                "Certification in sustainability (LEED, etc.)",
                "Experience with carbon accounting software",
                "Project management experience"
            ],
            "job_type": "full_time",
            "location_type": "remote",
            "location": "United States",
            "experience_level": "intermediate",
            "salary_min": 70000,
            "salary_max": 95000,
            "salary_currency": "USD",
            "status": "active",
            "screening_questions": [
                {
                    "question": "What sustainability frameworks are you familiar with?",
                    "question_type": "text",
                    "required": True,
                    "weight": 1.5
                }
            ],
            "ai_generated": False,
            "view_count": 130,
            "application_count": 0,
            "created_at": datetime.now(timezone.utc) - timedelta(days=3),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc) - timedelta(days=3)
        }
    ]
    
    await db.jobs.insert_many(jobs)
    print(f"✅ Created {len(jobs)} jobs")
    return jobs

async def seed_candidates():
    """Create test candidates"""
    print("\n👨‍💼 Creating candidates...")
    
    candidates = [
        {
            "id": "candidate-1",
            "email": "john.doe@email.com",
            "full_name": "John Doe",
            "phone": "+1-555-0101",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "parsed_resume": {
                "work_experience": [
                    {
                        "company": "Tech Innovations Inc",
                        "title": "Senior Software Engineer",
                        "start_date": "2019-01",
                        "end_date": "2024-12",
                        "is_current": True,
                        "description": "Led development of microservices architecture"
                    },
                    {
                        "company": "StartupXYZ",
                        "title": "Full-Stack Developer",
                        "start_date": "2016-06",
                        "end_date": "2018-12",
                        "is_current": False,
                        "description": "Built web applications using React and Node.js"
                    }
                ],
                "education": [
                    {
                        "institution": "Stanford University",
                        "degree": "Master of Science",
                        "field_of_study": "Computer Science",
                        "graduation_year": 2016
                    },
                    {
                        "institution": "UC Berkeley",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Science",
                        "graduation_year": 2014
                    }
                ],
                "skills": [
                    "React", "Node.js", "TypeScript", "Python", "AWS",
                    "MongoDB", "PostgreSQL", "Docker", "Kubernetes"
                ],
                "certifications": [
                    "AWS Certified Solutions Architect",
                    "Google Cloud Professional"
                ],
                "summary": "Experienced software engineer with 8+ years of full-stack development"
            },
            "resume_urls": ["https://example.com/resumes/john-doe.pdf"],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc) - timedelta(days=5),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "candidate-2",
            "email": "jane.smith@email.com",
            "full_name": "Jane Smith",
            "phone": "+1-555-0102",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "parsed_resume": {
                "work_experience": [
                    {
                        "company": "DevOps Solutions",
                        "title": "DevOps Lead",
                        "start_date": "2020-03",
                        "end_date": None,
                        "is_current": True,
                        "description": "Managing cloud infrastructure and CI/CD pipelines"
                    }
                ],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Engineering",
                        "graduation_year": 2019
                    }
                ],
                "skills": [
                    "Kubernetes", "Docker", "AWS", "Terraform",
                    "Jenkins", "Python", "Bash", "Prometheus"
                ],
                "certifications": [
                    "Kubernetes Administrator (CKA)",
                    "AWS DevOps Engineer"
                ],
                "summary": "DevOps engineer with 4+ years of cloud infrastructure experience"
            },
            "resume_urls": ["https://example.com/resumes/jane-smith.pdf"],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc) - timedelta(days=4),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "candidate-3",
            "email": "alex.chen@email.com",
            "full_name": "Alex Chen",
            "phone": "+1-555-0103",
            "linkedin_url": "https://linkedin.com/in/alexchen",
            "parsed_resume": {
                "work_experience": [
                    {
                        "company": "AI Research Lab",
                        "title": "Machine Learning Engineer",
                        "start_date": "2021-01",
                        "end_date": None,
                        "is_current": True,
                        "description": "Developing NLP models and working with LLMs"
                    },
                    {
                        "company": "Data Science Corp",
                        "title": "Data Scientist",
                        "start_date": "2018-06",
                        "end_date": "2020-12",
                        "is_current": False,
                        "description": "Built predictive models for business analytics"
                    }
                ],
                "education": [
                    {
                        "institution": "Carnegie Mellon University",
                        "degree": "PhD",
                        "field_of_study": "Machine Learning",
                        "graduation_year": 2021
                    }
                ],
                "skills": [
                    "PyTorch", "TensorFlow", "Python", "NLP",
                    "Computer Vision", "MLOps", "LLMs", "BERT", "GPT"
                ],
                "certifications": [
                    "Deep Learning Specialization",
                    "TensorFlow Developer"
                ],
                "summary": "ML engineer with PhD and 6+ years of AI/ML experience"
            },
            "resume_urls": ["https://example.com/resumes/alex-chen.pdf"],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc) - timedelta(days=3),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "candidate-4",
            "email": "sarah.wilson@email.com",
            "full_name": "Sarah Wilson",
            "phone": "+1-555-0104",
            "linkedin_url": "https://linkedin.com/in/sarahwilson",
            "parsed_resume": {
                "work_experience": [
                    {
                        "company": "Product Innovations",
                        "title": "Senior Product Manager",
                        "start_date": "2018-04",
                        "end_date": None,
                        "is_current": True,
                        "description": "Leading AI product development"
                    }
                ],
                "education": [
                    {
                        "institution": "Harvard Business School",
                        "degree": "MBA",
                        "field_of_study": "Business Administration",
                        "graduation_year": 2018
                    }
                ],
                "skills": [
                    "Product Management", "Agile", "AI/ML Products",
                    "Data Analytics", "Strategic Planning", "Stakeholder Management"
                ],
                "certifications": [
                    "Certified Scrum Product Owner",
                    "Product Management Certificate"
                ],
                "summary": "Product manager with 6+ years experience in AI products"
            },
            "resume_urls": ["https://example.com/resumes/sarah-wilson.pdf"],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc) - timedelta(days=2),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "candidate-5",
            "email": "mike.brown@email.com",
            "full_name": "Mike Brown",
            "phone": "+1-555-0105",
            "linkedin_url": "https://linkedin.com/in/mikebrown",
            "parsed_resume": {
                "work_experience": [
                    {
                        "company": "EcoConsulting",
                        "title": "Sustainability Consultant",
                        "start_date": "2020-01",
                        "end_date": None,
                        "is_current": True,
                        "description": "Advising companies on sustainability practices"
                    }
                ],
                "education": [
                    {
                        "institution": "Yale University",
                        "degree": "Master of Environmental Management",
                        "field_of_study": "Environmental Science",
                        "graduation_year": 2019
                    }
                ],
                "skills": [
                    "Sustainability Analysis", "Carbon Accounting",
                    "Environmental Reporting", "Data Analysis", "Excel", "Python"
                ],
                "certifications": [
                    "LEED Green Associate",
                    "Carbon Accounting Certification"
                ],
                "summary": "Sustainability analyst with 4+ years of environmental consulting"
            },
            "resume_urls": ["https://example.com/resumes/mike-brown.pdf"],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc) - timedelta(days=1),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.candidates.insert_many(candidates)
    print(f"✅ Created {len(candidates)} candidates")
    return candidates

async def seed_applications(jobs, candidates):
    """Create test applications"""
    print("\n📄 Creating applications...")
    
    applications = [
        # Applications for Job 1 (Senior Full-Stack Developer)
        {
            "id": "app-1",
            "job_id": jobs[0]['id'],
            "candidate_id": candidates[0]['id'],
            "candidate_email": candidates[0]['email'],
            "candidate_name": candidates[0]['full_name'],
            "candidate_phone": candidates[0]['phone'],
            "candidate_linkedin": candidates[0]['linkedin_url'],
            "resume_url": candidates[0]['resume_urls'][0],
            "questionnaire_answers": [
                {
                    "question": "How many years of experience do you have with React?",
                    "answer": "I have 6 years of experience with React, working on large-scale applications.",
                    "score": 9.5
                },
                {
                    "question": "Describe a complex technical challenge you solved recently.",
                    "answer": "I architected a microservices migration for a monolithic app serving 10M+ users...",
                    "score": 9.0
                },
                {
                    "question": "Are you authorized to work in the United States?",
                    "answer": "Yes",
                    "score": 10.0
                }
            ],
            "status": "shortlisted",
            "ai_evaluation": {
                "overall_score": 92.0,
                "score_breakdown": {
                    "skills_match": 95.0,
                    "experience_relevance": 90.0,
                    "education_fit": 95.0,
                    "career_trajectory": 90.0,
                    "questionnaire_score": 95.0
                },
                "summary": "Excellent candidate with strong full-stack experience and relevant skills.",
                "strengths": [
                    "8+ years of relevant experience",
                    "Strong React and Node.js skills",
                    "AWS certifications",
                    "Leadership experience"
                ],
                "concerns": [],
                "recommendation": "strong_match"
            },
            "notes": [],
            "tags": ["strong_candidate", "full_stack"],
            "created_at": datetime.now(timezone.utc) - timedelta(days=5),
            "updated_at": datetime.now(timezone.utc) - timedelta(days=2),
            "reviewed_at": datetime.now(timezone.utc) - timedelta(days=2)
        },
        # Applications for Job 2 (DevOps Engineer)
        {
            "id": "app-2",
            "job_id": jobs[1]['id'],
            "candidate_id": candidates[1]['id'],
            "candidate_email": candidates[1]['email'],
            "candidate_name": candidates[1]['full_name'],
            "candidate_phone": candidates[1]['phone'],
            "candidate_linkedin": candidates[1]['linkedin_url'],
            "resume_url": candidates[1]['resume_urls'][0],
            "questionnaire_answers": [
                {
                    "question": "Describe your experience with Kubernetes.",
                    "answer": "4 years managing K8s clusters, including multi-region deployments...",
                    "score": 9.0
                },
                {
                    "question": "What CI/CD tools have you worked with?",
                    "answer": "Jenkins, GitLab CI, GitHub Actions, ArgoCD",
                    "score": 8.5
                }
            ],
            "status": "interview_scheduled",
            "ai_evaluation": {
                "overall_score": 88.0,
                "score_breakdown": {
                    "skills_match": 90.0,
                    "experience_relevance": 85.0,
                    "education_fit": 85.0,
                    "career_trajectory": 90.0,
                    "questionnaire_score": 90.0
                },
                "summary": "Strong DevOps candidate with excellent Kubernetes experience.",
                "strengths": [
                    "4+ years DevOps experience",
                    "Strong K8s skills",
                    "CKA certification",
                    "Current role as DevOps Lead"
                ],
                "concerns": [
                    "Limited experience with Terraform"
                ],
                "recommendation": "strong_match"
            },
            "notes": [],
            "tags": ["kubernetes_expert", "aws"],
            "created_at": datetime.now(timezone.utc) - timedelta(days=4),
            "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
            "reviewed_at": datetime.now(timezone.utc) - timedelta(days=1)
        },
        # Applications for Job 3 (AI/ML Engineer)
        {
            "id": "app-3",
            "job_id": jobs[2]['id'],
            "candidate_id": candidates[2]['id'],
            "candidate_email": candidates[2]['email'],
            "candidate_name": candidates[2]['full_name'],
            "candidate_phone": candidates[2]['phone'],
            "candidate_linkedin": candidates[2]['linkedin_url'],
            "resume_url": candidates[2]['resume_urls'][0],
            "questionnaire_answers": [
                {
                    "question": "Describe your experience with large language models.",
                    "answer": "PhD research focused on LLMs, implemented custom transformers, fine-tuned GPT models...",
                    "score": 10.0
                },
                {
                    "question": "Share links to your research papers or GitHub repos.",
                    "answer": "github.com/alexchen, 5 published papers on NLP",
                    "score": 10.0
                }
            ],
            "status": "shortlisted",
            "ai_evaluation": {
                "overall_score": 96.0,
                "score_breakdown": {
                    "skills_match": 98.0,
                    "experience_relevance": 95.0,
                    "education_fit": 100.0,
                    "career_trajectory": 90.0,
                    "questionnaire_score": 100.0
                },
                "summary": "Outstanding candidate with PhD and deep expertise in LLMs.",
                "strengths": [
                    "PhD in Machine Learning",
                    "6+ years AI/ML experience",
                    "Published research papers",
                    "Deep LLM expertise"
                ],
                "concerns": [],
                "recommendation": "strong_match"
            },
            "notes": [],
            "tags": ["phd", "llm_expert", "research"],
            "created_at": datetime.now(timezone.utc) - timedelta(days=3),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=12),
            "reviewed_at": datetime.now(timezone.utc) - timedelta(hours=12)
        },
        # Applications for Job 4 (Product Manager)
        {
            "id": "app-4",
            "job_id": jobs[3]['id'],
            "candidate_id": candidates[3]['id'],
            "candidate_email": candidates[3]['email'],
            "candidate_name": candidates[3]['full_name'],
            "candidate_phone": candidates[3]['phone'],
            "candidate_linkedin": candidates[3]['linkedin_url'],
            "resume_url": candidates[3]['resume_urls'][0],
            "questionnaire_answers": [
                {
                    "question": "Describe your experience managing AI/ML products.",
                    "answer": "6 years managing AI products from 0 to 1, including NLP and computer vision products...",
                    "score": 9.5
                }
            ],
            "status": "submitted",
            "ai_evaluation": {
                "overall_score": 85.0,
                "score_breakdown": {
                    "skills_match": 85.0,
                    "experience_relevance": 90.0,
                    "education_fit": 90.0,
                    "career_trajectory": 80.0,
                    "questionnaire_score": 95.0
                },
                "summary": "Strong product management candidate with AI product experience.",
                "strengths": [
                    "6+ years PM experience",
                    "MBA from Harvard",
                    "AI product expertise",
                    "Strategic thinking"
                ],
                "concerns": [
                    "Limited technical background in ML"
                ],
                "recommendation": "consider"
            },
            "notes": [],
            "tags": ["product_management", "ai_products"],
            "created_at": datetime.now(timezone.utc) - timedelta(days=2),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=6),
            "reviewed_at": datetime.now(timezone.utc) - timedelta(hours=6)
        },
        # Applications for Job 5 (Sustainability Analyst)
        {
            "id": "app-5",
            "job_id": jobs[4]['id'],
            "candidate_id": candidates[4]['id'],
            "candidate_email": candidates[4]['email'],
            "candidate_name": candidates[4]['full_name'],
            "candidate_phone": candidates[4]['phone'],
            "candidate_linkedin": candidates[4]['linkedin_url'],
            "resume_url": candidates[4]['resume_urls'][0],
            "questionnaire_answers": [
                {
                    "question": "What sustainability frameworks are you familiar with?",
                    "answer": "GRI, SASB, TCFD, CDP reporting frameworks. LEED certified.",
                    "score": 9.0
                }
            ],
            "status": "submitted",
            "ai_evaluation": {
                "overall_score": 82.0,
                "score_breakdown": {
                    "skills_match": 85.0,
                    "experience_relevance": 80.0,
                    "education_fit": 90.0,
                    "career_trajectory": 75.0,
                    "questionnaire_score": 90.0
                },
                "summary": "Good candidate with relevant sustainability experience and certifications.",
                "strengths": [
                    "4+ years sustainability experience",
                    "Master's in Environmental Management",
                    "LEED certification",
                    "Consulting experience"
                ],
                "concerns": [
                    "Limited data analysis experience"
                ],
                "recommendation": "consider"
            },
            "notes": [],
            "tags": ["sustainability", "leed_certified"],
            "created_at": datetime.now(timezone.utc) - timedelta(days=1),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=3),
            "reviewed_at": datetime.now(timezone.utc) - timedelta(hours=3)
        }
    ]
    
    await db.applications.insert_many(applications)
    
    # Update job application counts
    for job in jobs:
        job_apps = [app for app in applications if app['job_id'] == job['id']]
        await db.jobs.update_one(
            {"id": job['id']},
            {"$set": {"application_count": len(job_apps)}}
        )
    
    # Update candidate application IDs
    for candidate in candidates:
        candidate_apps = [app['id'] for app in applications if app['candidate_id'] == candidate['id']]
        await db.candidates.update_one(
            {"id": candidate['id']},
            {"$set": {"application_ids": candidate_apps}}
        )
    
    print(f"✅ Created {len(applications)} applications")
    return applications

async def seed_interviews(applications, users):
    """Create test interviews"""
    print("\n🎤 Creating interviews...")
    
    interviews = [
        {
            "id": "interview-1",
            "application_id": applications[1]['id'],  # DevOps candidate
            "interviewer_id": users[0]['id'],
            "interview_type": "video",
            "duration_minutes": 60,
            "scheduled_at": datetime.now(timezone.utc) + timedelta(days=2, hours=10),
            "meeting_link": "https://meet.google.com/abc-defg-hij",
            "status": "scheduled",
            "notes": "Technical interview - focus on Kubernetes and AWS",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=12)
        },
        {
            "id": "interview-2",
            "application_id": applications[0]['id'],  # Full-stack candidate
            "interviewer_id": users[0]['id'],
            "interview_type": "video",
            "duration_minutes": 45,
            "scheduled_at": datetime.now(timezone.utc) - timedelta(days=1),
            "meeting_link": "https://meet.google.com/xyz-abcd-efg",
            "status": "completed",
            "notes": "Initial screening call",
            "feedback": {
                "rating": 5,
                "strengths": [
                    "Excellent communication skills",
                    "Deep technical knowledge",
                    "Great problem-solving approach"
                ],
                "weaknesses": [],
                "notes": "Very impressed with the candidate. Strong technical skills and cultural fit.",
                "recommendation": "strong_hire"
            },
            "created_at": datetime.now(timezone.utc) - timedelta(days=3),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=6)
        }
    ]
    
    await db.interviews.insert_many(interviews)
    print(f"✅ Created {len(interviews)} interviews")
    return interviews

async def main():
    """Main seed function"""
    print("\n" + "="*60)
    print("🌱 SEEDING HIREFLOW AI DATABASE")
    print("="*60)
    
    try:
        # Clear existing data
        await clear_existing_data()
        
        # Seed data in order
        users = await seed_users()
        companies = await seed_companies(users)
        jobs = await seed_jobs(companies)
        candidates = await seed_candidates()
        applications = await seed_applications(jobs, candidates)
        interviews = await seed_interviews(applications, users)
        
        print("\n" + "="*60)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   👤 Users: {len(users)}")
        print(f"   🏢 Companies: {len(companies)}")
        print(f"   💼 Jobs: {len(jobs)}")
        print(f"   👨‍💼 Candidates: {len(candidates)}")
        print(f"   📄 Applications: {len(applications)}")
        print(f"   🎤 Interviews: {len(interviews)}")
        print("\n🔐 Login Credentials:")
        print("   📧 admin@techcorp.com / password123")
        print("   📧 hr@innovateai.com / password123")
        print("   📧 recruiter@greenventures.com / password123")
        print("\n🌐 Career Pages:")
        print("   🔗 techcorp.hireflow.ai")
        print("   🔗 innovateai.hireflow.ai")
        print("   🔗 greenventures.hireflow.ai")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
