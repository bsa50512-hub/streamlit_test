import streamlit as st
import random
import hashlib
from datetime import date, datetime, timedelta, timezone
import pandas as pd

# 한국 시간 기준 '오늘' (서버가 해외/UTC여도 날짜가 어긋나지 않게)
KST = timezone(timedelta(hours=9))


def today_kst():
    return datetime.now(KST).date()


# ---------- 기본 정보 ----------
ANIMALS = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
ANIMAL_EMOJI = ["🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑", "🐵", "🐔", "🐶", "🐷"]
STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
# 천간 2개씩 같은 색·오행
COLORS = ["푸른", "푸른", "붉은", "붉은", "노란", "노란", "흰", "흰", "검은", "검은"]
ELEMENTS = ["나무", "나무", "불", "불", "흙", "흙", "쇠", "쇠", "물", "물"]
ELEMENT_TEXT = {
    "나무": "새싹처럼 계속 자라는 사람. 시작하는 힘이 강해요 🌱",
    "불": "열정이 넘치고 주변을 환하게 만드는 사람 🔥",
    "흙": "든든하고 믿음직한, 모두의 기댈 곳 ⛰️",
    "쇠": "한번 정하면 끝까지 가는 단단한 사람 ⚔️",
    "물": "유연하고 생각이 깊은, 분위기 파악의 달인 🌊",
}

LUCKY_ITEMS = ["편의점 삼각김밥", "충전 100% 보조배터리", "새 볼펜", "따뜻한 아메리카노",
               "이어폰", "노란 포스트잇", "초코우유", "우산", "텀블러", "에코백"]
LUCKY_COLORS = ["빨강", "주황", "노랑", "초록", "파랑", "남색", "보라", "분홍", "하양", "검정"]

ADVICE = {
    "연애운": {
        "high": "먼저 연락하면 좋은 일이 생겨요. 오늘은 용기 내는 날 💌",
        "mid": "무난한 하루. 상대 말에 리액션만 잘해도 호감도 상승 😊",
        "low": "오늘은 감정 표현보다 나 자신 챙기기. 내 기분이 먼저예요 🫶",
    },
    "시험운": {
        "high": "찍어도 맞는 날! 그래도 공부한 만큼 더 잘 나와요 ✍️",
        "mid": "아는 문제는 확실히, 헷갈리는 건 한 번 더 확인하세요 📚",
        "low": "오늘 미룬 공부는 내일의 내가 웁니다. 딱 30분만 하기 ⏰",
    },
    "취업운": {
        "high": "서류 넣기 좋은 날! 미뤄둔 자소서 오늘 제출하세요 📄",
        "mid": "포트폴리오 한 줄 다듬기 좋은 날. 작은 준비가 쌓여요 🧩",
        "low": "오늘은 쉬어가는 날. 컨디션 관리도 취업 준비예요 🍵",
    },
}


# 오늘 할 일 추천: 가장 점수가 높은 운세에 맞춘 할 일
TODO_BY_FORTUNE = {
    "연애운": ["오랜만에 친구에게 먼저 안부 문자 보내기", "고마운 사람에게 '고마워' 한마디 하기",
              "좋아하는 사람과 가볍게 커피 한 잔", "가족에게 맛있는 간식 사 가기"],
    "시험운": ["오늘 배운 내용 10분 복습하기", "헷갈리던 개념 하나 확실히 정리하기",
              "기출문제 한 세트 풀어보기", "공부 계획표 이번 주 것만 새로 짜기"],
    "취업운": ["자소서 한 문단 다듬기", "관심 회사 채용공고 3개 찾아 저장하기",
              "포트폴리오에 최근 작업 하나 추가하기", "링크드인/이력서 사진·한 줄 소개 업데이트"],
}
# 타고난 오행에 맞춘 할 일
TODO_BY_ELEMENT = {
    "나무": ["미뤄둔 일 하나 '시작'만 해보기", "새로운 카페나 산책길 가보기"],
    "불": ["좋아하는 노래 크게 틀고 신나게 정리하기", "운동 20분으로 에너지 발산하기"],
    "흙": ["방이나 책상 한 구역 정리하기", "이번 달 지출 한 번 점검하기"],
    "쇠": ["체크리스트 만들어서 하나씩 지우기", "끝내지 못한 일 하나 마무리하기"],
    "물": ["물 2리터 마시기 💧", "조용히 일기나 메모 한 줄 쓰기"],
}
# 누구에게나 좋은 작은 습관
TODO_SMALL = ["스트레칭 5분", "일찍 자기 (12시 전 취침)", "휴대폰 알림 정리하기",
              "창문 열고 환기하기", "하늘 사진 한 장 찍기", "물건 하나 버리기"]


