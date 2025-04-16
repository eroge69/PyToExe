import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

def xml_to_dataframe(xml_file_path):
    # XML 파일 읽기
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_string = file.read()
    # UTF-8 BOM 제거
    if xml_string.startswith('\ufeff'):
        xml_string = xml_string[1:]
    # XML이 여러 <어휘항목>을 포함하므로 임시 루트 추가
    root = ET.fromstring("<root>" + xml_string + "</root>")
    rows = []
    max_example = 0  # 최대 번역용례 개수 파악
    
    for 항목 in root.findall("어휘항목"):
        base = {}
        # 어휘항목의 식별자 attribute
        base["식별자"] = 항목.get("식별자")
        # 기본 태그: 문헌명, 항목, 음가, 속성, 어의, 어의보충 (어의보충은 없으면 빈 문자열)
        for tag in ["문헌명", "항목", "음가", "속성", "어의", "어의보충"]:
            el = 항목.find(tag)
            base[tag] = el.text.strip() if (el is not None and el.text) else ""
            
        # 번역용례 처리: 여러 <용례>가 있을 수 있음
        예목록 = []
        번역용례_elem = 항목.find("번역용례")
        if 번역용례_elem is not None:
            for 예 in 번역용례_elem.findall("용례"):
                ex = {
                    "용례 식별자": 예.get("식별자"),
                    "출전정보": 예.findtext("출전정보").strip() if 예.find("출전정보") is not None and 예.findtext("출전정보") else "",
                    "원문": 예.findtext("원문").strip() if 예.find("원문") is not None and 예.findtext("원문") else "",
                    "번역문": 예.findtext("번역문").strip() if 예.find("번역문") is not None and 예.findtext("번역문") else ""
                }
                예목록.append(ex)
        base["번역용례"] = 예목록
        max_example = max(max_example, len(예목록))
        
        # 참조사전: 여러 <사전> 태그의 텍스트를 '; '로 결합
        참조사전목록 = [c.text.strip() for c in 항목.findall("./참조사전/사전") if c.text]
        base["참조사전"] = "; ".join(참조사전목록)
        
        rows.append(base)
        
    # DataFrame 생성: MultiIndex 컬럼 구성
    df_rows = []
    for item in rows:
        d = {}
        # 기본 정보 (식별자, 문헌명, 항목, 음가, 속성, 어의, 어의보충)
        d[("기본", "식별자")] = item["식별자"]
        for tag in ["문헌명", "항목", "음가", "속성", "어의", "어의보충"]:
            d[("기본", tag)] = item[tag]
        # 번역용례는 최대 max_example 개 만큼 확장 (없으면 NaN 처리)
        for i in range(1, max_example+1):
            if i <= len(item["번역용례"]):
                ex = item["번역용례"][i-1]
                d[(f"번역용례{i}", "용례 식별자")] = ex["용례 식별자"]
                d[(f"번역용례{i}", "출전정보")] = ex["출전정보"]
                d[(f"번역용례{i}", "원문")] = ex["원문"]
                d[(f"번역용례{i}", "번역문")] = ex["번역문"]
            else:
                d[(f"번역용례{i}", "용례 식별자")] = np.nan
                d[(f"번역용례{i}", "출전정보")] = np.nan
                d[(f"번역용례{i}", "원문")] = np.nan
                d[(f"번역용례{i}", "번역문")] = np.nan
        # 참조사전
        d[("참조사전", "사전")] = item["참조사전"]
        df_rows.append(d)
        
    df = pd.DataFrame(df_rows)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df

# ──────────────────────────────────────────────
# 샘플 XML 파일 경로 (어의보충 포함)
xml_data = r"C:\Users\kaien\Downloads\REPOSITORY\private725\LX2024\tools\어휘속성작업물(논어주소1).xml"

# DataFrame 변환 실행
df = xml_to_dataframe(xml_data)
print("MultiIndex DataFrame:")
print(df)
