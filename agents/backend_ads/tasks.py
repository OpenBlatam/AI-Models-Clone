from celery import Celery
import dask
from dask.distributed import Client
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict, Any
import os
from models import AdsRequest, AdsResponse, BrandVoice, AudienceProfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Initialize Celery
celery_app = Celery('ads_processor',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

# Initialize Dask client
dask_client = Client(n_workers=4)

# Initialize LangChain
llm = OpenAI(temperature=0.7)

# Prompt template for copywriting suggestions
copywriting_prompt = PromptTemplate(
    input_variables=["brand_voice", "audience_profile", "product_description"],
    template="""
    Based on the following brand voice and audience profile, suggest compelling ad copy:
    
    Brand Voice: {brand_voice}
    Audience Profile: {audience_profile}
    Product Description: {product_description}
    
    Generate 3 different ad copy variations that would resonate with this audience.
    """
)

copywriting_chain = LLMChain(llm=llm, prompt=copywriting_prompt)

@celery_app.task(name='process_batch_ads')
def process_batch_ads(ads_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a batch of ads using Dask for parallel processing
    """
    # Convert to Dask delayed objects
    delayed_tasks = [dask.delayed(process_single_ad)(ad_request) for ad_request in ads_requests]
    
    # Compute results in parallel
    results = dask.compute(*delayed_tasks)
    return list(results)

async def process_single_ad(ad_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single ad with copywriting suggestions
    """
    # Convert dict to AdsRequest model
    request = AdsRequest(**ad_request)
    
    # Generate copywriting suggestions using LangChain
    copy_suggestions = await generate_copy_suggestions(
        request.prompt,
        request.brand_voice if hasattr(request, 'brand_voice') else None,
        request.audience_profile if hasattr(request, 'audience_profile') else None
    )
    
    # Process the ad (implement your existing ad processing logic here)
    processed_ad = {
        'original_request': ad_request,
        'copy_suggestions': copy_suggestions,
        'status': 'processed'
    }
    
    return processed_ad

async def generate_copy_suggestions(
    product_description: str,
    brand_voice: BrandVoice = None,
    audience_profile: AudienceProfile = None
) -> List[str]:
    """
    Generate copywriting suggestions using LangChain
    """
    # Convert models to string representations
    brand_voice_str = str(brand_voice.dict()) if brand_voice else "Not specified"
    audience_profile_str = str(audience_profile.dict()) if audience_profile else "Not specified"
    
    # Run the copywriting chain
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            copywriting_chain.run,
            brand_voice_str,
            audience_profile_str,
            product_description
        )
    
    # Parse and return the suggestions
    suggestions = result.split('\n\n')
    return [s.strip() for s in suggestions if s.strip()]

@celery_app.task(name='schedule_batch_processing')
def schedule_batch_processing(batch_size: int = 100):
    """
    Schedule batch processing of ads
    """
    # Implement your logic to fetch pending ads from database
    # and schedule them for processing
    pass

if __name__ == '__main__':
    celery_app.start() 