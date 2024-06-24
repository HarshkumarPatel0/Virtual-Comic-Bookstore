import sys
from pprint import pprint
import os
import psutil
import re
from models import *
from encode import pack, unpack, tables

MODELS = {
    "gcd_brand": Brand.fromGCD,
    "gcd_creator": Creator.fromGCD,
    "gcd_publisher": Publisher.fromGCD,
    "gcd_indicia_publisher": IndiciaPublisher.fromGCD,
    "gcd_series": Series.fromGCD,
    "gcd_issue": Comic.fromGCD,
    "gcd_story": Story.fromGCD,
    "gcd_feature": Feature.fromGCD,
}

strings = {}

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*")

def exists(table, id):
    return tables[table]["data"].get(id)

def extract(values):
    values = values.replace('\\"', '"')
    data = []
    pos = 0
    while pos < len(values):
        ch = values[pos]
        if ch.isdigit() or ch == "-":
            comma = values.find(",", pos)
            if comma < 0:
                comma = len(values)
            num = values[pos:comma]
            if "." in num:
                data.append(float(num))
            else:
                data.append(int(num))
            pos = comma + 1
        elif ch == "'":
            curr = pos + 1
            while True:
                curr = values.find("'", curr)
                if values[curr-1] != "\\":
                    break
                context = values[curr-2:curr+3]
                if values[curr-2] == "\\":
                    values = values[:curr - 1] + values[curr:]
                    curr -= 1
                    break
                else:
                    values = values[:curr-1] + values[curr:]

            value = values[pos+1:curr]
            if not TIMESTAMP.match(value):
                data.append(value)
            pos = curr + 2
        elif ch == "N":
            data.append(None)
            pos += 5
        else:
            print(values, file=sys.stderr)
            raise Exception(f"Values:{values}")
    return data

#print(extract(r"371386,'16','',0,0,26214,1289,0,NULL,1,'[1971]','1971-00-00',315225,'0,80 NLG; 12 BEF',36.000,0,'verschijnen eenmaal per drie maanden',0,'?',0,'\\','2007-08-25 00:00:00','2021-08-01 09:59:37',0,1,'','',0,NULL,'','',0,'',0,'1971',0,'',0,0,0"))

def stddata_country(values):
    if values[1] in {"au", "ca", "gb", "ie", "nz", "us"}:
        return values

def stddata_language(values):
    if values[1] in {"en", "zxx"}:
        return values

def stddata_date(values):
    if values[1] or values[2] or values[3]:
        return values

def stddata_script(values):
    if values[1] in {"Latn"}:
        return values

def gcd_story_type(values):
    return values

def gcd_reprint(values):
    return values

def gcd_brand_emblem_group(values):
    return
    #return values

def gcd_brand_use(values):
    return
    #return values

def gcd_series_bond(values):
    return
    #return values

def gcd_series_bond_type(values):
    return
    #return values

def gcd_series_publication_type(values):
    return
    #return values

def taggit_tag(values):
    return
    #return values

def taggit_taggeditem(values):
    return
    #if values[3] in {13, 127, 147}:
    #    return values

def django_content_type(values):
    return

def gcd_name_type(values):
    return values

def gcd_relation_type(values):
    return values

def gcd_school(values):
    return

def gcd_degree(values):
    return

def gcd_membership_type(values):
    return

def gcd_non_comic_work_role(values):
    return

def gcd_non_comic_work_type(values):
    return

def gcd_non_comic_work_year(values):
    return

def gcd_feature_type(values):
    return values

def gcd_feature_relation_type(values):
    return

def gcd_feature_logo_2_feature(values):
    return values

def gcd_credit_type(values):
    return values

def gcd_story_feature_logo(values):
    return values

def gcd_story_feature_object(values):
    return values

def gcd_biblio_entry(values):
    return values

def gcd_creator_relation_creator_name(values):
    return values

def gcd_creator_signature(values):
    return values

def gcd_issue_indicia_printer(values):
    return

def gcd_publisher(values):
    if not exists("stddata_country", values[2]):
        return
    return values

