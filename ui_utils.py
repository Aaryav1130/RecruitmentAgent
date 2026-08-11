import streamlit as st
from config import COLORS
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import base64


# Role requirement dictionary
role_requirements = {

    "AI Engineer": [
        "Python", "Transformers", "LLM APIs", "Prompt Engineering",
        "Retrieval-Augmented Generation", "Embeddings", "Semantic Search",
        "Vector Databases", "LangChain", "LlamaIndex", "LangGraph",
        "AI Agents", "Multi-Agent Systems", "Tool Calling",
        "LLM Fine-Tuning", "LoRA", "FastAPI",
        "Docker", "Model Evaluation", "Monitoring"
    ],

    "ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Scikit-Learn",
        "Supervised Learning", "Unsupervised Learning", "Deep Learning",
        "Transformers", "Feature Engineering",
        "Model Training", "Model Evaluation", "Hyperparameter Tuning",
        "Experiment Tracking", "Model Optimization",
        "Model Serving", "Docker", "Linux", "Git"
    ],

    "Agent Developer": [
        "Python", "AI Agents", "Multi-Agent Systems",
        "LangGraph", "LangChain", "LlamaIndex",
        "Retrieval-Augmented Generation", "Tool Calling",
        "Task Planning", "Memory Systems",
        "Vector Databases", "Prompt Engineering",
        "FastAPI", "Async Programming", "Docker"
    ],

    "Data Engineer": [
        "Python", "SQL", "Advanced SQL",
        "Data Modeling", "ETL", "ELT",
        "Apache Spark", "Kafka", "Airflow", "dbt",
        "Data Warehousing", "Batch Processing",
        "Streaming Processing", "Data Quality",
        "Linux", "Git"
    ],

    "Data Scientist": [
        "Python", "R", "Statistics", "Probability",
        "Hypothesis Testing", "Pandas", "NumPy",
        "Scikit-Learn", "Feature Engineering",
        "Model Evaluation", "Data Visualization",
        "SQL", "A/B Testing", "Time Series Analysis",
        "Machine Learning"
    ],

    "Frontend Engineer": [
        "JavaScript", "TypeScript",
        "React", "Next.js", "Vue", "Angular",
        "HTML5", "CSS3", "State Management",
        "API Integration", "Responsive Design",
        "Performance Optimization", "Accessibility",
        "Jest", "Cypress", "Git"
    ],

    "Backend Engineer": [
        "Python", "FastAPI", "Django",
        "Node.js", "Express",
        "Java", "Spring Boot",
        "REST APIs", "GraphQL",
        "System Design", "SQL", "PostgreSQL",
        "MongoDB", "Redis", "Kafka",
        "Authentication", "JWT", "OAuth2",
        "Docker", "CI/CD",
        "Logging", "Monitoring"
    ],

    "Full Stack Engineer": [
        "JavaScript", "TypeScript",
        "React", "Next.js",
        "Node.js", "Express",
        "Python", "FastAPI", "Django",
        "REST APIs", "GraphQL",
        "SQL", "PostgreSQL", "MongoDB",
        "Authentication", "JWT",
        "Responsive UI Development",
        "Docker", "CI/CD", "System Design"
    ],

    "DevOps Engineer": [
        "Linux", "Bash", "Docker",
        "Kubernetes", "Terraform", "Ansible",
        "CI/CD Pipelines", "GitHub Actions", "Jenkins",
        "AWS", "GCP", "Azure",
        "Networking", "Nginx",
        "Prometheus", "Grafana", "ELK Stack",
        "Infrastructure as Code", "Security Best Practices"
    ],

    "Product Manager": [
        "Product Strategy", "Roadmapping",
        "Prioritization Frameworks", "Agile", "Scrum",
        "User Research", "A/B Testing",
        "Product Analytics", "Market Research",
        "Competitive Analysis",
        "Stakeholder Management",
        "Technical Understanding", "API Knowledge",
        "KPIs", "OKRs", "Communication"
    ],

    "Cloud Engineer": [
        "AWS", "GCP", "Azure",
        "Cloud Architecture Design",
        "IAM", "VPC", "Load Balancing",
        "Auto Scaling", "Kubernetes",
        "Terraform", "CloudFormation",
        "Serverless", "Monitoring", "Logging",
        "Cost Optimization",
        "Backup", "Disaster Recovery"
    ],

    "Cybersecurity Engineer": [
        "Network Security", "Application Security",
        "OWASP Top 10", "Penetration Testing",
        "Vulnerability Assessment", "Threat Modeling",
        "SIEM", "Splunk", "ELK Stack",
        "IAM", "Cloud Security",
        "Encryption", "Incident Response",
        "Security Audits",
        "Python", "Bash", "Linux"
    ]

}



