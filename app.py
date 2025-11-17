import streamlit as st
from supabase import create_client, Client
from collections import Counter
import os

# =========================
# 1. Supabase 설정
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xxxxx.supabase.co")  # 수정
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOi...")             # 수정

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# 2. Streamlit UI
# =========================
st.set_page_config(page_title="다산콜센터 민원 분야 추천", layout="centered")

st.title("🔎 다산콜센터 민원 분야 추천 서비스")
st.write("키워드를 입력하면, 관련 상담 사례를 분석하여 **가장 많이 등장하는 민원 분야**를 추천합니다.")

keyword = st.text_input("검색 키워드를 입력하세요 (예: 주차, 세금, 출산, 장애인 등)")

if st.button("검색"):
    if not keyword.strip():
        st.warning("키워드를 입력해주세요.")
    else:
        # 로딩 인디케이터
        with st.spinner("민원 데이터를 검색하고 있습니다..."):
            # Supabase에서 question 컬럼에 keyword가 포함된 행 조회 (대소문자 구분 없이)
            pattern = f"%{keyword}%"
            response = supabase.table("dasancall") \
                               .select("category, question") \
                               .ilike("question", pattern) \
                               .execute()

            rows = response.data

        # 결과 처리
        if not rows:
            st.error("해당 키워드가 포함된 민원 상담 내역을 찾지 못했습니다.")
        else:
            # category 빈도 계산
            categories = [r["category"] for r in rows if r.get("category")]
            counter = Counter(categories)
            top_category, top_count = counter.most_common(1)[0]

            st.success(f"추천 분야: **{top_category}**")

            # 선택: 간단한 통계와 예시 몇 개 보여주기
            st.write("검색된 민원 분야 빈도:")
            for cat, cnt in counter.most_common():
                st.write(f"- {cat}: {cnt}건")

            with st.expander("🔍 해당 키워드가 포함된 질문 예시 보기 (최대 5개)"):
                for r in rows[:5]:
                    st.write(f"• {r['question']}")