def gcd_brand_group(values):
    if not exists("gcd_publisher", values[9]):
        return
    return values

def gcd_brand(values):
    return values

def gcd_indicia_publisher(values):
    if not exists("stddata_country", values[3]):
        return
    return values

def gcd_series(values):
    if not exists("gcd_publisher", values[12]) or not exists("stddata_country", values[13]) or not exists(
            "stddata_language", values[14]):
        return
    return values

def gcd_issue(values):
    if not exists("gcd_series", values[5]):
        return
    return values

def gcd_story(values):
    if not exists("gcd_issue", values[6]):
        return
    return values

def gcd_story_credit(values):
    if not exists("gcd_story", values[10]):
        return
    return values

def gcd_feature(values):
    if not exists("stddata_language", values[9]):
        return
    return values

def gcd_award(values):
    return

def gcd_received_award(values):
    return

def gcd_creator(values):
    return values

def gcd_creator_art_influence(values):
    return

def gcd_creator_degree(values):
    return

def gcd_creator_membership(values):
    return

def gcd_creator_name_detail(values):
    return values

def gcd_creator_non_comic_work(values):
    return

def gcd_creator_relation(values):
    return

def gcd_creator_school(values):
    return

def gcd_feature_logo(values):
    return values

def gcd_indicia_printer(values):
    return

def gcd_issue_credit(values):
    if not exists("gcd_issue", values[8]):
        return
    return values

def gcd_printer(values):
    return

def default(values):
    print(values)

def ignore(data):
    pass

CREATE = {
    "stddata_country": stddata_country,
    "stddata_language": stddata_language,
    "stddata_date": stddata_date,
    "stddata_script": stddata_script,
    "gcd_story_type": gcd_story_type,
    "gcd_reprint": gcd_reprint,
    "gcd_brand_emblem_group": gcd_brand_emblem_group,
    "gcd_brand_use": gcd_brand_use,
    "gcd_series_bond": gcd_series_bond,
    "gcd_series_bond_type": gcd_series_bond_type,
    "gcd_series_publication_type": gcd_series_publication_type,
    "taggit_tag": taggit_tag,
    "taggit_taggeditem": taggit_taggeditem,
    "django_content_type": django_content_type,
    "gcd_name_type": gcd_name_type,
    "gcd_relation_type": gcd_relation_type,
    "gcd_school": gcd_school,
    "gcd_degree": gcd_degree,
    "gcd_membership_type": gcd_membership_type,
    "gcd_non_comic_work_role": gcd_non_comic_work_role,
    "gcd_non_comic_work_type": gcd_non_comic_work_type,
    "gcd_non_comic_work_year": gcd_non_comic_work_year,
    "gcd_feature_type": gcd_feature_type,
    "gcd_feature_relation_type": gcd_feature_relation_type,
    "gcd_feature_logo_2_feature": gcd_feature_logo_2_feature,
    "gcd_credit_type": gcd_credit_type,
    "gcd_story_feature_logo": gcd_story_feature_logo,
    "gcd_story_feature_object": gcd_story_feature_object,
    "gcd_biblio_entry": gcd_biblio_entry,
    "gcd_creator_relation_creator_name": gcd_creator_relation_creator_name,
    "gcd_creator_signature": gcd_creator_signature,
    "gcd_issue_indicia_printer": gcd_issue_indicia_printer,
    "gcd_publisher": gcd_publisher,
    "gcd_brand_group": gcd_brand_group,
    "gcd_brand": gcd_brand,
    "gcd_indicia_publisher": gcd_indicia_publisher,
    "gcd_series": gcd_series,
    "gcd_issue": gcd_issue,
    "gcd_story": gcd_story,
    "gcd_story_credit": gcd_story_credit,
    "gcd_feature": gcd_feature,
    "gcd_award": gcd_award,
    "gcd_received_award": gcd_received_award,
    "gcd_creator": gcd_creator,
    "gcd_creator_art_influence": gcd_creator_art_influence,
    "gcd_creator_degree": gcd_creator_degree,
    "gcd_creator_membership": gcd_creator_membership,
    "gcd_creator_name_detail": gcd_creator_name_detail,
    "gcd_creator_non_comic_work": gcd_creator_non_comic_work,
    "gcd_creator_relation": gcd_creator_relation,
    "gcd_creator_school": gcd_creator_school,
    "gcd_feature_logo": gcd_feature_logo,
    "gcd_indicia_printer": gcd_indicia_printer,
    "gcd_issue_credit": gcd_issue_credit,
    "gcd_printer": gcd_printer
}

