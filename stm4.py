# [위치] apps/part4.py 새파일
import streamlit as st
import pandas as pd
DATA = "data/heart_failure_clinical_records_dataset.csv"
df = pd.read_csv(DATA)
st.title("심부전환자차트")
counts = df["DEATH_EVENT"].map({0: "생존", 1: "사망"}).value_counts()
st.bar_chart(counts)

# [위치] apps/part4.py — 맨 위 import 줄 아래에 끼워 넣기
# ▼ 이미 있는 줄
import pandas as pd
# ▼ 이 줄 아래에 새로 (0칸)
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("fonts/NanumGothic-Regular.ttf")
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

# [위치] apps/part4.py — 맨 아래에 이어서
# ▼ 이미 있는 줄
st.bar_chart(counts)
# ▼ 한 줄 띄우고 이 줄 아래에 새로 (0칸)
fig, ax = plt.subplots()
ax.bar(counts.index, counts.values)
ax.set_title("사망 여부별 환자 수")
st.pyplot(fig)