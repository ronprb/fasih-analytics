import asyncio
import pandas as pd
from api_client import post_requests

async def fetch_progress_row(rowx, survey_collection_df, headers, cookies, report_url, get_survey_name, get_payload, json_to_df):
    region1Id = rowx['region1Id']
    surveyPeriodId = rowx['surveyPeriodId']
    prov_id = rowx.get('prov_id', 'unknown')
    survey_name = get_survey_name(survey_collection_df, surveyPeriodId)
    payload = get_payload(region1Id, surveyPeriodId)
    
    try:
        response = await post_requests(report_url, headers, cookies, payload)
        print(f"✅ Status {response.status_code} | {survey_name} - {prov_id}")
        return json_to_df(response.json(), prov_id, survey_name)
    except Exception as e:
        print(f"❌ Error processing {survey_name} ({prov_id}): {e}")
        return None

async def run_parallel_requests(temp_df, survey_collection_df, headers, cookies, report_url, get_survey_name, get_payload, json_to_df):
    tasks = [
        fetch_progress_row(row, survey_collection_df, headers, cookies, report_url, get_survey_name, get_payload, json_to_df)
        for _, row in temp_df.iterrows()
    ]
    results = await asyncio.gather(*tasks)
    # Filter out None and concatenate
    progress_assignment_df = pd.concat([r for r in results if r is not None], ignore_index=True)
    return progress_assignment_df