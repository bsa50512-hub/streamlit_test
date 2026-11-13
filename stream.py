# 파이썬으로 웹 화면 만들기 !!
import streamlit as st

st.title("나의 첫 번째 웹")
st.write("안녕하세요. 저는 파이썬으로 웹 화면을 만들고 있습니다.")


age = st.slider("나이", 20, 45, 60)

st.write("나이는", age, "살 입니다.")