def gen():
    n = 0
    for table in MODELS:
        fromGCD = MODELS[table]
        for key, packed in tables[table]["data"].items():
            values = unpack(packed)
            #print(table, key, values)
            yield n
            n += 1
            instance = fromGCD(values, tables)
            if instance:
                tables[table]["data"][key] = instance


def main(args):
    define = []
    table = None

    convert = ignore

    with open(args[1], encoding="utf-8") as f:
        for n, line in enumerate(f):
            if line.startswith("CREATE TABLE"):
                table = line.split("`")[1]
                define = [line]
                continue
            elif define:
                define.append(line)
                if line.startswith(")"):
                    process = psutil.Process(os.getpid())
                    print(f"Mem used: {process.memory_info().rss/(1024*1024):.2f} MB")
                    print("".join(define))
                    tables[table] = {"SQL":define, "data":{}}
                    define = None
                    convert = CREATE.get(table, ignore)
                continue

            if line.startswith("INSERT INTO") and table:
                #print(line[:50], "...", line[-30:])
                data = line.strip().split("),(")
                bracket = data[0].index("(")
                data[0] = data[0][bracket+1:]
                if data[-1].endswith(");"):
                    data[-1] = data[-1][:-2]
                for i,values in enumerate(data):
                    if values is None:
                        continue
                    try:
                        if i+1 < len(data):
                            if not data[i+1][0].isdigit():
                                values = f"{values}),({data[i+1]}"
                                #print("NEW DATA:", values)
                                data[i+1] = None
                        converted = convert(extract(values))
                        #converted = None
                    except Exception as e:
                        print(e)
                        print(values)
                        sys.exit()
                    if converted: # and converted[0] < 1000:
                        for i, val in enumerate(converted):
                            if isinstance(val, str):
                                if val in strings:
                                    converted[i] = strings[val]
                                    #val = strings[val]
                                else:
                                    strings[val] = val
                                #print(hex(id(val)), val)

                        packed = pack(converted)
                        tables[table]["data"][converted[0]] = packed
                for value in data[:15]:
                    pass #print(value)
                #table = None # Speed up by only doing some

    with db_session:
        for i in gen():
            if not i % 1000:
                print(i)

        with open("sqldump.sql", "w", encoding="utf-8") as f:
            con = db.get_connection()
            for line in con.iterdump():
                f.write(f"{line}\n")

    #pprint(tables)


if __name__ == "__main__":
    main(sys.argv)
    #data = [-1,0,1,10,100,1000,10000,100000,1000000,10000000,"hello","world","",None,3.14,9.99]
    #data = [580423, '12', '12', 0, 0, 34754, 56, 0, 229, 0, 'March 1997', '1997-03-00', 32, '18.95 USD; 25.95 CAD', 141.92, 0, '', 0, '', 0, 'The book\'s title page gives \\"Working With People: Co-Evolution Quarterly, Winds of Change, American Splendor, Zap Comics\\" as the issue title rather than what\'s shown on the cover.\\r\\n\\r\\n1st: March 1997; 2nd (?) printing: November 2009 (19.99 USD)', 0, 1, '1-56097-264-5', '1560972645', 0, None, '', '978156097264851895', 0, "We're Livin' in the Lap of Luxury", 0, '1997', 0, '', 0, 0, 0]
    #packed = pack(data)
    #print(len(packed))
    #unpacked = unpack(packed)
    #print(data)
    #print(unpacked)
    #print(data == unpacked)