def display_resume_analysis_summary(resume_data):
    """Display a summary of the resume analysis with improved visibility.
    Args:
        resume_data (dict): The parsed resume data dictionary
    """
    if not resume_data:
        st.warning("Reasume data is not available.Please upload your resume.")
        return
    
    ############################################################################################################################################################################################################

    overall_score=resume_data.get('overall_score',0)
    selected=resume_data.get("selected",False)
    detailed_weaknesses=resume_data.get('detailed_weaknesses',[])


    ############################################################################################################################################################################################################
    
    # }
    tech_categories = {
    "Programming": ["python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "rust", "ruby", "php", "scala", "kotlin", "swift", "bash", "shell", "powershell"],
    "Data Science": ["data science", "data analysis", "statistics", "probability", "numpy", "pandas", "scipy", "matplotlib", "seaborn", "power bi", "tableau", "excel"],
    "Machine Learning & AI": ["machine learning", "deep learning", "artificial intelligence", "supervised learning", "unsupervised learning", "scikit-learn", "tensorflow", "keras", "pytorch", "nlp", "computer vision", "opencv", "recommendation systems", "time series"],
    "LLM / GenAI / Agentic": ["large language models", "llm", "genai", "generative ai", "prompt engineering", "chain-of-thought", "rag", "retrieval augmented generation", "agentic ai", "autonomous agents", "langchain", "langgraph", "llamaindex", "openai api", "groq", "anthropic", "huggingface", "transformers", "vector database", "embeddings", "faiss", "pinecone", "weaviate", "chroma"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "cloud", "ec2", "s3", "lambda", "ecs", "eks", "docker", "kubernetes", "helm", "ci/cd", "github actions", "gitlab ci", "terraform", "ansible", "linux", "nginx"],
    "Databases": ["sql", "mysql", "postgresql", "oracle", "mongodb", "dynamodb", "cassandra", "redis", "elasticsearch", "nosql"],
    "Web & Mobile": ["html", "css", "javascript", "react", "next.js", "vue", "angular", "node.js", "express", "django", "flask", "fastapi", "spring boot", "android", "ios", "react native", "flutter"],
    "Big Data & Streaming": ["hadoop", "spark", "pyspark", "kafka", "flink", "airflow", "databricks", "etl", "data pipelines"],
    "MLOps & Data Engineering": ["mlops", "model deployment", "model monitoring", "feature engineering", "mlflow", "kubeflow", "data versioning", "dvc"],
    "System Design & Architecture": ["system design", "software architecture", "microservices", "monolith", "distributed systems", "scalability", "load balancing", "high availability", "fault tolerance"],
    "Testing & Quality": ["unit testing", "integration testing", "pytest", "junit", "selenium", "cypress", "playwright", "test automation"],
    "Security": ["application security", "cybersecurity", "oauth", "jwt", "authentication", "authorization", "encryption", "ssl", "tls", "owasp"],
    "Other": []
}

    # Create summary
    st.subheader("📊 Resume Analysis Summary")

    # Srengths and areas to improve
    col1,col2=st.columns(2)

    with col1:
        st.markdown("""<h4 style="color: #1A237E; margin-bottom: 10px;">Strengths</h4>""",unsafe_allow_html=True)

        skills=resume_data.get("resume_skills",[])
        common_skills=resume_data.get("matching_skills",[])
        skills_lower = [s.lower() for s in skills]  # normalize

        ls = []

        # 1️⃣ Strong technical skill across multiple domains (≥2 skills in ≥2 domains)
        domain_counts = sum(
            1 for category, keywords in tech_categories.items()
            if len([s for s in skills_lower if any(k in s for k in keywords)]) >= 2
        )
        if domain_counts >= 3:
            ls.append("Strong technical skill set across multiple domains")

        if len(common_skills) >= 5:
            ls.append(
                "Your resume shows very strong alignment with the job description."
            )

        max_category = None
        max_count = 0

        for category, keywords in tech_categories.items():
            matched = [s for s in skills_lower if any(k in s for k in keywords)]
            count = len(matched)

            if count > max_count:
                max_count = count
                max_category = category

        # add only the top category if it meets minimum requirement
        if max_category and max_count >= 2:
            ls.append(f"Good {max_category} knowledge")

        # Remove duplicates
        lst= list(dict.fromkeys(ls))


    ############################################################################################################################################################################################################
       #  Display strengths with high-contrast styling
        if lst:
            for i in lst:
                st.markdown(
                    f"""<div style="background-color: #01579B; color: white; padding: 12px; border-radius: 6px; margin-bottom: 10px; font-weight: 500;">✅{i}</div>""",
                    unsafe_allow_html=True
                )
        else:
            st.markdown("""<div style="background-color: #546E7A; color: white; padding: 12px; border-radius: 6px;">Not enough information to determine strengths</div>""",
                        unsafe_allow_html=True
                        )
        
    with col2:
        st.markdown("""<h4 style="color: #B71C1C; margin-bottom: 10px;">Areas to Improve</h4>""",unsafe_allow_html=True)
        improvements=[]
        skills_lower = [s.lower() for s in skills]  # normalize
        improvements = []

        # 1️⃣ Version control
        if not any("git" in s for s in skills_lower):
            improvements.append("Version control experience (Git)")

        # 2️⃣ Databases
        if not any(any(k in s for k in tech_categories["Databases"]) for s in skills_lower):
            improvements.append("Database knowledge")

        # 3️⃣ Cloud & DevOps
        if not any(any(k in s for k in tech_categories["Cloud & DevOps"]) for s in skills_lower):
            improvements.append("Cloud platform experience")


############################################################################################################################################################################################################

        # Display improvement area with high-contrast styling
        if improvements:
            for improvement in improvements:
                st.markdown(
                    f"""<div style="background-color: #FA5C5C; color: white; padding: 12px; border-radius: 6px; margin-bottom: 10px; font-weight: 500;">⚠️{improvement}</div>""",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """<div style="background-color: #2E7D32; color: white; padding: 12px; border-radius: 6px;">No obvious improvement areas identified</div>""",
                unsafe_allow_html=True
            )
    
########################################################################################################################################################################################################
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    pie_col1,pie_col2=st.columns([1,2])

    with pie_col1:
        st.metric("overall Score",f"{overall_score}/100")
        fig=create_score_pie_chart(overall_score)
        st.pyplot(fig)
    with pie_col2:
        st.markdown("""
            <div style="
                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 250px;  /* match pie chart height */
                text-align: center;
            ">
            """, unsafe_allow_html=True)
        if selected:
            st.markdown("<h2 style='color:#4CAF50; '>✅ Congratulations! You have been shortlisted.</h2>",unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color:#d32f2f;'>❌ Unfortunately, You were not selected.</h2>",unsafe_allow_html=True)
        st.write("Candidate evaluated based on explicit resume content using semantic similarity and clear numeric scoring.")


    #Detailed weaknesses section

    if detailed_weaknesses:
        st.markdown('<hr>',unsafe_allow_html=True)
        st.subheader("📁 Detailed Weakness Analysis")

        for weakness in detailed_weaknesses:
            skill_name=weakness.get('skill','')

            with st.expander(f"{skill_name}"):
                # Close detail display
                detail=weakness.get('weakness','No specific details provided.')
                #Clean JSON formatting if it appears in the text
                if detail.startswith('```json') or '{' in detail:
                    detail="The resume lacks examples of this skill."
                st.markdown(f'<div class="weakness-detail"><strong>Issue:</strong> {detail}</div>',unsafe_allow_html=True)

                # Display improvement suggestions if available
                if 'improvement_suggestions' in weakness and weakness['improvement_suggestions']:
                    st.markdown("<strong>How to improve:</strong>",unsafe_allow_html=True)
                    for i,suggestion in enumerate(weakness['improvement_suggestions']):
                        st.markdown(f'<div class="solution-detail">{i+1}.{suggestion}</div>',unsafe_allow_html=True)

########################################################################################################################################################################
def create_score_pie_chart(score):
    """Create a pie chart showing the score"""
    # Make pie chart smaller
    fig, ax = plt.subplots(figsize=(3, 3))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    # Choose color based on score
    if score >= 75:
        score_color = "#32A536"   # green
    elif score >= 50:
        score_color = '#FF9800'   # orange
    else:
        score_color = '#d32f2f'   # red
    # Data
    sizes=[score,100-score]
    labels=['',''] #we'll use annotation instead
    colors=[score_color,'#333333']
    explode=(0.05,0) # explode the 1st size (score)

    # Plot
    wedges,texts=ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        startangle=90,
        wedgeprops={'width':0.5,'edgecolor':'black','linewidth':1}
    )

    # Draw a circle in the center to make it a donut chart
    centre_circle=patches.Circle((0,0),radius=0.25,facecolor='#111111')
    ax.add_artist(centre_circle)

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_aspect('equal')

    # Add score text in the center
    ax.text(0,0,f"{score}%",
            ha='center',va='center',
            fontsize=24,fontweight='bold',
            color='white')
    # Add pass/fail indicator
    status="PASS" if score>=70 else "FAIL"
    status_color="#4CAF50" if score >=70 else "#d32f2f"
    ax.text(0,-0.15,status,
            ha='center',va='center',
            fontsize=14,fontweight='bold',
            color=status_color)
    # Set the background color
    ax.set_facecolor('#111111')

    return fig



def resume_qa_section(ask_question_func=None):
    st.markdown('<div>',unsafe_allow_html=True)

    st.subheader("🔍 Resume Q&A")
    user_question=st.text_input("Enter your question about the resume:",
                                placeholder="e.g  What are the projects in this Resume")
    
    if user_question and ask_question_func:
    
        response=ask_question_func(user_question)

        # st.markdown('<div style="background-color: #111122; padding: 15px;' \
        # 'border-radius: 5px; border-left: 5px solid #d32f2f;">',
        # unsafe_allow_html=True)
        with st.chat_message("assistant",avatar="https://imgs.search.brave.com/1fads3PSU9YRNMwQ9oe2LXbnJatTdTBFIxFb_IViw6g/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTQ0/NTczMDg4Ny92ZWN0/b3IvY2hhdGJvdC1o/ZWFkLWluLXNwZWVj/aC1idWJibGUtdmVj/dG9yLWljb24uanBn/P3M9NjEyeDYxMiZ3/PTAmaz0yMCZjPTBO/Vkcyc2JTeE5ObzNt/R2ZDQ21HVVNxX0dD/MVVUdlB5ZU8xT25O/clkxM1U9"):
            st.markdown(f"<p>{response}</p>",unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

########################################################################################################################################################################


def clean_and_organize_experience(experience_items):
    """Helper function to organize experience into categories."""
    categories={
        "Programming Experience": [],
        "Machine Learning & AI": [],
        "Cloud & Infrastructure": [],
        "Data & Analysis": [],
        "Professional Experience": []
    }



    # Simple keyword-based categorization
    for item in experience_items:
        item_lower=item.lower()
        if any(kw in item_lower for kw in ["developed","implemented","engineered","designed","built","software","application","app","backend","frontend","api","rest","microservices","python","py","java","c++","cpp","c#","javascript","js","typescript","ts","framework","library","debugged","optimized","refactored","oop","dsa"]):
            categories["Programming Experience"].append(item)
        elif any(kw in item_lower for kw in ["machine learning","ml","deep learning","dl","artificial intelligence","ai","model","models","training","inference","prediction","nlp","cv","computer vision","classification","regression","clustering","tensorflow","tf","pytorch","torch","scikit-learn","sklearn","llm","rag","genai","transformer","embeddings"]):
            categories["Machine Learning & AI"].append(item)
        elif any(kw in item_lower for kw in ["cloud","aws","amazon web services","azure","gcp","google cloud","deployment","infra","infrastructure","server","docker","kubernetes","k8s","container","ci/cd","devops","terraform","linux","scalability","load balancing"]):
            categories["Cloud & Infrastructure"].append(item)
        elif any(kw in item_lower for kw in ["data analysis","data processing","analytics","eda","sql","nosql","dataset","datasets","dashboard","dashboards","reporting","bi","power bi","tableau","pandas","numpy","statistics","stats","visualization","etl","pipeline","pipelines"]):
            categories["Data & Analysis"].append(item)
        elif any(kw in item_lower for kw in ["intern","internship","project","projects","capstone","research","collaboration","team","teamwork","responsible for","worked on","contributed to","experience","role","roles","assignment","freelance","contract"]):
            categories["Professional Experience"].append(item)
    return categories



def display_extracted_information(resume_data,resume_file):
    """Display extracted resume information with better visibility.
        Args:
            resume_data (dict): The parsed resume data dictionary
    """
    if not resume_data:
        st.warning("Resume data is not available.Please upload your resume.")
        return
    st.subheader("Extracted Information")

    # Create columns for different information types
    info_col1,info_col2=st.columns(2)

    with info_col1:
        #Display contact info
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">📞Contact Information</h4>""",unsafe_allow_html=True)
        contact_info=resume_data.get("contact_info",{})
        contact_html="""<div style="background-color: #1A237E; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">"""

        if contact_info and (contact_info.get("email") or contact_info.get("phone")):
            if contact_info.get("email"):
                contact_html+=f"<p><strong>Email:</strong>{ contact_info["email"]}</p>"
            if contact_info.get("phone"):
                contact_html+=f"<p><strong>Phone:</strong>{ contact_info["phone"]}</p>"
        else:
            contact_html+="<p>No contact information detected.</p>"

        contact_html+="</div>"
        st.markdown(contact_html,unsafe_allow_html=True)

        #Display education
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">🎓 Education</h4>""",unsafe_allow_html=True)
        education=resume_data.get("education",[])
        education_html="""<div style="background-color: #4A148C; color: white; padding: 15px; border-radius: 8px;">"""

        if education:
            for edu in education:
                education_html+=f"<p>• {edu}</p>"
        else:
            education_html+="<p>No education information detected.</p>"

        education_html+="</div>"
        st.markdown(education_html,unsafe_allow_html=True)

        st.markdown("""<h4 style="color: #333; margin-bottom: 10px; margin-top: 10px;">🖼️ Resume Preview</h4>""",unsafe_allow_html=True)
        if resume_file:
            pdf_bytes = resume_file.getvalue()
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0" '
                f'width="100%" height="800"></iframe>',
                unsafe_allow_html=True
            )




    with info_col2:
        # Display skills with high-contrast horizontal layout
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">🛠️ Skills</h4>""",unsafe_allow_html=True)
        skills=resume_data.get("resume_skills",[])

        if skills:
            # Create a flex container for horizontal layout
            skills_html="""<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""

            # Add each skill with a high-contrast background
            for skill in skills:
                skills_html+=f"""<div style="background-color: #0D47A1; color: white;
                padding: 8px 12px; border-radius: 20px; font-weight: 500; margin-bottom: 8px;">
                {skill}</div>"""

            skills_html+="</div>"
            st.markdown(skills_html,unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background-color: #546E7A; color: white; padding: 15px; 
                border-radius: 8px;">No skills detected.</div>""",unsafe_allow_html=True)
        
        # Display experience using the organized categories function
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">💼 Experience</h4>""",unsafe_allow_html=True)
        experience=resume_data.get("experience",[])
        if experience:
            # Organize the experience items
            organized_exp=clean_and_organize_experience(experience)

            #Display each category in an accordion-like structure
            for category,items in organized_exp.items():
                if items:
                    # Set category-specific colors
                    if "Programming" in category:
                        bg_color="#01579B"  # Deep blue
                    elif "Machine Learning" in category or "AI" in category:
                        bg_color = "#4A148C"  # Deep purple
                    elif "Cloud" in category:
                        bg_color = "#004D40"  # Deep teal
                    elif "Data" in category:
                        bg_color = "#BF360C"  # Deep orange
                    elif "Companies" in category:
                        bg_color = "#B71C1C"  # Deep red
                    else:
                        bg_color = "#37474F"  # Deep blue-grey

                    # Create category header
                    st.markdown(
                        f"""<div style="background-color: {bg_color}; color: white; padding: 10px; 
                        border-radius: 8px 8px 0 0; font-weight: bold; margin-top: 10px;">{category} ({len(items)})</div>""",unsafe_allow_html=True
                    )

                    # Create flex container for items
                    items_html=f"""<div style="background-color: {bg_color}; opacity: 0.9; color: white; 
                    padding: 10px; border-radius: 0 0 8px 8px; margin-bottom: 10px;">
                    <div style="display: flex; flex-wrap: wrap; gap: 6px;">"""

                    for item in items:
                        items_html+=f"""<div style="background-color: rgba(255,255,255,0.2); 
                        padding: 6px 10px; border-radius: 15px; margin-bottom: 6px;">
                        {item}</div>"""
                    items_html+="</div></div>"
                    st.markdown(items_html,unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background-color: #546E7A; color: white; padding: 15px; 
                border-radius: 8px;">No experience information detected.</div>""", 
                unsafe_allow_html=True)