def saju_year(birth):
    """사주에서 해가 바뀌는 기준은 1월 1일이 아니라 입춘(약 2월 4일)"""
    if (birth.month, birth.day) < (2, 4):
        return birth.year - 1
    return birth.year


def make_rng(name, birth, birth_time, today):
    """같은 사람·같은 날이면 항상 같은 결과가 나오게 하는 랜덤 생성기"""
    key = f"{name}-{birth}-{birth_time}-{today}"
    seed = int(hashlib.md5(key.encode()).hexdigest(), 16) % (10 ** 8)
    return random.Random(seed)


def level(score):
    if score >= 80:
        return "high"
    elif score >= 50:
        return "mid"
    return "low"


# ---------- 화면 ----------
st.title("🔮 오늘의 사주 운세")
st.caption("이름과 생일을 넣으면 오늘의 운세를 알려드려요")

name = st.text_input("이름", placeholder="예: 김서아").strip()
birth = st.date_input("생년월일", value=date(2000, 1, 1),
                      min_value=date(1940, 1, 1), max_value=today_kst())
birth_time = st.selectbox("태어난 시간", ["모름", "새벽 (0~6시)", "오전 (6~12시)",
                                       "오후 (12~18시)", "저녁 (18~24시)"])

if st.button("사주 보기 ✨"):
    if name == "":
        st.warning("이름을 입력해 주세요!")
    else:
        today = today_kst()
        rng = make_rng(name, birth, birth_time, today)

        # 1) 띠와 오행 (입춘 기준)
        y = saju_year(birth)
        idx12 = (y - 4) % 12
        stem = (y - 4) % 10
        animal = ANIMALS[idx12]
        emoji = ANIMAL_EMOJI[idx12]
        element = ELEMENTS[stem]
        gapja = STEMS[stem] + BRANCHES[idx12]

        st.header(f"{emoji} {name}님은 {COLORS[stem]} {animal}띠")
        st.write(f"**{y}년 = {gapja}년**, **{element}**의 기운을 타고났어요.")
        if y != birth.year:
            st.caption(f"※ 입춘(2월 4일) 전에 태어나서 {y}년 기준으로 봤어요.")
        st.info(ELEMENT_TEXT[element])

        # 2) 오늘의 운세 점수
        st.subheader(f"📅 {today.strftime('%Y년 %m월 %d일')} 오늘의 운세")
        scores = {k: rng.randint(30, 100) for k in ["연애운", "시험운", "취업운"]}

        cols = st.columns(3)
        for col, (k, v) in zip(cols, scores.items()):
            stars = "★" * (v // 20) + "☆" * (5 - v // 20)
            col.metric(k, f"{v}점")
            col.write(stars)

        st.bar_chart(pd.DataFrame({"점수": scores}))

        # 3) 운세별 한 줄 조언
        for k, v in scores.items():
            st.write(f"**{k}** · {ADVICE[k][level(v)]}")

        # 4) 행운 아이템
        st.subheader("🍀 오늘의 행운")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**아이템**\n\n{rng.choice(LUCKY_ITEMS)}")
        c2.write(f"**색깔**\n\n{rng.choice(LUCKY_COLORS)}")
        c3.write(f"**숫자**\n\n{rng.randint(1, 45)}")

        # 5) 총평
        avg = sum(scores.values()) / 3
        if avg >= 80:
            st.success("오늘은 대길! 뭘 해도 되는 날이에요 🎉")
            st.balloons()
        elif avg >= 55:
            st.info("무난하고 편안한 하루가 될 거예요 🙂")
        else:
            st.warning("오늘은 조심조심. 내일은 분명 더 좋아요 💪")

        # 6) 오늘 할 일 추천
        st.subheader("✅ 오늘 할 일 추천")
        best = max(scores, key=scores.get)
        todos = [
            (f"{best}이 가장 좋아요", rng.choice(TODO_BY_FORTUNE[best])),
            (f"{element}의 기운", rng.choice(TODO_BY_ELEMENT[element])),
            ("작은 습관", rng.choice(TODO_SMALL)),
        ]
        for i, (why, todo) in enumerate(todos, 1):
            st.markdown(f"**{i}. {todo}**  \n<small>└ {why}</small>",
                        unsafe_allow_html=True)

st.divider()
st.caption("※ 재미로만 봐주세요 😊 같은 이름·생일·시간이면 하루 동안 같은 결과가 나와요.")
