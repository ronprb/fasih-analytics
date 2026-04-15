import pandas as pd
import asyncio
import argparse
import os
import time
from importer import get_cookies_and_csrf, get_payload, COOKIE_CACHE_PATH
from config import BASE_HEADERS, payload_survey, report_progress_assignment_url, report_user_assignment_url, progress_status_order, assignment_status_order, pemutakhiran_base_url, pemutakhiran_payload, pemutakhiran_status_order
from api_client import post_requests, get_requests
from adjust_survey import adjust_period, adjust_sample, adjust_deadline
from transformer import json_to_df, pemutakhiran_json_to_df
from data_loader import get_survey_name
from plotter import generate_plots_2
from survey_selector import select_surveys
from generate_pivot import main as generate_pivot

async def main():
    os.makedirs("outputs/csv", exist_ok=True)
    start_time = time.time()

    cookies, csrf_token = get_cookies_and_csrf()
    headers = {**BASE_HEADERS, "X-XSRF-TOKEN": csrf_token}

    # Fetch survey list (POST)
    url = "https://fasih-sm.bps.go.id/survey/api/v1/surveys/datatable?surveyType=Pencacahan"
    response = await post_requests(url, headers, cookies, payload_survey)
    json_data = response.json()

    survey_collection_df = pd.DataFrame(json_data['data']['content'])

    # Let user pick which surveys to scrape and tag their type
    survey_config = await select_surveys(survey_collection_df['name'].tolist())
    selected_names = [e['name'] for e in survey_config]
    pencacahan_names = [e['name'] for e in survey_config if e['type'] == 'pencacahan']
    pemutakhiran_names = [e['name'] for e in survey_config if e['type'] == 'pemutakhiran']

    survey_collection_df = survey_collection_df[
        survey_collection_df['name'].isin(selected_names)
    ].reset_index(drop=True)

    survey_id_dict = {i: j for i, j in zip(survey_collection_df['id'], survey_collection_df['name'])}

    semaphore = asyncio.Semaphore(10)

    # Load previously saved survey collection to compare dates
    _prev_csv = "outputs/csv/survey_collection_deadline_adjusted.csv"
    prev_survey_df = pd.read_csv(_prev_csv) if os.path.exists(_prev_csv) else pd.DataFrame()
    date_changes = []

    def fmt(d):
        try:
            return pd.to_datetime(d).strftime('%d %b %Y')
        except:
            return str(d)

    # Fetch metadata (GET) concurrently
    surveys_base_url = "https://fasih-sm.bps.go.id/survey/api/v1/surveys/"
    survey_periods_url = "https://fasih-sm.bps.go.id/survey/api/v1/survey-periods/my?surveyId="

    async def fetch_metadata(i, j):
        async with semaphore:
            try:
                survey_response, periods_response = await asyncio.gather(
                    get_requests(surveys_base_url + str(i), headers=headers, cookies=cookies),
                    get_requests(survey_periods_url + str(i), headers=headers, cookies=cookies),
                )
                survey_data = survey_response.json()["data"]
                periods = periods_response.json()["data"]
                latest_period = periods[-1]

                new_start = latest_period["startDate"]
                new_end = latest_period["endDate"]

                survey_collection_df.loc[
                    survey_collection_df["id"] == i,
                    ["regionGroupId", "survey_period_id", "startDate", "endDate"]
                ] = [
                    survey_data["regionGroupId"],
                    latest_period["id"],
                    new_start,
                    new_end,
                ]

                # Collect date changes to print in summary later
                if not prev_survey_df.empty and 'name' in prev_survey_df.columns:
                    prev_row = prev_survey_df[prev_survey_df['name'] == j]
                    if not prev_row.empty:
                        old_start = prev_row['startDate'].values[0]
                        old_end = prev_row['endDate'].values[0]
                        if str(old_start) != str(new_start) or str(old_end) != str(new_end):
                            date_changes.append((j, old_start, old_end, new_start, new_end))

                print(f"✅ Status 200 | {j}")
            except Exception as e:
                print(f"❌ Error for {j}: {e}")

    # Run all metadata requests concurrently
    tasks = [fetch_metadata(i, j) for i, j in survey_id_dict.items()]
    await asyncio.gather(*tasks)

    # Update period and save
    try:
        survey_collection_df = adjust_period(survey_collection_df)
    except Exception as e:
        print(f"⚠️ adjust_period() failed: {e}")
        # You could log the traceback if needed
        import traceback
        traceback.print_exc()
    finally:
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        survey_collection_df.to_csv(f"outputs/csv/survey_collection_{timestamp}.csv", index=False)
        print("\n📁 Data saved to output folder.\n")

    # Get province sample for each survey asynchronously with semaphore
    prov_sampel = {}

    async def fetch_prov_sample(surveyPeriodId):
        async with semaphore:
            url = "https://fasih-sm.bps.go.id/survey/api/v1/users/myinfo?surveyPeriodId=" + surveyPeriodId
            response = await get_requests(url, headers, cookies)
            json_data = response.json()['data']
            groupId = survey_collection_df.loc[survey_collection_df['survey_period_id']==surveyPeriodId, 'regionGroupId']
            prov_sampel[surveyPeriodId] = json_data['regionId']
            print(f"Survey Period ID: {surveyPeriodId}, Group ID: {groupId.values[0]}, Region ID: {json_data['regionId']}")

    pencacahan_period_ids = survey_collection_df.loc[
        survey_collection_df['name'].isin(pencacahan_names), 'survey_period_id'
    ].tolist()
    prov_tasks = [fetch_prov_sample(surveyPeriodId) for surveyPeriodId in pencacahan_period_ids]
    await asyncio.gather(*prov_tasks)

    rows = []

    # Fetch region1_id concurrently with semaphore
    async def fetch_region1_id(surveyPeriodId, prov_id):
        async with semaphore:
            groupId = survey_collection_df.loc[survey_collection_df['survey_period_id'] == surveyPeriodId, 'regionGroupId'].iloc[0]
            url = "https://fasih-sm.bps.go.id/region/api/v1/region/level1?groupId=" + groupId
            response = await get_requests(url, headers=headers, cookies=cookies)
            json_data = response.json()
            level1_df = pd.DataFrame(json_data['data'])
            region1_id = level1_df.loc[level1_df['fullCode'] == prov_id, 'id'].iloc[0]
            print(f"Processed survey period ID {surveyPeriodId}: {prov_id} - Region 1 ID: {region1_id}")
            return {
                'surveyPeriodId': surveyPeriodId,
                'prov_id': prov_id,
                'region1Id': region1_id
            }

    region1_tasks = []
    for surveyPeriodId, prov_list in prov_sampel.items():
        if prov_list is None:
            continue
        for prov_id in prov_list:
            region1_tasks.append(fetch_region1_id(surveyPeriodId, prov_id))
    region1_results = await asyncio.gather(*region1_tasks)
    rows.extend(region1_results)

    temp_df = pd.DataFrame(rows)


    urls = [report_progress_assignment_url, report_user_assignment_url]
    report_assignment_df = pd.DataFrame()

    async def fetch_progress_assignment(rowx, url):
        async with semaphore:
            await asyncio.sleep(0.3)
            region1Id = rowx['region1Id']
            surveyPeriodId = rowx['surveyPeriodId']
            prov_id = rowx.get('prov_id', 'unknown')
            survey_name = get_survey_name(survey_collection_df, surveyPeriodId)

            try:
                payload = get_payload(region1Id, surveyPeriodId)
                response = await post_requests(url, headers, cookies, payload)
                print(f"Status {response.status_code} | {survey_name} - {prov_id}")

                if response.status_code != 200:
                    print(f"❌ Failed for {survey_name}, {prov_id}")
                    return None

                tab = json_to_df(response.json(), prov_id, survey_name)
                tab["type"] = "user_assignment" if url == report_user_assignment_url else "progress"
                return tab

            except Exception as e:
                print(f"❗Error processing {survey_name} ({prov_id}): {e}")
                return None

    # Run both URLs concurrently — each URL has its own rate limit so interleaving reduces per-URL burst
    print(f"\n🚀 Fetching data from {urls[0]} and {urls[1]} concurrently...")
    report_tasks = [
        fetch_progress_assignment(rowx, url)
        for url in urls
        for _, rowx in temp_df.iterrows()
    ]
    report_results = await asyncio.gather(*report_tasks)
    report_results = [r for r in report_results if r is not None]
    if report_results:
        report_assignment_df = pd.concat([report_assignment_df, *report_results], ignore_index=True)

    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    # Adjustment for Sampel and Deadlines
    try:
        report_assignment_df = adjust_sample(report_assignment_df)
        survey_collection_df = adjust_deadline(survey_collection_df)
    except Exception as e:
        print(f"⚠️ Adjustment step failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        report_assignment_df.to_csv(f"outputs/csv/report_assignment_{timestamp}.csv", index=False)
        report_assignment_df.to_csv(f"outputs/csv/report_assignment.csv", index=False)
        survey_collection_df.to_csv(f"outputs/csv/survey_collection_deadline_adjusted.csv", index=False)
        print(f"\n📁 Data saved to output folder.\n")

    # Pemutakhiran flow
    report_pemutakhiran_df = pd.DataFrame()
    if pemutakhiran_names:
        print("\n🚀 Fetching pemutakhiran data...")

        async def fetch_pemutakhiran(survey_name, survey_period_id):
            async with semaphore:
                url = pemutakhiran_base_url + survey_period_id
                try:
                    response = await post_requests(url, headers, cookies, pemutakhiran_payload)
                    print(f"Status {response.status_code} | {survey_name}")
                    if response.status_code != 200:
                        print(f"❌ Failed pemutakhiran: {survey_name}")
                        return None
                    data = response.json().get('data', [])
                    tab = pemutakhiran_json_to_df(data, survey_name)
                    return tab
                except Exception as e:
                    print(f"❗ Error pemutakhiran {survey_name}: {e}")
                    return None

        pemutakhiran_rows = survey_collection_df[
            survey_collection_df['name'].isin(pemutakhiran_names)
        ][['name', 'survey_period_id']].itertuples(index=False)

        pemutakhiran_tasks = [
            fetch_pemutakhiran(row.name, row.survey_period_id)
            for row in pemutakhiran_rows
        ]
        pemutakhiran_results = await asyncio.gather(*pemutakhiran_tasks)
        pemutakhiran_results = [r for r in pemutakhiran_results if r is not None]
        if pemutakhiran_results:
            report_pemutakhiran_df = pd.concat(pemutakhiran_results, ignore_index=True)
            report_pemutakhiran_df.to_csv(f"outputs/csv/report_pemutakhiran_{timestamp}.csv", index=False)
            print(f"\n📁 Pemutakhiran data saved.\n")

    # Always overwrite the canonical pemutakhiran CSV so stale data from a
    # previous run never leaks into the pivot report on the next run.
    report_pemutakhiran_df.to_csv("outputs/csv/report_pemutakhiran.csv", index=False)

    # Plot combined chart (pencacahan + pemutakhiran together)
    survey_collection_df = pd.read_csv('outputs/csv/survey_collection_deadline_adjusted.csv')
    combined_progress_df = pd.DataFrame()

    if pencacahan_names:
        report_assignment_df = pd.read_csv('outputs/csv/report_assignment.csv')
        progress_assignment_df = report_assignment_df[report_assignment_df['type'] == "progress"].copy()
        user_assignment_df = report_assignment_df[report_assignment_df['type'] != "progress"].copy()
        combined_progress_df = pd.concat([combined_progress_df, progress_assignment_df], ignore_index=True)
        generate_plots_2(user_assignment_df, survey_collection_df, assignment_status_order, 2, pencacahan_names)

    if not report_pemutakhiran_df.empty:
        combined_progress_df = pd.concat([combined_progress_df, report_pemutakhiran_df], ignore_index=True)

    if not combined_progress_df.empty:
        combined_status_order = progress_status_order + pemutakhiran_status_order
        generate_plots_2(combined_progress_df, survey_collection_df, combined_status_order, 1, selected_names)



    generate_pivot()

    if date_changes:
        print("\n📋 Survey Period Changes:")
        for name, old_start, old_end, new_start, new_end in date_changes:
            print(f"  • {name}")
            print(f"    {fmt(new_start)} – {fmt(new_end)}  →  {fmt(old_start)} – {fmt(old_end)}")

    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n⏱️  Scraping completed in {minutes}m {seconds}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--relogin", action="store_true", help="Force fresh login, ignoring cached session")
    parser.add_argument("--title", type=str, help="Set the primary chart title (saved for future runs)")
    parser.add_argument("--user-title", type=str, help="Set the user assignment chart title (saved for future runs)")
    args = parser.parse_args()

    if args.relogin and os.path.exists(COOKIE_CACHE_PATH):
        os.remove(COOKIE_CACHE_PATH)
        print("🗑️  Cached session cleared.\n")

    if args.title or args.user_title:
        import json
        from survey_selector import CONFIG_PATH
        cfg = json.load(open(CONFIG_PATH)) if os.path.exists(CONFIG_PATH) else {}
        if args.title:
            cfg["chart_title"] = args.title
            print(f"📝 Chart title set to: {args.title}\n")
        if args.user_title:
            cfg["user_assignment_title"] = args.user_title
            print(f"📝 User assignment title set to: {args.user_title}\n")
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

    asyncio.run(main())