########################################################################################################################################################################

def display_formatted_analysis_new(resume_overall_analysis: dict):
    """
    Beautify and display Resume Overall Analysis (structured JSON)
    """

    if not resume_overall_analysis or not isinstance(resume_overall_analysis, dict):
        st.info("No resume analysis available")
        return

    # Section configuration
    section_config = {
        "overall_assessment": {
            "title": "Overall Assessment",
            "color": "#3a506b"
        },
        "content_improvements": {
            "title": "Content Improvements",
            "color": "#1b3a4b"
        },
        "format_suggestions": {
            "title": "Format Suggestions",
            "color": "#4d194d"
        },
        "ats_optimization": {
            "title": "ATS Optimization",
            "color": "#54478c"
        }
    }

    for section_key, config in section_config.items():
        section_data = resume_overall_analysis.get(section_key)

        if not section_data:
            continue

        st.subheader(config["title"])

        rendered_blocks = []

        for sub_key, items in section_data.items():
            if not items or items == ["Not found"]:
                continue

            # Human-readable subtitle
            subtitle = sub_key.replace("_", " ").title()

            bullet_html = "".join(
                f"<li>{item}</li>" for item in items if item
            )

            rendered_blocks.append(
                f"""
                <div style="margin-bottom:10px;">
                    <strong>{subtitle}</strong>
                    <ul style="margin-top:6px;">{bullet_html}</ul>
                </div>
                """
            )

        if rendered_blocks:
            st.markdown(
                f"""
                <div style="
                    background-color:{config['color']};
                    color:white;
                    padding:16px;
                    border-radius:10px;
                    font-size:15px;
                    line-height:1.6;
                ">
                    {''.join(rendered_blocks)}
                </div>
                """,
                unsafe_allow_html=True
            )

