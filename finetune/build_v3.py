"""데비&마를렌 파인튜닝 데이터셋 v3 - 말투(assistant only) + Q&A + 아이템"""
import json, re, random, os
from pathlib import Path
from collections import defaultdict

random.seed(42)
BASE = Path(__file__).parent
RAW = BASE / "raw_data"
OUT = BASE / "dataset"
OUT.mkdir(exist_ok=True)

# ── 나무위키 파싱 ──
SKIP = {
    "[편집]","파란색","빨간색","으로 표기.","데비의 대사는","마를렌의 대사는",
    "[더미]","(대사 1)","(대사 2)","데비","마를렌","행동","지역","전투","제작",
    "교전","킬","[목소리]","공격",
}
CATS = [
    "로비","선택 시","실험 시작","하이퍼루프 이용","하이퍼 루프 이용",
    "아군에게 하이퍼루프","보안 콘솔 이용","트랩 설치","휴식","해킹 시도",
    "소생 시작","소생 성공","부활 성공","점령장치 점령","원격드론 호출",
    "필요한 아이템 요청","감정표현","농담","감정 표현","도발","감사",
    "Q 스킬 시전","W 스킬 시전","E 스킬 시전","R 스킬 시전",
    "무기 스킬 습득","양손검 - 빗겨 흘리기",
    "고급 등급 아이템 제작","영웅 등급 아이템 제작",
    "전설 등급 아이템 제작","초월 등급 아이템 제작",
    "고급 아이템 제작","영웅 아이템 제작","전설 아이템 제작",
    "적 처치","아군 처치됨","적 처치 시","아군 처치 시","사망 시",
    "사망","처치","승리","패배","최종 금지구역",
    "금지구역 이동","금지구역 알림","제작 관련","상호 대사",
    "첫 킬","멀티킬","처치 지원",
    "골목길","양궁장","묘지","성당","공장","소방서","숲",
    "주유소","항구","병원","호텔","경찰서","학교","연못",
    "모래사장","고급 주택가","번화가","연구소","연구소 외곽",
]

def is_cat(line):
    if line in CATS: return True
    if re.match(r"^\d+명 처치 시$", line): return True
    if re.match(r"^(상위권|하위권|\d+등|꼴등)$", line): return True
    if re.match(r"^.+\s?채집$", line): return True
    return False

def parse_namu(fp):
    lines = open(fp, encoding="utf-8").readlines()
    res, inq, sec, idx = [], False, "", 0
    for i, raw in enumerate(lines):
        l = raw.strip()
        if not l: continue
        if "실험체 대사" in l and "스파클링" not in l and "방과" not in l: inq,sec=True,""; continue
        if "스파클링 트윈즈 데비&마를렌 대사" in l: inq,sec=True,""; continue
        if "방과 후 자유시간 데비&마를렌 대사" in l: inq,sec=True,""; continue
        if "아나운서 대사" in l: inq=False; continue
        if not inq: continue
        if re.match(r"^\d+\.\s*$",l):
            if int(l.split(".")[0])!=9: inq=False
            continue
        if re.match(r"^\d+\.\d",l): continue
        if l=="데비" and i+1<len(lines) and "[편집]" in lines[i+1]: sec="d"; continue
        if l=="마를렌" and i+1<len(lines) and "[편집]" in lines[i+1]: sec="m"; continue
        if l in SKIP or (l.startswith("[") and l.endswith("]")): continue
        if l.startswith(". "): continue
        if is_cat(l): idx=0; continue
        if re.match(r"^\d+[\d.]*$",l) or l.isdigit(): continue
        if len(l)<2: continue
        if "마를렌의 대사는" in l or "데비의 대사는" in l: continue
        if sec=="d": sp="debi" if idx%2==0 else "marlene"
        elif sec=="m": sp="marlene" if idx%2==0 else "debi"
        else: sp="debi" if idx%2==0 else "marlene"
        res.append({"s":sp,"t":l}); idx+=1
    return res

