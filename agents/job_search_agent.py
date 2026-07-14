from utils.job_scraper import JobScrapper
from utils.serp_api_searcher import SerpApiSearcher
from config import GROQ_API_KEY,LLM_MODEL,JOB_PLATFORMS
import time

class JobSearchAgent:
    """Agent for searching and matching jobs."""
    def __init__(self):
        """Initialize the job search agent."""
        self.api_key=None
        self.model=LLM_MODEL
        self.job_scraper=JobScrapper()
        self.serp_api_searcher=SerpApiSearcher()

    def search_jobs(self,resume_data,keywords,search_term,location,platforms=None,count=5,days_ago=2,job_type="Fulltime"):
        """
        Search for jobs based on resume and keywords.
        
        Args:
            resume_data (dict): The parsed resume data
            keywords (str): Search keywords or job title
            location (str): Job location
            platforms (list): List of job platforms to search
            count (int): Number of jobs per platform
            
        Returns:
            list: List of job dictionaries
        """

        target_platforms = platforms or JOB_PLATFORMS
        final_results = []

        # results = self.job_scraper.search_jobs(keywords,search_term,location,target_platforms, count,days_ago,job_type=job_type)
        # final_results.extend(results)

        for platform in target_platforms:
            # 1. TIER 1: Try Real Scraping (JobSpy)
            time.sleep(4.0)
            results = self.job_scraper.search_jobs(keywords,search_term,location, [platform], count,days_ago,job_type=job_type)
            
            # 2. TIER 2: If Scraper fails (returns None), try SerpAPI
            if results is None:
                print(f"Scraper blocked for {platform}. Trying SerpAPI fallback...")
                results = self.serp_api_searcher.search_jobs(keywords, location, platform, count,days_ago)
            
            # 3. TIER 3: If both fail, use the platform-specific fake generator
            if not results:
                print(f"Real data unavailable for {platform}. Using specific safety net...")
                results = self.job_scraper.search_jobs(keywords,search_term,location, [platform], count, force_fake=True,days_ago=days_ago,job_type=job_type)  
            final_results.extend(results)
        # if not final_results:
        #     print(f"Real data unavailable for {target_platforms}. Using specific safety net...")
        #     results = self.job_scraper.search_jobs(keywords,search_term,location,target_platforms, count, force_fake=True,days_ago=days_ago,job_type=job_type)
        
        # final_results.extend(results)

        return final_results
        
    
    def get_job_match_analysis(self,resume_data,job_data):
        """
        Analyze how well a resume matches a job description.
        
        Args:
            resume_data (dict): The parsed resume data
            job_data (dict): The job listing data
            
        Returns:
            dict: Match analysis with score and recommendations
        """

        return self._generate_basic_match_analysis(resume_data, job_data)
        
        

    def _generate_basic_match_analysis(self,resume_data,job_data):
        """Generate basic job match analysis when OpenAI is not available."""
        skills=resume_data.get("resume_skills",[])
        job_description=job_data.get("description","").lower()

        # Count matching skills
        matching_skills=[skill for skill in skills if skill.lower() in job_description]

        # Calculate a simple match score
        match_score=min(len(matching_skills)*10,100) if skills else 50

        return {
            "match_score": match_score,
            "key_matches": matching_skills[:5],
            "gaps": ["Unable to analyze gaps without AI processing"],
            "recommendations": [
                "Review the job description and identify key requirements",
                "Customize your resume to highlight relevant skills and experience",
                "Add any missing skills that you possess but aren't in your resume"
            ]
        }
