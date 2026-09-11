from app.models.job import Job, RankedJob
import re

# app/services/rank_jobs.py

def rank_jobs(
        jobs: list,
        user_profile: dict
) -> list[dict]:
    """
    Rank jobs based on the user's preferences and requirements.
    """
    ranked_jobs = []
    
    # 1. Safely handle user profile formatting conversion
    if isinstance(user_profile, dict):
        user_profile_dict = user_profile
    elif hasattr(user_profile, "model_dump") and not isinstance(user_profile, type):
        user_profile_dict = user_profile.model_dump()
    else:
        user_profile_dict = getattr(user_profile, "__dict__", {})

    for item in jobs:
        # 🚨 THE DIRECT CATCH RULE: If the item is a class type declaration definition, skip it!
        if isinstance(item, type):
            continue

        # 2. Extract standard dictionary keys from the active node items safely
        if isinstance(item, dict):
            job_dict = item
        elif hasattr(item, "model_dump") and not isinstance(item, type):
            job_dict = item.model_dump()
        elif hasattr(item, "__dict__") and not isinstance(item, type):
            job_dict = item.__dict__
        else:
            job_dict = dict(item) if hasattr(item, "items") else {}

        # 3. If conversion resulted in an empty configuration object, discard it
        if not job_dict:
            continue

        # Execute processing scores using structural elements
        job_score = calculate_job_score(job_dict, user_profile_dict)

        # Rehydrate into model configurations safely for tracking pipelines
        try:
            if "title" not in job_dict:
                job_dict["title"] = job_dict.get("job_title") or job_dict.get("role") or "Unknown Title"
            job_obj = Job(**job_dict)
        except Exception:
            job_obj = item 

        ranked_jobs.append(RankedJob(job=job_obj, score=job_score))

    # Sort descending based on scoring metrics
    ranked_jobs.sort(key=lambda ranked_job: ranked_job.score, reverse=True)
    
    # Clear out outputs back down into standard JSON structures for graph transitions
    output_list = []
    for model in ranked_jobs:
        if hasattr(model, "model_dump") and not isinstance(model, type):
            output_list.append(model.model_dump())
        else:
            output_list.append({"job": job_dict, "score": model.score})
            
    return output_list



def calculate_job_score(job: dict, user_profile: dict) -> float:
    role_score = calculate_role_score(job, user_profile)
    skill_score = calculate_skill_score(job, user_profile)
    experience_score = calculate_experience_score(job, user_profile)
    location_score = calculate_location_score(job, user_profile)

    total_score = (
        role_score * 0.4 +
        skill_score * 0.3 +
        experience_score * 0.2 +
        location_score * 0.1
    )

    return round(total_score, 2)

def calculate_role_score(job: dict, user_profile: dict) -> float:
    target_roles = user_profile.get("target_roles", [])
    if not target_roles:
        return 0.0

    #  FIX: Look for common title naming conventions to avoid AttributeError
    job_title_raw = job.get("title") or job.get("job_title") or job.get("role") or ""
    job_title = job_title_raw.lower()
    
    role_match = any(
        role.lower() in job_title for role in target_roles
    )
    return 1.0 if role_match else 0.0

def calculate_skill_score(job: dict, user_profile: dict) -> float:
    user_skills = user_profile.get("skills", [])
    if not user_skills:
        return 0.0

    job_title_raw = job.get("title") or job.get("job_title") or job.get("role") or ""
    job_desc = job.get("description") or job.get("job_description") or ""
    
    job_text = f"{job_title_raw} {job_desc}".lower()
    
    total_matches = 0
    for skill in user_skills:
        pattern = rf"\b{re.escape(skill.lower())}\b"
        if re.search(pattern, job_text):
            total_matches += 1

    return total_matches / len(user_skills) if len(user_skills) > 0 else 0.0

def calculate_experience_score(job: dict, user_profile: dict) -> float:
    user_experience = user_profile.get("experience_years")
    if not user_experience:
        return 0.0

    job_title_raw = job.get("title") or job.get("job_title") or job.get("role") or ""
    job_desc = job.get("description") or job.get("job_description") or ""
    job_text = f"{job_title_raw} {job_desc}".lower()

    if str(user_experience).lower() in job_text:
        return 1.0
    return 0.0

def calculate_location_score(job: dict, user_profile: dict) -> float:
    preferred_locations = user_profile.get("locations", [])
    if not preferred_locations:
        return 0.0
        
    job_location = (job.get("location") or job.get("job_location") or "").lower()

    for location in preferred_locations:
        if location.lower() in job_location:
            return 1.0
            
    return 0.0