########################################################################################################################################################################
            
def display_formatted_analysis(analysis):
    """Format and display the resume analysis in a structured way with improved visibility.
    Args:
        analysis (str): The resume analysis text"""
    if not analysis:
        return
    
    # Extract sections using typical patterns
    sections={
        "Overall Assessment": "",
        "Content Improvements": "",
        "Skills": "",
        "Format Suggestions": "",
        "ATS Optimization": ""
    }

    current_section=None
    lines=analysis.split('\n')

    for line in lines:
        # Check if this line is a section header
        for section in sections.keys():
            if section.lower() in line.lower() or "strength" in line.lower() or "weakness" in line.lower():
                current_section=section
                break
        # Add content to the current section
        if current_section and line:
            sections[current_section]+=line+"\n"

    # Display each section in a formatted way with improved visibility
    section_colors={
        "Overall Assessment": "#3a506b",
        "Content Improvements": "#1b3a4b",
        "Skills": "#006466",
        "Format Suggestions": "#4d194d",
        "ATS Optimization": "#54478c"
    }

    for section,content in sections.items():
        if content.strip():
            st.subheader(section)
            bg_color=section_colors.get(section,"#3a506b")
            st.markdown(
                f"""<div style='background-color: {bg_color}; color: white; 
                padding: 15px; border-radius: 8px; margin-top: 10px; 
                font-size: 16px; line-height: 1.5;'>{content}</div>""", 
                unsafe_allow_html=True
            )



