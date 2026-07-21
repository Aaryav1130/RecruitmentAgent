import streamlit as st
import pandas as pd
import os
import json
import tempfile
import PyPDF2
import docx
from datetime import datetime,timedelta
from ui_utils import role_requirements,resume_qa_section
import subprocess
import base64
from pathlib import Path
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
import requests
import streamlit.components.v1 as components

# --------------------------------------------------
# Thread executor (global)

executor = ThreadPoolExecutor(max_workers=2)


# --------------------------------------------------

def render_latex_to_pdf(latex_code):
        try:
            # Define the path to your LaTeX compiler (xelatex or any other compiler)
            xelatex_path = "/usr/local/texlive/2025basic/bin/universal-darwin/xelatex"  # Adjust this path accordingly
            
            # Create a temporary directory to store LaTeX file and PDF output
            with tempfile.TemporaryDirectory() as tmpdirname:
                tex_file = Path(tmpdirname) / "resume.tex"
                pdf_file = Path(tmpdirname) / "resume.pdf"

                # Step 1: Write LaTeX code to a temporary .tex file
                tex_file.write_text(latex_code)

                # Step 2: Compile the LaTeX code using xelatex
                result = subprocess.run(
                    [xelatex_path, "-interaction=nonstopmode", str(tex_file)],
                    cwd=tmpdirname,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Step 3: Capture LaTeX Compilation Error (if any)
                error = result.stderr.decode('utf-8')

                if error:
                    st.text_area("LaTeX Compilation Error", error)

                # Step 4: Read the compiled PDF
                pdf_bytes = pdf_file.read_bytes()

                # Step 5: Convert PDF to Base64 for inline rendering in Streamlit
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="1350" height="1000"></iframe>',
                    unsafe_allow_html=True
                )

                # Step 6: Allow the user to download the compiled PDF
                st.download_button("Download Resume PDF", pdf_bytes, file_name="resume.pdf")

        except subprocess.CalledProcessError as e:
            st.error(f"Failed to compile PDF. Check your LaTeX code.\nError: {e}")
        except FileNotFoundError:
            st.error("xelatex not found. Make sure BasicTeX is installed and the path is correct.")

# Create directories if they don't exist
os.makedirs("agents", exist_ok=True)
os.makedirs("utils", exist_ok=True)
os.makedirs("saved_jobs", exist_ok=True)

# Import the UI utilities for improved display
from ui_utils import (
    display_formatted_analysis_new,
    display_resume_analysis_summary,
    display_extracted_information,
    format_job_description,
    display_matching_skills,
    apply_styling
)
# IMport job storage funcitons
from utils.job_storage import (
    save_jobs_to_local,
    load_saved_jobs,
    remove_saved_job
)

# Import configuration
from config import COLORS,JOB_PLATFORMS

