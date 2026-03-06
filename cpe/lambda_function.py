# -*- coding: utf-8 -*-
"""
Created on Wed May 24 17:34:53 2023
Updated to save scan results to S3 as a CSV file.

@author: 11101009
"""

import nvdlib
import datetime
import pymsteams
import boto3
import json
import csv
import io

S3_BUCKET_NAME = "daily-cpe" 
S3_FILE_KEY = f"cve_reports/cve_report_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv"

# Boto3 S3 客戶端
s3_client = boto3.client("s3")

now_utc = datetime.datetime.now(datetime.timezone.utc)
start_date_for_query = now_utc - datetime.timedelta(hours=26)
end_date_for_query = now_utc
cvssV3Severity = "Critical"
apikey = "9fe446da-869a-4fa4-aadc-10a82f9d7f57"

def parse_cpe_string(cpe_str):
    """將單一 CPE 字串解析為廠商、產品和版本"""
    parts = cpe_str.strip().split(':')
    if len(parts) > 5:
        # cpe:2.3:a:vendor:product:version
        return {
            "vendor": parts[3],
            "product": parts[4],
            "version": parts[5]
        }
    return None

def write_csv_to_s3(bucket, key, data_rows):
    """
    將資料寫入記憶體中的 CSV，並上傳到 S3。
    :param bucket: S3 儲存桶名稱
    :param key: S3 中的檔案路徑/名稱
    :param data_rows: 要寫入的資料列表，每個元素為一列
    """
    try:
        string_io = io.StringIO()
        
        header = ['Vulnerability ID', 'CVSS Score', 'Description', 'CPE Vendor', 'CPE Product', 'CPE Version']
        
        writer = csv.writer(string_io)
        
        writer.writerow(header)
        writer.writerows(data_rows)
        
        s3_client.put_object(
            Bucket=bucket, 
            Key=key, 
            Body=string_io.getvalue().encode('utf-8')
        )
        print(f"Successfully wrote CSV report to s3://{bucket}/{key}")
        return True
    except Exception as e:
        print(f"Error writing to S3: {e}")
        return False


def search_cve_data(
    start_date_for_query, end_date_for_query, cvssV3Severity, apikey
):
    """
    搜尋 CVE 並將結果格式化為適合寫入 CSV 的列表。
    返回一個列表，其中每個元素都是 CSV 的一列。
    """
    print("Searching for CVEs...")
    cve_items = nvdlib.searchCVE(
        pubStartDate=now_utc - datetime.timedelta(days=30),
        pubEndDate=now_utc,
        lastModStartDate=start_date_for_query,
        lastModEndDate=end_date_for_query,
        cvssV3Severity=cvssV3Severity,
        key=apikey,
    )
    print(f"Found {len(cve_items)} CVEs to process.")
    
    # 準備用來寫入 CSV 的資料列表
    csv_data_rows = []

    for cve_item in cve_items:
        cve_id = cve_item.id
        description = cve_item.descriptions[0].value

        if hasattr(cve_item, 'v31score'):
            cvss_score = cve_item.v31score
        if hasattr(cve_item.metrics, 'cvssMetricV31'):
            for metric in cve_item.metrics.cvssMetricV31:
                if metric.source == "nvd@nist.gov":
                    cvss_score = metric.cvssData.baseScore
        if cvss_score == None:
            continue
        cpe_list = []
        if hasattr(cve_item, 'configurations'):
            for config in cve_item.configurations:
                for node in config.nodes:
                    for cpe in node.cpeMatch:
                        if cpe.vulnerable:
                            parsed_cpe = parse_cpe_string(cpe.criteria)
                            if parsed_cpe:
                                cpe_list.append(parsed_cpe)
        
        if cpe_list:
            for cpe_info in cpe_list:
                row = [
                    cve_id,
                    cvss_score,
                    description,
                    cpe_info.get('vendor', ''),
                    cpe_info.get('product', ''),
                    cpe_info.get('version', '')
                ]
                csv_data_rows.append(row)
        else:
            pass

    return csv_data_rows


def lambda_handler(event, context):
    vulnerability_rows = search_cve_data(
        start_date_for_query, end_date_for_query, cvssV3Severity, apikey
    )
    
    if vulnerability_rows:
        # 如果有資料，就寫入 S3
        print(f"Found {len(vulnerability_rows)} vulnerability entries to be saved.")
        write_csv_to_s3(S3_BUCKET_NAME, S3_FILE_KEY, vulnerability_rows)
    else:
        # 如果沒有找到任何漏洞，也發送一個通知
        print("No new vulnerabilities found to report.")

    return {"statusCode": 200, "body": json.dumps("CVE scan process completed.")}

if __name__ == "__main__":
    lambda_handler(None, None)