def format_job_description(description):
    """Format the job description for better readability with high contrast.
    Args:
        description (str): Job description text
    Returns:
    str: Formatted HTML for the job description"""
    if not description:
        return """<div style="background-color: #455A64; color: white; padding: 15px; 
                border-radius: 8px; margin-top: 15px;">No description available</div>"""
    
    # Clean up any problematic formatting
    description=description.replace('\n\n','<br><br>').replace('\n','<br>')

    # Wrap the description in a styled div with high contrast
    formatted_description=f"""
        <div style="background-color: #263238; color: white; padding: 15px; 
        border-radius: 8px; margin-top: 15px; line-height: 1.5; font-size: 16px;">
        {description}
        </div>
        """
    return formatted_description

def display_matching_skills(skills,job_description):
    """Display skills that match a job description with high-contrast styling.
    
    Args:
        skills (list): List of skills from resume
        job_description (str): Job description text
        """
    if not skills or not job_description:
        st.markdown(
            """<div style="background-color: #455A64; color: white; padding: 12px; 
            border-radius: 6px;">No matching skills could be determined.</div>""", 
            unsafe_allow_html=True
        )
        return
    job_desc=job_description.lower()

    matching_skills=[]
    for skill in skills:
        if skill.lower() in job_desc:
            matching_skills.append(skill)
    if matching_skills:
        st.markdown("""<h4 style="color: #26A69A; margin-bottom: 10px;">Skills Matching Job Description</h4>""",unsafe_allow_html=True)
        skills_html="""<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""
        
        for skill in matching_skills[:5]: # Show top 5 matching skills
            skills_html+=f"""<div style="background-color: #01579B; color: white; 
            padding: 8px 12px; border-radius: 20px; font-weight: 500; margin-bottom: 8px;">
            ✅ {skill}</div>"""

        skills_html+="</div>"
        st.markdown(skills_html,unsafe_allow_html=True)
    else:
        st.markdown(
            """<div style="background-color: #455A64; color: white; padding: 12px; 
            border-radius: 6px;">No matching skills detected in the job description.</div>""", 
            unsafe_allow_html=True
        )
    # Identify missing skills
    missing_skills=[]
    common_tech_skills=[
        "python", "java", "javascript", "sql", "aws", "azure", 
        "react", "node", "docker", "kubernetes", "machine learning",
        "data science", "agile", "scrum", "git", "ci/cd"
    ]

    for tech in common_tech_skills:
        if tech in job_desc and not any(tech.lower() in s.lower() for s in skills):
            missing_skills.append(tech)
    if missing_skills:
        st.markdown("""<h4 style="color: #B71C1C; margin-bottom: 10px;">Skills to Emphasize or Develop</h4>""",unsafe_allow_html=True)
        missing_html= """<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""
        
        for skill in missing_skills[:5]: #Show top 5 missing skills
            missing_html+=f"""<div style="background-color: #C62828; color: white; 
            padding: 8px 12px; border-radius: 20px; font-weight: 500; margin-bottom: 8px;">
            ⚠️ {skill.title()}</div>"""

        missing_html+="</div>"
        st.markdown(missing_html,unsafe_allow_html=True)


########################################################################################################################################################################


# Custom CSS to enhance teh UI with a professional balanced style
def apply_styling():
    st.markdown(f"""
    <style>
        /* Global font styling */
        * {{
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }}
        /* Main header styling - like the "You have 1 saved jobs" header */
        h2 {{
            color: white !important;
            background-color: {COLORS['seventh']} !important;
            padding: 20px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }}
        h1, .main-header {{
            color: white !important;
            background-color: {COLORS['eighth']} !important;
            padding: 20px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }}

        
        /* Blue header panels styling - consistent across all pages */
        div[style*="background-color: {COLORS['primary']}"],
        div[style*="background-color: rgb(28, 78, 128)"],
        [data-testid="stForm"] h3,
        .blue-header {{
            color: white !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
            padding: 15px !important;
            border-radius: 6px !important;
            margin-bottom: 15px !important;
            background-color: {COLORS['primary']} !important;
        }}
        
        /* Fix for text in blue panels */
        div[style*="background-color: {COLORS['primary']}"] p,
        div[style*="background-color: {COLORS['primary']}"] span,
        div[style*="background-color: {COLORS['primary']}"] h3,
        div[style*="background-color: {COLORS['primary']}"] h4,
        div[style*="background-color: {COLORS['primary']}"] div {{
            color: white !important;
            font-weight: bold !important;
        }}
        
        /* Buttons styled like "Apply to this job" button */
        .stButton>button,
        button[kind="primary"] {{
            background-color: {COLORS["accent3"]} !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            font-size: 16px !important;
            height: auto !important;
            margin-top:20px;
        }}
        
        .stButton>button:hover,
        button[kind="primary"]:hover {{
            background-color: #E67E22 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }}
        
        /* Tables like in Saved Jobs tab */
        table, .dataframe, [data-testid="stTable"] {{
            width: 100% !important;
            border-collapse: collapse !important;
            margin-bottom: 20px !important;
            border-radius: 4px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }}
        
        /* Table headers like "Saved Jobs" tab */
        th, thead tr th {{
            background-color: #222222 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 8px !important;
            text-align: left !important;
            border: none !important;
        }}
        
        /* Table cells like "Saved Jobs" tab */
        td, tbody tr td {{
            padding: 12px 8px !important;
            border-bottom: 1px solid #EEEEEE !important;
            background-color: white !important;
            color: black !important;
        }}
        
        /* Alternate row styling */
        tbody tr:nth-child(even) td {{
            background-color: #f9f9f9 !important;
        }}
        
        /* Main navigation tabs */
        div[data-baseweb="tab-list"] {{
            gap: 0 !important;
            background-color: {COLORS["background"]} !important;
            padding: 10px !important;
            border-radius: 12px !important;
            display: flex !important;
            justify-content: space-between !important;
            width: 100% !important;
            margin-bottom: 20px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        }}
        
        div[data-baseweb="tab-list"] button {{
            flex: 1 !important;
            text-align: center !important;
            margin: 0 5px !important;
            height: 60px !important;
            font-size: 16px !important;
            background-color: rgba(255, 255, 255, 0.7) !important;
            color: {COLORS["primary"]} !important;
            border-radius: 8px !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease !important;
        }}
        
        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: {COLORS["primary"]} !important;
            color: white !important;
            border-bottom: 3px solid {COLORS["accent3"]} !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transform: translateY(-2px) !important;
        }}

        /* Checkbox label text */
        div[data-testid="stCheckbox"] label {{
            font-size: 8px !important;
        }}

        /* Weakness detail styling */
        .weakness-detail {{
            background-color: #ffebee;
            color: #c62828;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #d32f2f;
        }}

        /* Solution styling */
        .solution-detail {{
            background-color: #e8f5e9;
            color: #2e7d32;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #388e3c;
        }}

        /* Example detail styling */
        .example-detail {{
            background-color: #000033;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #6666ff;
        }}

    </style>
    """, unsafe_allow_html=True)
        