# Set page configuration with professional appearance
st.set_page_config(
    page_title="Professional Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Custom CSS
apply_styling()

# Initialize tools and agents
@st.cache_resource
def load_resources():
    """Load and cache all required resources"""
    from utils.serp_api_searcher import SerpApiSearcher
    from agents.job_search_agent import JobSearchAgent
    from agents.interview_agent import InterviewAgent

    job_search_agent=JobSearchAgent()
    interview_agent=InterviewAgent()
    serp_api_searcher=SerpApiSearcher()



    return {
 
        "job_search_agent": job_search_agent,
        "interview_agent": interview_agent,
        "serp_api_searcher": serp_api_searcher,
    }

# Load resources
resources=load_resources()

st.markdown("""
<style>
header {visibility: hidden;}
.block-container { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)
st.image("Images/5logo.png", width="content")


# Session state initialization
# Create session-local agent (one per user/session)
if "analysis_agent" not in st.session_state:
    from agents.analysis_agent import Implement
    st.session_state.analysis_agent = Implement()


if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = load_saved_jobs()
if "latex_code" not in st.session_state:
    st.session_state.latex_code = None
if "tab4_state" not in st.session_state:
    st.session_state.tab4_state = "idle"
if "live_interview" not in st.session_state:
    st.session_state.live_interview=False
if "final_report" not in st.session_state:
    st.session_state.final_report = None
    # 1. Initialize a loading state if not present
if "processing_report" not in st.session_state:
    st.session_state.processing_report = False

# --------------------------------------------------


defaults = {
    "job_id": None,
    "active_resume_name": None,
    "preprocess_future": None,
    "analyze_requested": False,
    "analysis_running": False,
    "analysis_result": None,
    "resume_text": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------


# Create main navigation tabs
tabs=st.tabs([
    "📄 Resume Analysis", 
    "🔍 Job Search", 
    "🎯 Interview Preparation", 
    "💼 Saved Jobs"
])


# Make sure the correct tab is active if coming from another section
if hasattr(st.session_state, 'active_tab'):
    active_tab_index = st.session_state.active_tab
    # We can't directly set the active tab, so we'll rely on session state changes to indicate
    # which tab should be active when the page reruns

# Tab 1: Resume Analysis
with tabs[0]:
    st.header("Resume Analysis")


    # Create two columsn for upload options
    col1,col2=st.columns(2)

    with col1:
        # Resume upload section
        st.subheader("📄 Upload Resume")

        st.markdown("""<div style="color:white; font-size:1rem;margin-bottom: 15px;">
                    <p style="margin-bottom:1px">We'll analyze your resume and extract key information to help you find matching jobs</p>
                    <p style="margin-top:1px"><i>suggested</i>: PDF, DOCX, or TXT format.</p></div>""",unsafe_allow_html=True)

        #Resume file uploader
        resume_file=st.file_uploader("Upload your Resume",type=["pdf","txt","docx"],key="resume_uploader")

        # --------------------------------------------------
        # BACKGROUND PREPROCESSING (ON UPLOAD)
        # --------------------------------------------------
        if resume_file and st.session_state.active_resume_name != resume_file.name:
            new_job_id = str(uuid.uuid4())

            # Reset state for new upload
            st.session_state.job_id = new_job_id
            st.session_state.active_resume_name = resume_file.name
            st.session_state.preprocess_future = None
            st.session_state.analyze_requested = False
            st.session_state.analysis_running = False
            st.session_state.analysis_result = None
            st.session_state.resume_text = None

            resume_analyser = st.session_state.analysis_agent

            # Start background preprocessing
            st.session_state.preprocess_future = executor.submit(
                resume_analyser.preprocess_resume,
                resume_file,
                new_job_id,
            )

            st.warning(f"Resume uploaded:✅ Please refresh the page first to upload new Resume")

        ######################################################################################################################################
        st.markdown("---")
        new_col1,new_col2=st.columns([2,1])

        with new_col1:
            role=st.selectbox("Select the role you're applying for:",list(role_requirements.keys()))

        with new_col2:
            upload_jd=st.checkbox("Upload custom job description instead")
        custom_jd=None
        if upload_jd:
            custom_jd_file=st.file_uploader("Upload job description (PDF or TXT)",type=["pdf","txt"])
            if custom_jd_file:
                st.success("✅ Custom job description uploaded!")
                custom_jd=custom_jd_file
        if not upload_jd:
            st.info(f"Required skills: {', '.join(role_requirements[role])}")
            st.markdown(f"""<p style="font-size: 12px;">Cutoff Score for selection: <b>{75}/100</b></p>""",
                        unsafe_allow_html=True)
            
        

        ######################################################################################################################################
        # --------------------------------------------------
        # ANALYZE BUTTON (ONE REQUEST ONLY)
        # --------------------------------------------------
        if st.button("🔍 Analyze Resume",width="stretch",disabled=st.session_state.analyze_requested):
            if st.session_state.preprocess_future is None:
                st.warning("Please upload a resume first.")
            else:
                st.session_state.analyze_requested = True
        # --------------------------------------------------
        # ORCHESTRATION LOGIC
        # --------------------------------------------------
        if st.session_state.analyze_requested and st.session_state.analysis_result is None:

            # Wait until preprocessing finishes
            if not st.session_state.preprocess_future.done():
                with st.spinner("Please wait processing will take some time..."):
                    time.sleep(20)
                st.rerun()

            # Preprocessing finished
            finished_job_id = st.session_state.preprocess_future.result()

            # 🔒 Ignore stale uploads
            if finished_job_id != st.session_state.job_id:
                st.warning("Old resume discarded. Please wait for the latest upload.")
                st.stop()

            # Run analysis ONCE
            if not st.session_state.analysis_running:
                st.session_state.analysis_running = True
                resume_analyser = st.session_state.analysis_agent





                with st.spinner("Analyzing your resume..."):
                    try:
                        if custom_jd:
                            with tempfile.NamedTemporaryFile(delete=False,suffix=f".{custom_jd.name.split('.')[-1]}") as temp_file:
                                temp_file.write(custom_jd.getbuffer())
                                temp_path=temp_file.name
                            analysis_result,extracted_text=resume_analyser.analyze_resume(resume_file,custom_jd=custom_jd)
                        else:
                            analysis_result,extracted_text=resume_analyser.analyze_resume(resume_file,role=role_requirements[role])
                        try:
                            if extracted_text:
                                st.session_state.analysis_result = analysis_result
                                st.session_state.resume_text = extracted_text
                            else:
                                st.error("Could not extract text from the uploaded file.")
                        except Exception as file_error:
                            st.error(f"Error processng file: {str(file_error)}")
                            st.info("If the error persists, try uploading a different file format or check if the resume is properly formatted.")

                    except Exception as e:
                        st.error(f"Error analyzing resume: {e}")
                        st.info("If the error persists, try uploading a different file format or check if the resume is properly formatted.")

        

        # FINAL OUTPUT + VERIFICATION
        if st.session_state.analysis_result:
            st.success("✅ Resume analysis complete!")

            # Store for downstream tabs
            st.session_state.resume_data = st.session_state.analysis_result
            st.session_state.resume_data["raw_text"] = st.session_state.resume_text




            ######################################################################################################################################
        with col2:
            
            colo1,colo2=st.columns([2,1])
            with colo1:


                st.image(
                            "Images/logo_frontened.png",
                            width="content"
                        )
            with colo2:
            
                #ATS optimization tips
                st.markdown(f"""
                <div style="background-color: {COLORS["nineth"]}; color: white; padding: 15px; border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0;font-size: 19px; color: white;"><strong>✪  ATS Optimization :</strong></h4>
                <ul style="margin-bottom: 15px;">
                <li>Use keywords from the job description</li>
                <li>Avoid tables, headers/footers, and images</li>
                <li>Use standard section headings</li>
                <li>Submit in PDF format when possible</li>
                <li>Keep formatting simple and clean</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            #Resume tips and advice
            st.subheader("🔑 Resume Tips")
            st.markdown(f"""
            <div style="background-color: {COLORS["tenth"]}; color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; color: white;"><strong>✪  Key Resume Components:</strong></h4>
            <ul style="margin-bottom: 15px;">
            <li><strong>Clear contact information</strong> - Make it easy for employers to reach you</li>
            <li><strong>Relevant skills section</strong> - Highlight technical and soft skills</li>
            <li><strong>Quantified achievements</strong> - Use numbers to demonstrate impact</li>
            <li><strong>ATS-friendly format</strong> - Use standard headings and keywords</li>
            <li><strong>Consistent formatting</strong> - Maintain professional appearance</li>
            </ul>
            </div>
            """,unsafe_allow_html=True)




    # Display resume analysis results if available
    if "resume_data" in st.session_state and st.session_state.resume_data:
        st.markdown("---")

        # Create tabs for different views of resume data
        resume_tabs=st.tabs(["Summary", "Skills & Experience", "Analysis", "Improved Resume"])

        # Tab1: Summary view
        with resume_tabs[0]:
            display_resume_analysis_summary(st.session_state.resume_data)

        # Tab 2: Skills & Experience
        with resume_tabs[1]:
            display_extracted_information(st.session_state.resume_data,resume_file)
    
        # Tab 3: Analysis
        with resume_tabs[2]:
            if "resume_overall_analysis" in st.session_state.resume_data:
                display_formatted_analysis_new(st.session_state.resume_data["resume_overall_analysis"])
            else:
                st.info("No detailed analysis available. Please re-upload your resume to generate an analysis.")

        # # Tab 4: Improved resume
        # with resume_tabs[3]:
        #     if not st.session_state.latex_code:
        #         if st.button("🚀 Improve Resume", key="improve_resume",width="content"):
        #             resume_analyser=st.session_state.analysis_agent
        #             latex = resume_analyser.get_improved_resume(
        #                 st.session_state.analysis_result
        #             )

        #             st.session_state.latex_code = latex
        #             render_latex_to_pdf(latex_code=st.session_state.latex_code)    
        #     else:
        #         st.info("Improved resume not available.")
        ################################################################################################################
        with resume_tabs[3]:

            tab_container = st.container()

            # ---------- IDLE ----------
            if st.session_state.tab4_state == "idle":

                left, right = tab_container.columns([1, 2])

                with left:
                    st.image(
                        "Images/cv_template_hero.avif",
                        caption="Create your own Professional Resume",
                        width="content"
                    )

                with right:
                    st.markdown("<div style='padding-top:120px; text-align:center'>", unsafe_allow_html=True)
                    st.markdown(
                        """
                        <div style="text-align:center">
                            <div style="font-size:40px; font-weight:bold; color:#cdcdcd; margin-bottom:10px;">Ready to improve your resume?</div>
                            <div style="font-size:20px; color:#555;">Click the button below to generate a clean, ATS-friendly Resume.</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
                    # Centered button in middle column
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        button_container = st.container()
                        with button_container:
                            improve_clicked = st.button("🚀 Improve Resume", key="improve_resume",width="content")

                    # Isolated CSS for ONLY this button
                    st.markdown("""
                    <style>
                    div[data-testid="stContainer"] > div > button {
                        width: 100% !important;
                        padding: 25px 0 !important;
                        font-size: 24px !important;
                        border-radius: 12px !important;
                        background-color: #4CAF50 !important;
                        color: white !important;
                    }
                    div[data-testid="stContainer"] > div > button:hover {
                        background-color: #45a049 !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    if improve_clicked:
                        st.session_state.tab4_state = "generating"
                        st.rerun()

            # ---------- GENERATING ----------
            elif st.session_state.tab4_state == "generating":

                # Spinner with isolated styling (no purple bar)
                tab_container.markdown("""
                <style>
                .spinner-title {
                    font-size: 28px;
                    font-weight: bold;
                    color: #333 !important;
                    background: none !important;
                    padding: 0 !important;
                    margin: 20px 0 10px 0 !important;
                    box-shadow: none !important;
                }
                .spinner-text {
                    font-size: 18px;
                    color: #555 !important;
                }
                .loader {
                    border: 10px solid #f3f3f3;
                    border-top: 10px solid #4CAF50;
                    border-radius: 50%;
                    width: 80px;
                    height: 80px;
                    animation: spin 1s linear infinite;
                    margin: auto;
                }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                </style>

                <div style="text-align:center; padding-top:120px">
                    <div class="loader"></div>
                    <div class="spinner-title">✨ Improving your resume</div>
                    <div class="spinner-text">Please wait while we analyze and format your resume</div>
                </div>
                """, unsafe_allow_html=True)

                # 🔹 LLM CALL (REAL ONE)
                resume_analyser=st.session_state.analysis_agent
                try:
                    latex = resume_analyser.get_improved_resume(
                        st.session_state.analysis_result
                    )

                    st.session_state.latex_code = latex
                    st.session_state.tab4_state = "done"

                except Exception as e:
                    st.error(str(e))
                    st.session_state.tab4_state = "idle"

                st.rerun()

            # ---------- DONE ----------
            elif st.session_state.tab4_state == "done":

                with tab_container:

                    st.success("✅ Improved resume generated")

                    render_latex_to_pdf(st.session_state.latex_code)

        # Add a section to explain resume improvement suggestions
            ########################################################################################################################################################################
        resume_analyser=st.session_state.analysis_agent

        st.markdown("---")
        resume_qa_section(ask_question_func=lambda q: resume_analyser.ask_question(q))
        st.markdown("---")
    else:
        # Display a message when no resume is uploaded
        st.markdown(f"""
        <div style="background-color: {COLORS["background"]}; padding: 20px; border-radius: 8px; border: 1px dashed {COLORS["primary"]}; text-align: center; margin-top: 30px;">
        <img src="https://img.icons8.com/fluency/96/000000/resume.png" style="width: 64px; height: 64px; margin-bottom: 15px;">
        <h3 style="color: {COLORS["primary"]};">No Resume Uploaded</h3>
        <p>Upload your resume using the file uploader above to see the analysis.</p>
        </div>
        """, unsafe_allow_html=True)


with tabs[1]:
    st.header("Job Search")

    # Common job titles and locations
    common_job_titles = [
        "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
        "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
        "Full Stack Developer", "DevOps Engineer", "UX Designer", "AI Engineer",
        "Cloud Architect", "Database Administrator", "Project Manager", "Business Analyst",
        "Java Developer", "Python Developer", "React Developer", "Android Developer",
        "iOS Developer", "Node.js Developer", "Data Engineer", "Blockchain Developer",
        "Cybersecurity Analyst", "Quality Assurance Engineer"
    ]
    
    locations = [
        "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
        "Pune, India", "Chennai, India","India", "London, UK", "Berlin, Germany", "Toronto, Canada",
        "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
        "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
    ]

  
    with st.form("job_search_form"):
        st.subheader("Search Criteria")

        # Create a 2-column layout for job title and location
        col1,col2=st.columns(2)
        
        with col1:
            title = st.session_state.resume_data.get("job_role", "Data Scientist")

            # Normalize for comparison
            title_lower = title.lower()
            titles_lower = [job.lower() for job in common_job_titles]

            if title_lower in titles_lower:
                default_index = titles_lower.index(title_lower)
            else:
                default_index = titles_lower.index("data scientist")

            keywords = st.selectbox(
                "Job Title:",
                common_job_titles,
                index=default_index,
                key="job_titles"
            )


        with col2:
            location=st.selectbox("Location:", locations, key="locations")

        # Advanced filters accordion
        with st.expander("Advance Filters",expanded=False):
            # Job type selection
            job_types=["Full-time", "Part-time", "Contract", "Internship"]
            selected_job_types=st.selectbox("Job Types (optional):",job_types,key="job_types")

            # Experience level
            experience_level=st.select_slider(
                "Years of experience:",
                options=["0-1","1-3", "3-5", "5-10", "10+"],
                value="1-3",
                key="experience_level"
            )

            # Recency filter
            recency=st.select_slider(
                "Show jobs posted within:",
                options=["1 day", "3 days", "1 week", "2 weeks", "1 month", "Any time"],
                value="1 week",
                key="recency"
            )

            # Platform selection
            selected_platforms=st.multiselect(
                "Job Platforms:",
                options=JOB_PLATFORMS,
                default=["LinkedIn"],
                key="platforms"
            )

            # Number of results
            job_count=st.slider("Jobs per platform:",1,10,5,key="job_count")

            # Use Serapi option
            use_serp_api=st.checkbox("Use SerpAPI for more jobs",value=False,key="use_serp_api")

        submit_search=st.form_submit_button("Search Jobs")

    # Execute job search
    if submit_search:
        # Build the search query including job types and experience
        search_query=keywords

        # Add job types to query if selected
        if selected_job_types:
            search_query+=f" {selected_job_types}"

        # Add experience level to wuery if needed
        if experience_level: # if not default
            search_query+=f" experience of {experience_level} years"

        # Convert recency to day for API
        recency_days={
            "1 day": 1, "3 days": 3, "1 week": 7,
            "2 weeks": 14, "1 month": 30, "Any time": 365
        }
        days_ago=recency_days.get(recency,7)

        if not st.session_state.resume_data:
            st.warning("Please upload and analyze your resume first for better job matching.")

        search_message=f"Searching for {search_query} jobs in {location}"
        search_message+=f" posted within the last {recency}"
        if selected_job_types:
            search_message+=f" ({selected_job_types})"
        
        with st.spinner(search_message):
            jobs=[]
            if use_serp_api:
                # Use serpapi to get real job listings
                serp_api_searcher=resources["serp_api_searcher"]
                for platform in selected_platforms:
                    try:
                        platform_jobs=serp_api_searcher.search_jobs(
                            keywords=search_query,
                            location=location,
                            platform=platform,
                            count=job_count,
                            days_ago=days_ago
                        )
                        jobs.extend(platform_jobs)
                    except Exception as e:
                        st.error(f"Error searching jobs on {platform}: {str(e)}")
                print(jobs)

                if not jobs:
                    st.warning("No jobs found via SerpAPI. Falling back to standard search.")
                    job_search_agent=resources["job_search_agent"]
                    try:
                        jobs=job_search_agent.search_jobs(
                            st.session_state.resume_data,
                            search_query,
                            location,
                            platforms=selected_platforms,
                            count=job_count
                        )
                    except Exception as e:
                        st.error(f"Error in job search: {str(e)}")
            else:
                # Use standard job search
                job_search_agent=resources["job_search_agent"]
                try:
                    jobs=job_search_agent.search_jobs(
                        st.session_state.resume_data,
                        search_query,
                        search_term=keywords,
                        location=location,
                        platforms=selected_platforms,
                        count=job_count,
                        days_ago=days_ago,
                        job_type=selected_job_types
                    )
                except Exception as e:
                    st.error(f"Error in job search: {str(e)}")
            
            st.session_state.job_results=jobs

    # Display job results (common to both search methods)
    if st.session_state.job_results:
        total_jobs=len(st.session_state.job_results)
        st.subheader(f"Job Results ({total_jobs})")

        # Filter options
        col1,col2=st.columns(2)
        with col1:
            # Sort options
            sort_option=st.selectbox(
                "Sort by:",
                ["Most Recent", "Relevance", "Company Name", "Location"],
                key="sort_options"
            )

        with col2:
            # Filter by platform
            filter_platform = st.selectbox(
                "Filter by platform:",
                ["All Platforms"] + JOB_PLATFORMS,
                key="filter_platform"
            )
        # Apply platform filter
        filtered_jobs=st.session_state.job_results
        if filter_platform!="All Platforms":
            filtered_jobs=[job for job in filtered_jobs if job.get("platform","").lower()==filter_platform.lower()]

        # Sort jobs based on selection
        sorted_jobs=filtered_jobs.copy()
        if sort_option=="Most Recent":
            # Try to parse dates for sorting
            for job in sorted_jobs:
                if job.get("date_posted") and isinstance(job["date_posted"],str):
                    try:
                        if "hour" in job["date_posted"].lower():
                            hours = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(hours=hours)
                        elif "day" in job["date_posted"].lower():
                            days = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=days)
                        elif "week" in job["date_posted"].lower():
                            weeks = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(weeks=weeks)
                        elif "month" in job["date_posted"].lower():
                            months = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=30 * months)
                        else:
                            job["sort_date"] = datetime.now() - timedelta(days=365)
                    except (ValueError,IndexError):
                        job["sort_date"]=datetime.now()-timedelta(days=365)
                else:
                    job["sort_date"]=datetime.now()-timedelta(days=365)
            
            sorted_jobs.sort(key=lambda x: x.get("sort_date"),reverse=False)
        elif sort_option=="Company Name":
            sorted_jobs.sort(key=lambda x: x.get("company", "").lower())
        elif sort_option == "Location":
            sorted_jobs.sort(key=lambda x: x.get("location", "").lower())

        if not sorted_jobs:
            st.warning(f"No jobs found for the selected platform: {filter_platform}")
        else:
            # Create a dataframe for easier display
            job_df=pd.DataFrame([
                {
                    "Title": job["title"],
                    "Company": job["company"],
                    "Location": job.get("location", "Not specified"),
                    "Platform": job.get("platform", "Unknown"),
                    "Posted": job.get("date_posted", "Recent"),
                    "Job Type": job.get("job_type", ""),
                    "Real Job": "✓" if job.get("is_real_job", False) else "?"
                }
                for job in sorted_jobs
            ])

            # Display jobs in a dataframe with improved styling
            st.dataframe(
                job_df,
                width="stretch",
                column_config={
                    "Title": st.column_config.TextColumn("Job Title"),
                    "Real Job": st.column_config.TextColumn("Verified")
                },
                hide_index=True
            )

            # Job selection for detailed view
            if sorted_jobs:
                st.markdown("### Job Details")
                selected_index=st.selectbox(
                    "Select a job to view details:",
                    range(len(sorted_jobs)),
                    format_func=lambda i: f"{sorted_jobs[i]['title']} at {sorted_jobs[i]['company']}",
                    key="job_selection"
                )

                if selected_index is not None:
                    st.session_state.selected_job=sorted_jobs[selected_index]
                    selected_job=st.session_state.selected_job

                    # job title and company with professsional styling
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, {COLORS["fourth"]}, {COLORS["fifth"]}); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.2);'>
                        <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{selected_job['title']}</h3>
                        <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job['company']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Create columns for jobs details
                    col1,col2,col3=st.columns(3)

                    with col1:
                        st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Location</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('location', 'Not specified')}</p>
                        </div>""", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Platform</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('platform', 'Unknown')}</p>
                        </div>""", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Posted</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('date_posted', 'Recent')}</p>
                        </div>""", unsafe_allow_html=True)

                    # Job type if available
                    if selected_job.get('job_type'):
                        st.markdown(f"""<div style="background-color: {COLORS["secondary"]}; color: white; 
                        padding: 8px 15px; border-radius: 20px; display: inline-block; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <span style="text-shadow: 1px 1px 1px rgba(0,0,0,0.2);">{selected_job.get('job_type')}</span></div>""", unsafe_allow_html=True)

                    # Apply button
                    if selected_job.get('apply_url'):
                        apply_url=selected_job['apply_url']
                        is_real_job=selected_job.get('is_real_job',False)

                        st.markdown(f"""
                        <div style="background-color: {COLORS["accent"]}; padding: 12px; 
                        border-radius: 6px; margin: 15px 0; text-align: center; box-shadow: 0 3px 8px rgba(0,0,0,0.15);">
                        <a href="{apply_url}" target="_blank" style="color: white; 
                        text-decoration: none; font-weight: bold; display: block; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                        {'➡️ Apply Now' if is_real_job else '➡️ View Job Details'}</a>
                        </div>
                        """, unsafe_allow_html=True)

                        if is_real_job:
                            st.success("This is a real job listing from a job search platform.")
                        else:
                            st.warning("This is a generated job listing for demonstration purposes.")
                    
                    # Job description
                    if selected_job.get("description"):
                        st.subheader("Job Description")
                        st.markdown(format_job_description(selected_job['description']),unsafe_allow_html=True)
                    else:
                        st.warning("No job description available.")
                    
                    # Job match analysis if resume is available
                    if st.session_state.resume_data:
                        with st.expander("Resume Match Analysis",expanded=True):
                            with st.spinner("Analyzing match between your resume and job..."):
                                # Display skills match
                                skills=st.session_state.resume_data.get("resume_skills",[])
                                job_description=selected_job.get('description','')

                                if skills and job_description:
                                    display_matching_skills(skills,job_description)

                                    # Get detailed match analysis
                                    job_search_agent=resources["job_search_agent"]
                                    match_analysis=job_search_agent.get_job_match_analysis(
                                        st.session_state.resume_data,
                                        selected_job
                                    )

                                    # Display match score
                                    match_score = match_analysis.get("match_score", 0)
                                    st.markdown(f"""
                                    <div style="text-align: center; margin: 20px 0;">
                                        <div style="background-color: {COLORS["primary"]}; display: inline-block; padding: 10px 20px; 
                                        border-radius: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                                            <span style="color: white; font-size: 1.5rem; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                                            Match Score: {match_score}%</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display recommendations
                                    recommendations = match_analysis.get("recommendations", [])
                                    if recommendations:
                                        st.markdown("#### Recommendations")
                                        for rec in recommendations:
                                            st.markdown(f"- {rec}")
                                else:
                                    st.info("Upload your resume in the Resume Analysis tab to see how well you match this job.")

                    # Job actions (save,prepare for interview)
                    col1,col2=st.columns(2)

                    with col1:
                        # Check if this job is already saved
                        job_title=selected_job.get('title','')
                        job_company=selected_job.get('company','')

                        is_saved=any(
                            saved_job.get('title')==job_title and saved_job.get('company')==job_company 
                            for saved_job in st.session_state.saved_jobs
                        )

                        if is_saved:
                            if st.button("Remove from Saved Jobs",key="remove_job_btn",width="stretch"):
                                # Remove job from saved jobs
                                if remove_saved_job(job_title,job_company):
                                    # Reload saved jobs
                                    st.session_state.saved_jobs=load_saved_jobs()
                                    st.success(f"Job {job_title} at {job_company} removed from saved jobs.")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove job from saved jobs.")
                        else:
                            if st.button("Save Job",key="save_job_btn",width="stretch"):
                                # Save job to local storage
                                saved_path=save_jobs_to_local(selected_job)
                                st.session_state.saved_jobs=load_saved_jobs()
                                st.success(f"Jobs saved successfully")
                                st.rerun()
                    with col2:
                        if st.button("Prepare for Interview", key="prepare_interview_btn",width="stretch"):
                            st.session_state.active_tab=2 #store which tab to activate
                            st.rerun()