def parse_tts(fp, sp):
    res=[]
    for l in open(fp,encoding="utf-8"):
        if l.strip(): res.append({"s":sp,"t":json.loads(l)["text"]})
    return res

# ── Part 1: 말투 (assistant only) ──
def build_p1(quotes):
    ds, seen, i = [], set(), 0
    while i<len(quotes):
        q=quotes[i]
        if q["t"] in seen: i+=1; continue
        if i+1<len(quotes) and quotes[i]["s"]!=quotes[i+1]["s"]:
            q2=quotes[i+1]
            if q2["t"] not in seen:
                n1="데비" if q["s"]=="debi" else "마를렌"
                n2="마를렌" if q["s"]=="debi" else "데비"
                ds.append({"messages":[{"role":"assistant","content":f"{n1}: {q['t']}\n{n2}: {q2['t']}"}]})
                seen.add(q["t"]); seen.add(q2["t"]); i+=2; continue
        n="데비" if q["s"]=="debi" else "마를렌"
        ds.append({"messages":[{"role":"assistant","content":f"{n}: {q['t']}"}]})
        seen.add(q["t"]); i+=1
    return ds

# ── Part 2: Q&A (txt) ──
def build_p2(fp):
    if not os.path.exists(fp): return []
    content = open(fp, encoding="utf-8").read()
    ds, blocks = [], content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines)<2: continue
        # [섹션 헤더] 스킵
        if lines[0].startswith("["): continue
        q = lines[0]
        if q.startswith("Q:"): q = q.split(":",1)[1].strip()
        a_parts = []
        for al in lines[1:]:
            if al.startswith("A:"): a_parts.append(al.split(":",1)[1].strip())
            else: a_parts.append(al.strip())
        a = "\n".join(a_parts)
        if q and a:
            ds.append({"messages":[{"role":"user","content":q},{"role":"assistant","content":a}]})
    return ds

# ── Part 3: 아이템 ──
def build_p3(fp, n=200):
    if not os.path.exists(fp): return []
    data = json.load(open(fp,encoding="utf-8"))
    ds=[]; random.shuffle(data)
    for item in data[:n]:
        orig = item["conversations"][1]["value"]
        m = re.match(r"^(.+?)(이야|야)\.", orig)
        if not m: continue
        name, rest = m.group(1), orig[m.end():].strip()
        pats = [
            f"데비: {name}! {rest}\n마를렌: 쓸만한 장비지.",
            f"데비: 오~ {name}이잖아!\n마를렌: {orig}",
            f"데비: {name}? 알지~\n마를렌: {rest}",
        ]
        qs = [f"{name} 뭐야?", f"{name} 어때?", f"{name} 알아?"]
        ds.append({"messages":[{"role":"user","content":random.choice(qs)},{"role":"assistant","content":random.choice(pats)}]})
    return ds

# ── 메인 ──
def main():
    print("=== v3 데이터셋 생성 ===\n")
    quotes = []
    namu = RAW/"namu_debi_marlene_main.txt"
    if namu.exists():
        q = parse_namu(str(namu)); quotes.extend(q); print(f"나무위키: {len(q)}개")
    for fn,sp in [("debi_finetune.jsonl","debi"),("marlene_finetune.jsonl","marlene")]:
        p = BASE/fn
        if p.exists():
            t = parse_tts(str(p),sp); quotes.extend(t); print(f"TTS ({sp}): {len(t)}개")

    p1 = build_p1(quotes); print(f"\nPart 1 (말투): {len(p1)}개")
    p2 = build_p2(str(BASE/"qa_custom.txt")); print(f"Part 2 (Q&A):  {len(p2)}개")
    vlm = BASE.parent/"vlm_training"/"dataset"/"eternal_return_vlm_dataset.json"
    p3 = build_p3(str(vlm)); print(f"Part 3 (지식): {len(p3)}개")

    all_data = p1 + p2 + p3
    random.shuffle(all_data)
    json.dump(all_data, open(OUT/"train.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n합계: {len(all_data)}개 -> {OUT/'train.json'}")

if __name__=="__main__": main()
