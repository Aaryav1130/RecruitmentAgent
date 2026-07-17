import pandas as pd
from jobspy import scrape_jobs
import random
import requests
import time
from datetime import datetime, date


class JobScrapper:
    def __init__(self):
        self.platform_map = {
            "LinkedIn": "linkedin",
            "Indeed": "indeed",
            "Glassdoor": "glassdoor",
            "Naukri": "naukri"
        }

        self.job_type_map={
            "Full-time": "fulltime",
            "Part-time": "parttime",
            "Internship":"internship",
            "Contract": "contract"
        }


    def relative_date(self,value):
        """
        Convert date/datetime/string to 'X days ago'
        """
        if not value:
            return "N/A"

        # If already relative text
        if isinstance(value, str) and "day" in value.lower():
            return value

        try:
            # Handle datetime / date
            if isinstance(value, (datetime, date)):
                posted_date = value.date() if isinstance(value, datetime) else value
            else:
                # Handle string date
                posted_date = datetime.strptime(str(value), "%Y-%m-%d").date()

            delta_days = (date.today() - posted_date).days

            if delta_days <= 0:
                return "Today"
            elif delta_days == 1:
                return "1 day ago"
            else:
                return f"{delta_days} days ago"

        except Exception:
            return "N/A"
    
    def search_jobs(self, keywords,search_term, location, platform=["LinkedIn"],count=5,days_ago=2 ,force_fake=False,job_type="Fulltime"):
        
        """Tier 1: Real Scraper (JobSpy) or Skip to Fake."""
        if force_fake:
            return self.get_platform_specific_fake_jobs(keywords, location, platform[0], count=1)

        try:
            flag=False
            print(" ")
            print("===========================================================================================================================")
            print(" ")
            print(keywords,"=>",type(keywords))
            print(search_term,"=>",type(search_term))
            print(location,"=>",type(location))
            print(platform,"=>",type(platform))
            print(count,"=>",type(count))
            print(days_ago,"=>",type(days_ago))
            print(job_type,"=>",type(job_type))
            print(" ")
            print("===========================================================================================================================")

            # site_key = list({
            #                     self.platform_map.get(p, "indeed")
            #                     for p in platform
            #                 })
            site_key = [self.platform_map.get(p,p.lower()) for p in platform]
            total_hours = int(days_ago) * 24
            # 2. Optimized Human-like Delay (Faster but safe)
            time.sleep(3.0)
            keywords+=f" in {location}"
            keywords+=f", within {days_ago} days"
            if location=="Remote":
                flag=True

            print(f"Scraping {site_key} for the last {total_hours} hours for {keywords}...")
            
            job_type_arg=self.job_type_map.get(job_type,job_type.lower())


            print(" ")
            print("===========================================================================================================================")
            print(" ")
            print(keywords,"=>",type(keywords))
            print(search_term,"=>",type(search_term))
            print(location,"=>",type(location))
            print(platform,"=>",type(platform))
            print(count,"=>",type(count))
            print(days_ago,"=>",type(days_ago))
            print(job_type,"=>",type(job_type))
            print(site_key,"=>",type(site_key))
            print(total_hours,"=>",type(total_hours))
            print(job_type_arg,"=>",type(job_type_arg))
            print(" ")
            print("===========================================================================================================================")

            # site_key = list({

            jobs_df = scrape_jobs(
                site_name=site_key,
                search_term=search_term,
                google_search_term=keywords,
                location=location,
                results_wanted=count,
                hours_old=total_hours,
                verbose=2,
                country_indeed="India",
                is_remote=flag,
                job_type=job_type_arg,
                linkedin_fetch_description=True  
            )
            # if not jobs_df.empty:
            #     return self._format_dataframe(jobs_df, platform)
            if jobs_df is not None and not jobs_df.empty:
                # We no longer pass platform[0] here
                raw_jobs = self._format_dataframe(jobs_df)
                print("Scraping finished.")
                
                
                return raw_jobs
        except Exception as e:
            print(f"JobSpy Error for {platform}: {e}")
        
        return None # Signal Agent to try SerpAPI

    def get_platform_specific_fake_jobs(self, keywords, location, platform, count=1):
        """Tier 3: Platform-Specific Emergency Safety Net."""
        print(f"Generating platform-specific safety-net for {platform}...")
        
        # Configuration for specific platform 'vibes'
        configs = {
            "LinkedIn": {
                "companies": ["Microsoft", "Google", "Meta", "Apple", "Amazon"],
                "roles": ["Lead", "Director", "Senior Manager", "Principal"],
                "url": "https://www.linkedin.com/jobs"
            },
            "Indeed": {
                "companies": ["Acme Tech", "Global Systems", "InnoTech", "Digital Ventures"],
                "roles": ["Specialist", "Engineer", "Analyst", "Developer"],
                "url": "https://www.indeed.com"
            },
            "Glassdoor": {
                "companies": ["Goldman Sachs", "JP Morgan", "Stripe", "Airbnb"],
                "roles": ["Consultant", "Associate", "Engineer", "Lead"],
                "url": "https://www.glassdoor.com"
            }
        }

        # Fallback to general if platform not in list
        cfg = configs.get(platform, {
            "companies": ["Tech Corp", "Solutions Ltd"],
            "roles": ["Professional"],
            "url": "https://www.google.com/search?q=jobs"
        })

        jobs = []
        for i in range(count):
            role_suffix = cfg["roles"][i % len(cfg["roles"])]
            jobs.append({
                "title": f"{keywords} {role_suffix}",
                "company": cfg["companies"][i % len(cfg["companies"])],
                "location": location,
                "description": f"Join {cfg['companies'][i % len(cfg['companies'])]} as a {keywords} expert. Competitive salary and benefits.",
                "url": cfg["url"],
                "apply_url": cfg["url"],
                "date_posted": f"{random.randint(1, 4)} days ago",
                "platform": platform,
                "job_type": "Full-time",
                "is_real_job": False 
            })
        return jobs

    def _format_dataframe(self, df):
        """Simple formatter that uses the platform JobSpy actually found."""
        if df is None or df.empty:
            return []
        
        formatted_list = []
        for _, row in df.iterrows():
            # Get the actual site name from the scraper result (e.g., 'linkedin')
            raw_site = row.get("site", "unknown") 
            
            formatted_list.append({
                "title": row.get("title", "N/A"),
                "company": row.get("company", "N/A"),
                "location": row.get("location", "N/A"),
                "description": row.get("description", ""),
                "url": row.get("job_url", ""),
                "apply_url": row.get("job_url_direct") or row.get("job_url", ""),
                "date_posted": str(self.relative_date(row.get("date_posted",None))),
                "job_type": row.get("job_type", "N/A"),
                "platform": str(raw_site).capitalize(), # Labeled by source
                "is_real_job": True
            })
        return formatted_list