# Tab 3: INterview Preparation
with tabs[2]:
    st.header("Interview Preparation")

    # Check if coming from another tab
    if hasattr(st.session_state,'active_tab') and st.session_state.active_tab==2:
        delattr(st.session_state,'active_tab') # Clear the flag

    # Check if we have a selected job
    if st.session_state.selected_job:
        selected_job=st.session_state.selected_job

        # job details display
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, {COLORS["fourth"]}, {COLORS["fifth"]}); 
        padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
            <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>Prepare for: {selected_job['title']}</h3>
            <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job['company']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Create columns
        col1,col2=st.columns(2)

        with col1:
            # Enhanced interview preparation options
            st.subheader("Preparation Type")
            interview_type = st.radio(
                "Select interview preparation type:",
                ["Technical Interview", "Behavioral Interview", "Coding Interview", "System Design", "Project Experience"],
                key="interview_type"
            )

            # Difficulty level
            difficulty = st.select_slider(
                "Interview difficulty:",
                options=["Entry Level", "Intermediate", "Advanced", "Expert"],
                value="Intermediate",
                key="interview_difficulty"
            )

            # Add specific focus areas based on selected interview type
            if interview_type == "Technical Interview":
                focus_areas = st.multiselect(
                    "Select focus areas:",
                    ["Algorithms", "Data Structures", "System Architecture", "Database", "Web Technologies", "DevOps", "Cloud"],
                    default=["Algorithms", "Data Structures"],
                    key="tech_focus_areas"
                )
            elif interview_type == "Coding Interview":
                focus_areas = st.multiselect(
                    "Select coding challenges:",
                    ["Array Problems", "String Manipulation", "Dynamic Programming", "Graph Algorithms", "Sorting", "Searching", "Object-Oriented Design"],
                    default=["Array Problems", "String Manipulation"],
                    key="coding_focus_areas"
                )
            elif interview_type == "Behavioral Interview":
                focus_areas = st.multiselect(
                    "Select behavioral aspects:",
                    ["Leadership", "Teamwork", "Conflict Resolution", "Problem Solving", "Time Management", "Adaptability", "Communication"],
                    default=["Leadership", "Teamwork"],
                    key="behavioral_focus_areas"
                )
            elif interview_type == "System Design":
                focus_areas = st.multiselect(
                    "Select design challenges:",
                    ["Scalability", "Database Design", "API Design", "Microservices", "Security", "Caching", "Load Balancing"],
                    default=["Scalability", "Database Design"],
                    key="design_focus_areas"
                )
            else:  # Project Experience
                focus_areas = st.multiselect(
                    "Select project aspects:",
                    ["Technical Challenges", "Project Management", "Teamwork", "Problem Solving", "Innovation", "Results", "Lessons Learned"],
                    default=["Technical Challenges", "Results"],
                    key="project_focus_areas"
                )


            # Number of questions
            num_questions = st.slider(
                "Number of questions:",
                1, 10, 5,
                key="num_interview_questions"
            )

        def start_interview():
            st.session_state.live_interview = True

        with col2:
            with st.container(border=True):
                st.subheader("🎤 Live Interview")
                st.image("Images/interview.webp", use_container_width=True)
                is_started = st.checkbox("Start Interview Mode", key="interview_toggle")
                if is_started:
                    st.link_button(
                    "🚀 Generate Interview",
                    "http://localhost:5173/",
                    use_container_width=True
                    )
                    st.session_state.live_interview=True
                    
    
        if st.session_state.live_interview and is_started:

            report_btn = st.button("Generate report", disabled=st.session_state.processing_report)

            if report_btn:
                st.session_state.processing_report = True

                with st.spinner("Fetching conversation and analyzing..."):
                    try:
                        # Step 1: Fetch current messages from Flask
                        response = requests.get("http://127.0.0.1:5001/get-messages", timeout=60)
                        if response.status_code != 200:
                            st.error(f"Backend returned error: {response.status_code}")
                            st.session_state.processing_report = False
                            st.stop()

                        messages = response.json()
                        if not messages:
                            st.error("No messages returned from backend")
                            st.session_state.processing_report = False
                            st.stop()

                        # Step 2: Call evaluation function
                        evaluation = resume_analyser.feedback_interview(messages)

                        if "error" in evaluation:
                            st.error(f"Evaluation failed: {evaluation['error']}")
                            st.session_state.processing_report = False
                            st.stop()

                        # Step 3: Store report
                        st.session_state.final_report = evaluation
                        st.success("Report generated successfully!")

                    except Exception as e:
                        st.error(f"Error: {e}")

            # --- Render report ---
            report = st.session_state.get("final_report")
            if report and isinstance(report, dict):
                st.subheader("🎯 Overall Score")
                score = report.get("overall_score", 0)
                st.progress(min(float(score)/10, 1.0))
                st.metric("Overall Score", f"{score}/10")

                st.write(report.get("final_summary", ""))

                st.subheader("📌 Recommendation")
                st.success(report.get("recommendation", ""))

                st.divider()
                st.subheader("📝 Question-wise Evaluation")
                for idx, q in enumerate(report.get("questions", []), 1):
                    with st.expander(f"Question {idx} — Score: {q.get('score', 0)}/10"):
                        st.markdown(f"**Question:** {q.get('question', 'N/A')}")
                        st.markdown(f"**Answer Summary:** {q.get('answer_summary', 'N/A')}")
                        st.markdown(f"**Strengths:** {q.get('strengths', 'N/A')}")
                        st.markdown(f"**Improvements:** {q.get('improvements', 'N/A')}")

    # --- CHANGE END HERE ---
        else:
            generate_btn = st.button("Generate Interview Questions", key="generate_interview_btn")
    

        # Generate interview questions
            if generate_btn:
                with st.spinner("Generating interview questions..."):
                    try:
                        interview_agent=resources["interview_agent"]

                        # Get the job description
                        job_description=selected_job.get('description','')

                        # Get resume data id available
                        resume_data=st.session_state.resume_data

                        # Create a more detailed prompt based on the interview type and focus areas
                        prompt_additions=f"Interview Type: {interview_type}\nDifficulty Level: {difficulty}\n"
                        if 'focus_areas' in locals():
                            prompt_additions+=f"Focus Areas: {', '.join(focus_areas)}\n"

                        # Create an enhanced job data object with our customizations
                        enhanced_job_data = selected_job.copy()
                        enhanced_job_data['interview_customization'] = prompt_additions

                        # Generate questions based on job description and resume
                        questions=interview_agent.generate_interview_questions(
                            job_data=enhanced_job_data,
                            resume_data=resume_data,
                            question_count=num_questions
                        )
                        
                        # Store in session state
                        st.session_state.interview_questions={
                            'job': selected_job,
                            'type': interview_type,
                            'difficulty': difficulty,
                            'focus_areas': focus_areas if 'focus_areas' in locals() else [],
                            'questions': questions
                        }

                        # Rerun to refresh the page
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating interview questions: {str(e)}")
                        st.info("Try with a different interview type or reduce the number of questions.")

        # Display generated questions with enhanced formatting
        if st.session_state.interview_questions:
            interview_data=st.session_state.interview_questions

            if interview_data['job']['title']==selected_job['title'] and interview_data['job']['company']==selected_job['company']:
                st.markdown(f"""
                <div style="background-color: {COLORS["secondary"]}; color: white; 
                padding: 10px 15px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{interview_data['type']} Questions ({interview_data['difficulty']})</h3>
                </div>
                """, unsafe_allow_html=True)

                # Create an expander for each question with space for notes
                for i,question in enumerate(interview_data['questions'],1):
                    # Check if question is a string or dictionary
                    if isinstance(question,str):
                        # If its a string,create a title and format the question
                        question_title=f"Question {i}"
                        question_text=question

                        # Extract question title if it has a clear format (e.g. "Title: Content")
                        if ": " in question and question.index(": ")<50:
                            parts=question.split(": ",1)
                            question_title=f"Question {i}: {parts[0]}"
                            question_text=parts[1]

                        with st.expander(question_title,expanded=i==1):
                            st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                            padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question_text}</span>
                            </div>""", unsafe_allow_html=True)

                            # Add note-taking area
                            note_key=f"note_{i}"
                            if note_key not in st.session_state:
                                st.session_state[note_key]=""

                            st.text_area("Your Notes:",key=note_key,height=100)
                    else:
                        # If its a dictionary,use the structured approach
                        question_title=f"Question {i}: {question.get('question', 'Question Details')}"
                        # Shorten the title if its too long
                        if len(question_title)>80:
                            question_title=question_title[:77]+"..."
                        with st.expander(question_title,expanded=i==1):
                            # Display full question text if it was truncated in the title
                            if len(question.get('question',''))>77 and "..." in question_title:
                                st.markdown(f"""<div style="background-color: {COLORS["question"]}; font-weight: bold;font-size: 18px;color: #070707; 
                                padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question.get('question')}</span>
                                </div>""", unsafe_allow_html=True)
                            # Display context if available
                            if question.get('context'):
                                st.markdown("<h4>Question Context</h4>", unsafe_allow_html=True)
                                st.markdown(f"""<div style="background-color: {COLORS["context"]}; color: #0F2A44; 
                                padding: 12px; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question['context']}</span>
                                </div>""", unsafe_allow_html=True)
                            
                            # Display suggested answer if available
                            if question.get('suggested_answer') or question.get('answer'):
                                answer = question.get('suggested_answer', question.get('answer', ''))
                                st.markdown("<h4>Suggested Approach</h4>", unsafe_allow_html=True)
                                st.markdown(f"""<div style="background-color: {COLORS["approach"]}; color: #1F5E3B; 
                                padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{answer}</span>
                                </div>""", unsafe_allow_html=True)
                            
                            # Display tips if available
                            if question.get('tips'):
                                st.markdown("<h4>Interview Tips</h4>", unsafe_allow_html=True)
                                st.markdown(f"""<div style="background-color: {COLORS["tips"]}; color: #7A4A00; 
                                padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question['tips']}</span>
                                </div>""", unsafe_allow_html=True)
                            
                            # Display code solution for coding questions if available
                            if question.get('code_solution'):
                                st.markdown("<h4>Code Solution</h4>", unsafe_allow_html=True)
                                st.code(question['code_solution'], language="python")
                            
                            # Add note-taking area
                            note_key = f"note_{i}"
                            if note_key not in st.session_state:
                                st.session_state[note_key] = ""
                            
                            st.text_area("Your Notes:", key=note_key, height=100)
    else:
        # No job selected
        st.info("Please select a job from the Job Search or Saved Jobs tab to prepare for an interview.")
        
        # Display generic interview preparation
        st.subheader("Generic Interview Preparation")
        
        # Common interview question types with expanded options
        interview_categories = [
            "Common Behavioral Questions",
            "Technical Interview Questions",
            "Programming & Coding Questions",
            "System Design Questions",
            "Problem-Solving Questions",
            "Cultural Fit Questions",
            "Leadership & Management Questions"
        ]

        selected_category=st.selectbox("Select question category:", interview_categories)

        # Add difficulty selection for generic questions
        generic_difficulty = st.select_slider(
            "Difficulty level:",
            options=["Entry Level", "Intermediate", "Advanced", "Expert"],
            value="Intermediate",
            key="generic_difficulty"
        )

        # Add focus areas based on selected category
        if "Technical" in selected_category:
            generic_focus = st.multiselect(
                "Select technical focus areas:",
                ["Web Development", "Mobile Development", "Cloud Computing", "DevOps", "Data Science", "Machine Learning", "Databases", "Security"],
                default=["Web Development"],
                key="generic_tech_focus"
            )
        elif "Programming" in selected_category or "Coding" in selected_category:
            generic_focus = st.multiselect(
                "Select programming focus areas:",
                ["Algorithms", "Data Structures", "Object-Oriented Design", "Functional Programming", "Front-end", "Back-end", "API Design"],
                default=["Algorithms", "Data Structures"],
                key="generic_coding_focus"
            )
        elif "System Design" in selected_category:
            generic_focus = st.multiselect(
                "Select system design areas:",
                ["Scalability", "High Availability", "Microservices", "APIs", "Databases", "Caching", "Load Balancing"],
                default=["Scalability", "APIs"],
                key="generic_design_focus"
            )
        # Number of questions
        generic_count = st.slider(
            "Number of questions:",
            5, 15, 8,
            key="generic_question_count"
        )

        # Generate generic questions button
        if st.button("Generate Generic Questions", key="generic_questions_btn"):
            with st.spinner("Generating generic interview questions..."):
                try:
                    interview_agent = resources["interview_agent"]
                    
                    # Generate questions based on selected category
                    generic_job = {
                        "title": "Generic Interview",
                        "company": "Various Companies",
                        "description": f"Prepare for {selected_category}",
                        "interview_customization": f"Difficulty Level: {generic_difficulty}\nFocus Areas: {', '.join(generic_focus) if 'generic_focus' in locals() else 'General'}"
                    }
                    
                    questions = interview_agent.generate_interview_questions(
                        job_data=generic_job,
                        question_count=generic_count
                    )
                    
                    # Store in session state
                    st.session_state.interview_questions = {
                        'job': {'title': 'Generic', 'company': 'Various'},
                        'type': selected_category,
                        'difficulty': generic_difficulty,
                        'questions': questions
                    }
                    
                    # Refresh the page
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating interview questions: {str(e)}")

        # Display generated generic questions
        if st.session_state.interview_questions and st.session_state.interview_questions['job']['title'] == 'Generic':
            interview_data = st.session_state.interview_questions
            
            st.markdown(f"""
            <div style="background-color: {COLORS["secondary"]}; color: white; 
            padding: 10px 15px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
            <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{interview_data['type']}</h3>
            </div>
            """, unsafe_allow_html=True)

            # Create an expander for each question with space for notes
            for i, question in enumerate(interview_data['questions'], 1):
                if isinstance(question, str):
                    # If it's a string, display it directly
                    with st.expander(f"Question {i}", expanded=i==1):
                        st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question}</span>
                        </div>""", unsafe_allow_html=True)
                        
                        # Add note-taking area
                        note_key = f"generic_note_{i}"
                        if note_key not in st.session_state:
                            st.session_state[note_key] = ""
                        
                        st.text_area("Your Notes:", key=note_key, height=100)
                else:
                    # If it's a dictionary, use the structured approach
                    question_title = f"Question {i}: {question.get('question', 'Question Details')}"
                    # Shorten the title if it's too long
                    if len(question_title) > 80:
                        question_title = question_title[:77] + "..."
                        
                    with st.expander(question_title, expanded=i==1):
                        # Display full question text if it was truncated in the title
                        if len(question.get('question', '')) > 77 and "..." in question_title:
                            st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                            padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question.get('question')}</span>
                            </div>""", unsafe_allow_html=True)
                        
                        # Display suggested answer if available
                        if question.get('suggested_answer'):
                            st.markdown("<h4>Suggested Answer</h4>", unsafe_allow_html=True)
                            st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                            padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question['suggested_answer']}</span>
                            </div>""", 
                            unsafe_allow_html=True)
                        
                        # Display tips if available
                        if question.get('tips'):
                            st.markdown("<h4>Tips</h4>", unsafe_allow_html=True)
                            st.markdown(f"""<div style="background-color: {COLORS["accent1"]}; color: white; 
                            padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <span style="text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{question['tips']}</span>
                            </div>""", 
                            unsafe_allow_html=True)
                        
                        # Add note-taking area
                        note_key = f"generic_note_{i}"
                        if note_key not in st.session_state:
                            st.session_state[note_key] = ""
                        
                        st.text_area("Your Notes:", key=note_key, height=100)


