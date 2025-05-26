# Salesforce credentials can come from env-vars or hard-code here
import os
import pandas as pd, re, datetime as dt, math
from ftfy import fix_text            # better “mojibake” repair
from simple_salesforce import Salesforce
import re
import tkinter as tk
from tkinter import filedialog
SOSL_SPECIAL = r"([\\'\?\&\|\!$$\{\}$$\^\~\*\:\+\-])"   # note the hyphen last / escaped
def sosl_escape(txt:str) -> str:
    return re.sub(SOSL_SPECIAL, r"\\\1", txt)

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    return file_path
# ------------------------------------------------------------
# 2. READ + CLEAN
# ------------------------------------------------------------
def main():
    # Prompt the user to select an Excel file
    print("Please select an Excel file.")
    source_file = select_file()

    if not source_file:
        print("No file selected. Exiting.")
        return

    # Determine output file path
    source_dir = os.path.dirname(source_file)
    out_file = os.path.join(source_dir, "shortlist_enriched.xlsx")
    tmp_file = os.path.join(source_dir, "shortlist.xlsx")
    df = pd.read_excel(source_file)
    target_rows = 200
     # Prompt the user to input SID
    SID = input("Please enter your Salesforce SID: ")

    def fix_encoding(s):
        return fix_text(s) if isinstance(s, str) else s

    for col in ['First Name','Last Name','Company','Position']:
        df[col] = df[col].apply(fix_encoding)

    df['Connected On'] = pd.to_datetime(df['Connected On'], errors='coerce')

    # ------------------------------------------------------------------
    # 1. Which companies should be removed?
    #    - The word "consult" in any form
    #    - Global powerhouses
    #    - Danish / Nordic consultancies
    #    - Tech Collective (explicit request)
    # ------------------------------------------------------------------
    consultancy_patterns = [
        r'\bconsult(ant|ing|ancy)?\b',          # consult, consulting, consultancy, consultant
        # Global strategy / management
        r'mckinsey', r'\bbcg\b', r'\bbain\b', r'oliver\s*wyman', r'bearing\s*point',
        # Big-4 & Accenture
        r'accenture', r'deloitte', r'\bpwc\b', r'price\s*waterhouse', r'\bey\b', r'ernst.*young', r'\bkpmg\b',
        # IT / Tech services
        r'capgemini', r'cognizant', r'atos', r'ibm\s+services?', r'infosys', r'\btcs\b', r'wipro',
        # Danish / Nordic boutiques and midsize players
        r'implement', r'valcon', r'devoteam', r'netcompany', r'prokura',
        r'ramboll', r'niras', r'cowi', r'afry', r'atkins', r'\beg\b', r'peak\s*consulting',
        r'pa\s*consulting', r'charlie\ssierra',   # add others freely
        # Auditors that run consulting arms in DK
        r'\bbdo\b', r'grant\s*thornton',
        # Explicitly requested
        r'tech\s*collective'
    ]

    # ------------------------------------------------------------------
    # 2. Which job titles shout “consultant”?
    #    (keep it short; the company filter already catches most cases)
    # ------------------------------------------------------------------
    position_patterns = [
        r'\bconsult(ant|ing)\b',
        r'advisor|advisory',
        r'partner|associate\s*partner|principal',
        r'engagement\s*manager|project\s*(leader|manager)',
        r'case\s*team\s*leader',
        r'senior?\s*associate',
        r'\banalyst\b'
    ]

    # ------------------------------------------------------------------
    # 3. Compile and filter
    # ------------------------------------------------------------------
    company_regex  = re.compile('|'.join(consultancy_patterns),  flags=re.I)
    position_regex = re.compile('|'.join(position_patterns),     flags=re.I)

    mask_company  = df['Company'].fillna('').str.contains(company_regex)
    mask_position = df['Position'].fillna('').str.contains(position_regex)

    df_filtered = df[~(mask_company | mask_position)].copy()

    # df_filtered now contains only non-consultancy contacts

    # ------------------------------------------------------------
    # 3. SCORING
    # ------------------------------------------------------------
    C_LEVEL = r"\b(C[EO]O|CFO|CIO|CDO|CTO|CMO|CHRO|CCO|CSO)\b"
    EXEC    = r"(Administrerende direktør|Managing Director|Group CEO|EVP|Executive)"
    SVP_VP  = r"(Senior Vice President|Vice President|SVP|VP)"
    DIRECT  = r"(Director|Koncerndirektør|Direktør|Tribe|Funktionsdirektør|Afdelingsdirektør|Forretningsdirektør)"
    HEAD    = r"\b(Head|Lead|Leader|Chef)\b"

    def seniority(s):
        s = str(s)
        if re.search(C_LEVEL, s, re.I) or re.search(EXEC, s, re.I): return 5
        if re.search(SVP_VP,  s, re.I): return 4
        if re.search(DIRECT,  s, re.I): return 3
        if re.search(HEAD,    s, re.I): return 2
        return 0

    FIN = r"(Bank|Finans|Insurance|Forsikring|Asset|Pension|AML|Compliance)"
    TEC = r"(Tech|Digital|IT|Data|AI|Innovation|Software|Cyber)"

    def sector(company,title):
        blob = f"{company} {title}"
        fin, tec = bool(re.search(FIN, blob, re.I)), bool(re.search(TEC, blob, re.I))
        return 3 if fin and tec else 2 if fin or tec else 0

    today = dt.datetime.today()
    rec  = lambda d: 3 if (today-dt.timedelta(days=180))<=d<=today else \
                    2 if (today-dt.timedelta(days=365))<=d<=today else \
                    1 if (today-dt.timedelta(days=720))<=d<=today else 0

    df['Senior']   = df['Position'].apply(seniority)
    df['Sector']   = df.apply(lambda r: sector(r['Company'], r['Position']), axis=1)
    df['Recency']  = df['Connected On'].apply(lambda x: rec(x) if pd.notna(x) else 0)

    df['Score'] = 3*df['Senior'] + df['Sector'] + df['Recency'] + df['Cap']

    short = (df.sort_values(['Score','Senior','Connected On'], ascending=[False,False,False])
            .head(target_rows)
            .reset_index(drop=True))


    # ------------------------------------------------------------
    # 4. SALESFORCE ENRICHMENT
    # ------------------------------------------------------------
    print("→ Contacting Salesforce API …")
    sf = Salesforce(
            instance_url = "https://implement.my.salesforce.com",
            session_id   = SID
    )
    # --- A)  query by e-mail  ------------------------------------
    emails_have = short['Email Address'].dropna().unique().tolist()
    CONTACT_FIELDS = (
        "Id, FirstName, LastName, Email, Title, "
        "Account.Name, Owner.Name, CreatedDate, LastModifiedDate, "
        "reldata__Closest_Internal_Relationship_Email__c, "
        "reldata__Internal_Contact_Latest_Date__c"
    )
    sf_rows = []
    if emails_have:
        def chunks(lst,n):            # helper
            for i in range(0,len(lst),n): yield lst[i:i+n]

        for ch in chunks(emails_have, 1000):
            emails_sql = ",".join("'" + e.replace("'", r"\'") + "'" for e in ch)
            soql = f"SELECT {CONTACT_FIELDS} FROM Contact WHERE Email IN ({emails_sql})"
            sf_rows.extend(sf.query_all(soql)['records'])

    # keep track of which names we already matched by email
    matched_by_email = {(c['FirstName'].lower(), c['LastName'].lower()) for c in sf_rows}

    # ------------------------------------------------------------
    # helper: escape special chars
    # ------------------------------------------------------------
    SOSL_SPECIAL = r"([\\'\?\&\|\!$$\{\}$$\^\~\*\:\+\-])"
    def sosl_escape(txt):         # for SOSL
        import re
        return re.sub(SOSL_SPECIAL, r"\\\1", txt)

    def soql_escape(txt):         # for SOQL
        return str(txt).replace("'", r"\'")

    # ------------------------------------------------------------
    # --- B)  fallback: name look-up tolerant to wrong split ------
    # ------------------------------------------------------------
    need_name_lookup = short[short['Email Address'].isna()]

    for _, row in need_name_lookup.iterrows():
        raw_first = str(row['First Name']).strip()
        raw_last  = str(row['Last Name']).strip()
        if raw_first=='Søren':
            print(1)
        

        # build token list once
        tokens = (raw_first + " " + raw_last).split()
        if len(tokens) < 2:
            continue                # nothing to split

        # prepare split variants  (first | rest, first+mid | last, etc.)
        variants = []
        # 1) every front split as before
        variants.extend(
            ( " ".join(tokens[:k]), " ".join(tokens[k:]), None )   # None = no middle constraint
            for k in range(1, len(tokens))
        )
        # 2) dedicated middle-name variant: first token / last token + middle in-between
        if len(tokens) >= 3:
            fn  = tokens[0]
            ln  = tokens[-1]
            mid = " ".join(tokens[1:-1])
            variants.insert(0, (fn, ln, mid))     # try this one first

        record_found = None
        for fn, ln, mid in variants:
            key = (fn.lower(), ln.lower())
            if key in matched_by_email:           # already matched earlier
                record_found = True
                break

            # build SOQL
            soql_parts = [
                "SELECT Id, FirstName, LastName, MiddleName, Email, Title, "
                "       Account.Name, Owner.Name, CreatedDate, LastModifiedDate, reldata__Closest_Internal_Relationship_Email__c, reldata__Internal_Contact_Latest_Date__c "
                "FROM   Contact WHERE "
                f"FirstName = '{soql_escape(fn)}' AND "
                f"LastName  = '{soql_escape(ln)}'"
            ]
            if mid:                               # middle-name constraint when we have one
                soql_parts.append(f" AND MiddleName = '{soql_escape(mid)}'")
            soql_parts.append(" LIMIT 1")
            soql = "".join(soql_parts)

            res = sf.query(soql)["records"]
            if res:
                record_found = res[0]
                break

        # nothing yet → SOSL fuzzy across all name fields
        if record_found is None:
            term = sosl_escape(" ".join(tokens))
            sosl = (
                f"FIND {{{term}}} IN NAME FIELDS RETURNING "
                "Contact(Id, FirstName, LastName, MiddleName, Email, Title, "
                "        Account.Name, Owner.Name, CreatedDate, LastModifiedDate, reldata__Closest_Internal_Relationship_Email__c, reldata__Internal_Contact_Latest_Date__c "
                "        LIMIT 1)"
            )
            recs = sf.search(sosl).get("searchRecords", [])
            record_found = recs[0] if recs else None

        if isinstance(record_found, dict):
            sf_rows.append(record_found)


    # ---------------------------------------------------
    # 4e)  AGGREGATE TASK + EVENT INTERACTIONS
    # ---------------------------------------------------
    # build a DataFrame of the 150 contacts + their Salesforce Ids
    enriched = pd.json_normalize(sf_rows)
    enriched = enriched.rename(columns={
        'reldata__Closest_Internal_Relationship_Email__c':
            'StrongestRelationshipEmail',
        'reldata__Internal_Contact_Latest_Date__c':
            'InternalLatestDate'
    })
    enriched['InternalLatestDate'] = pd.to_datetime(
            enriched['InternalLatestDate'], errors='coerce'
    )
    today = pd.Timestamp.today().normalize()
    enriched['DaysSinceInternalTouch'] = (
            today - enriched['InternalLatestDate']
    ).dt.days
    # make sure the SF Id column is called exactly 'Id'
    if 'Id' not in enriched.columns:
        # simple-salesforce returns 'Id'; but if you renamed it earlier, undo that:
        if 'ContactId' in enriched.columns:
            enriched = enriched.rename(columns={'ContactId': 'Id'})
        elif 'Contact.Id' in enriched.columns:
            enriched = enriched.rename(columns={'Contact.Id': 'Id'})
        else:
            # create an empty Id column so the merge still works
            enriched['Id'] = pd.NA

    # keep only the columns you need
    enriched = enriched[['Id', 'FirstName', 'LastName', 'MiddleName','Email',
                        'Title', 'Account.Name', 'Owner.Name',
                        'CreatedDate', 'StrongestRelationshipEmail', 'DaysSinceInternalTouch', 'InternalLatestDate']]
    ids = enriched['Id'].dropna().unique().tolist()

    # helper to run aggregate SOQL in chunks
    def agg_query(sobject: str,
                alias_date: str,
                alias_cnt: str,
                id_list: list[str]) -> pd.DataFrame:
        """
        sobject     : 'Task'  or 'Event'
        alias_date  : column name to hold MAX(CreatedDate)
        alias_cnt   : column name to hold COUNT(Id)
        id_list     : list of Contact Ids to aggregate for
        returns     : DataFrame with columns  [Id, alias_date, alias_cnt]
        """

        rows = []

        # query in chunks (SOQL IN-list limit = 2000; we stay at 200)
        for chunk in chunks(id_list, 200):
            ids_sql = ",".join(f"'{cid}'" for cid in chunk)

            soql = (
                f"SELECT  WhoId, "
                f"        MAX(CreatedDate) {alias_date}, "
                f"        COUNT(Id)        {alias_cnt} "
                f"FROM    {sobject} "
                f"WHERE   WhoId IN ({ids_sql}) "
                f"GROUP   BY WhoId"
            )

            rows.extend(sf.query_all(soql)["records"])

        # turn API rows into DataFrame
        df_tmp = pd.json_normalize(rows)

        if df_tmp.empty:
            # create an empty frame with the right columns
            df_tmp = pd.DataFrame(columns=["Id", alias_date, alias_cnt])
        else:
            df_tmp = (
                df_tmp.rename(columns={"WhoId": "Id"})
                    .loc[:, ["Id", alias_date, alias_cnt]]
            )

        # make sure the two value columns always exist
        if alias_date not in df_tmp.columns:
            df_tmp[alias_date] = pd.NaT
        if alias_cnt not in df_tmp.columns:
            df_tmp[alias_cnt] = 0

        return df_tmp

    df_tasks  = agg_query("Task",  "LastTaskDate",  "TaskCount",ids)
    df_events = agg_query("Event", "LastEventDate", "EventCount",ids)

    rel = df_tasks.merge(df_events, on='Id', how='outer')

    # 1) make the two date columns exist & become datetime
    for col in ['LastTaskDate', 'LastEventDate']:
        if col not in rel.columns:
            rel[col] = pd.NaT
        rel[col] = pd.to_datetime(rel[col], errors='coerce')

    # 2) make the count columns exist & be nullable integers
    for col in ['TaskCount', 'EventCount']:
        if col not in rel.columns:
            rel[col] = 0
        rel[col] = rel[col].fillna(0).astype('Int64')

    # 3) compute latest interaction per row (works even with all-NaT)
    rel['LastInteractionDate'] = rel.apply(
        lambda r: max(r['LastTaskDate'], r['LastEventDate']), axis=1
    )

    rel['InteractionsLast12m'] = rel['TaskCount'] + rel['EventCount'] # you may refine to only count recent ones with a WHERE clause

    # ---------------------------------------------------
    # 4f)  FINAL MERGE
    # ---------------------------------------------------
    def normalise_name(*parts):
        """lower-case, strip accents if you like, drop all whitespace"""
        import re, unidecode
        txt = " ".join(filter(None, parts))          # concat non-None tokens
        txt = unidecode.unidecode(txt)               # Å → A  (pip install Unidecode)
        txt = txt.lower()
        txt = re.sub(r"\s+", "", txt)                # kill all spaces
        return txt

    # key for the shortlist (sheet)
    short['LookupKey'] = short.apply(
        lambda r: normalise_name(r['First Name'], r['Last Name']),
        axis=1
    )

    # key for the SF enrichment; include MiddleName if present
    enriched['LookupKey'] = enriched.apply(
        lambda r: normalise_name(r.get('FirstName'),
                                r.get('MiddleName'),   # may be NaN
                                r.get('LastName')),
        axis=1
    )



    # ------------------------------------------------------------------
    #  B)  merge on that key instead of separate columns
    # ------------------------------------------------------------------
    merged = (short
            .merge(enriched, how='left', on='LookupKey', suffixes=('', '_SF'))
            .merge(rel,      how='left', on='Id'))

    # optional: drop the helper column afterwards
    merged.drop(columns='LookupKey', inplace=True)
    # ------------------------------------------------------------
    # 5.  OUTPUT  – add “days since last contact”
    # ------------------------------------------------------------
    # instead of pd.Timestamp.today().normalize()
    TODAY = pd.Timestamp.now(tz='UTC').normalize()


    cols = ['First Name','Last Name','Company','Position',
            'Connected On','Score',
            'Id',
            'StrongestRelationshipEmail','InternalLatestDate','DaysSinceInternalTouch',
            'InteractionsLast12m']


    for col in merged.select_dtypes(include=["datetimetz"]).columns:
        merged[col] = merged[col].dt.tz_localize(None)

    # now export
    merged[cols].to_excel(out_file, index=False)
    print(f"✅  Saved enriched shortlist to {out_file}")

if __name__ == "__main__":
    main()