# Tab 4: Saved jobs
with tabs[3]:
    st.header("Saved Jobs")

    # Refresh saved jobs list
    st.session_state.saved_jobs=load_saved_jobs()

    if not st.session_state.saved_jobs:
        st.info("You haven't saved any jobs yet. Use the Job Search tab to find and save jobs.")
    else:
        # Display count of saved jobs
        st.markdown(f"""
        <div style="background-color: {COLORS["fifth"]}; color: white; 
        padding: 10px 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
        <h3 style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">You have {len(st.session_state.saved_jobs)} saved jobs</h3>
        </div>
        """, unsafe_allow_html=True)

         # Create a dataframe for saved jobs
        saved_jobs_df = pd.DataFrame([
            {
                "Title": job["title"],
                "Company": job["company"],
                "Location": job.get("location", "Not specified"),
                "Platform": job.get("platform", "Unknown"),
                "Date Saved": job.get("date_saved", "Recent")
            }
            for job in st.session_state.saved_jobs
        ])

        # Display saved jobs in a dataframe with improved styling
        st.dataframe(
            saved_jobs_df,
            width="stretch",
            column_config={
                "Title": st.column_config.TextColumn("Job Title"),
                "Date Saved": st.column_config.TextColumn("Saved On")
            },
            hide_index=True
        )

         # Allow selection of a saved job for detailed view
        if st.session_state.saved_jobs:
            st.markdown("### Job Details")
            selected_index = st.selectbox(
                "Select a job to view details:",
                range(len(st.session_state.saved_jobs)),
                format_func=lambda i: f"{st.session_state.saved_jobs[i]['title']} at {st.session_state.saved_jobs[i]['company']}",
                key="saved_job_selection"
            )

            if selected_index is not None:
                st.session_state.selected_job = st.session_state.saved_jobs[selected_index]
                selected_job = st.session_state.selected_job
                
                # Job title and company with professional styling
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, {COLORS["fourth"]}, {COLORS["fifth"]}); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.15);'>
                    <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{selected_job['title']}</h3>
                    <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job['company']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create columns for job details
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                    padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Location</p>
                    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('location', 'Not specified')}</p>
                    </div>""", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                    padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Platform</p>
                    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('platform', 'Unknown')}</p>
                    </div>""", unsafe_allow_html=True)
                
                with col3:
                    date_info = selected_job.get('date_saved', selected_job.get('date_posted', 'Recent'))
                    st.markdown(f"""<div style="background-color: {COLORS["sixth"]}; color: white; 
                    padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Date Saved</p>
                    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{date_info}</p>
                    </div>""", unsafe_allow_html=True)
                
                # Display job URL as a clickable link
                if selected_job.get('apply_url'):
                    st.markdown(f"""
                    <div style="background-color: {COLORS["accent"]}; padding: 12px; 
                    border-radius: 6px; margin: 15px 0; text-align: center; box-shadow: 0 3px 8px rgba(0,0,0,0.15);">
                    <a href="{selected_job['apply_url']}" target="_blank" style="color: white; 
                    text-decoration: none; font-weight: bold; display: block; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                    ➡️ Apply to this job</a>
                    </div>
                    """, unsafe_allow_html=True)

                # Display job description with better formatting
                if selected_job.get('description'):
                    st.subheader("Job Description")
                    st.markdown(format_job_description(selected_job['description']), unsafe_allow_html=True)
                else:
                    st.warning("No job description available.")

                # Job actions
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Remove from Saved Jobs", key="remove_saved_job_btn",width="stretch"):
                        # Remove job from saved jobs
                        job_title = selected_job.get('title', '')
                        job_company = selected_job.get('company', '')
                        
                        if remove_saved_job(job_title, job_company):
                            # Reload saved jobs
                            st.session_state.saved_jobs = load_saved_jobs()
                            st.success(f"Job {job_title} at {job_company} removed from saved jobs.")
                            st.rerun()
                        else:
                            st.error("Failed to remove job from saved jobs.")
                
                with col2:
                    if st.button("Prepare for Interview", key="saved_job_interview_btn",width="stretch"):
                        st.session_state.active_tab = 2  # Switch to Interview tab
                        st.rerun()
# Footer
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
    color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
    <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Professional Job Search Assistant | Built with Streamlit | © {datetime.now().year}</p>
    </div>""",
    unsafe_allow_html=True
)
