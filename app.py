import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="젠더갈등 인식 분석 대시보드", layout="wide")
st.title("📊 젠더갈등 인식 분석 대시보드")
st.markdown("---")

# 2. 데이터 연결 설정
csv_file = "kor_data.csv"

if not os.path.exists(csv_file):
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다. GitHub에 CSV 파일이 업로드되어 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    """CSV를 읽어 가상 DB를 만들고 SQL을 실행하는 함수"""
    conn = sqlite3.connect(':memory:')
    try:
        df_from_csv = pd.read_csv(csv_file)
    except UnicodeDecodeError:
        df_from_csv = pd.read_csv(csv_file, encoding='cp949')
    df_from_csv.to_sql('kor_data', conn, index=False, if_exists='replace')
    result = pd.read_sql(query, conn)
    conn.close()
    return result

# --- 차트 1: 성별 남녀평등수준 평가 ---
st.header("1. 성별 남녀평등수준 평가")

st.markdown("""
아래 막대그래프는 성별에 따라 다음 주제에 대해 각각 남녀평등수준을 1~10점 사이로 평가한 것을 집계하여 평균을 낸 것입니다.  
**주제:** 우리사회전반, 취업, 직장 내 승진, 임금, 가족 내 의사결정, 가사노동 및 돌봄, 연애관계, 정치참여, 범죄나 폭력으로부터의 안전, 성차별관련 언론보도
""")

sql1 = """
SELECT 
    CASE 
        WHEN SQ1 = 1 THEN '여자'
        WHEN SQ1 = 2 THEN '남자'
        ELSE '기타' 
    END AS 성별,
    AVG(
        COALESCE(Q2_1, 0) + COALESCE(Q2_2, 0) + COALESCE(Q2_3, 0) + 
        COALESCE(Q2_4, 0) + COALESCE(Q2_5, 0) + COALESCE(Q2_6, 0) + 
        COALESCE(Q2_7, 0) + COALESCE(Q2_8, 0) + COALESCE(Q2_9, 0) + 
        COALESCE(Q2_10, 0)
    ) / 10 AS Q2_합계_평균
FROM kor_data
GROUP BY SQ1;
"""

try:
    df1 = run_query(sql1)
    col1_1, col1_2 = st.columns([1.5, 1])

    with col1_1:
        fig1 = px.bar(df1, x='성별', y='Q2_합계_평균', color='성별', 
                      title="성별에 따른 남녀평등수준 평균 점수",
                      text_auto='.2f', 
                      color_discrete_sequence=['#ff9999','#66b3ff'])
        st.plotly_chart(fig1, use_container_width=True)

    with col1_2:
        st.subheader("🧐 데이터 분석 인사이트")
        st.info("**요약:** 남녀 모두 평등 수준이 낮다고 보나, 여성(4.00점)이 남성(5.43점)보다 불평등을 훨씬 크게 체감합니다.")
        
        with st.expander("🔍 상세 분석 내용 보기", expanded=True):
            st.markdown("""
            **1. 전반적인 평등 수준 점수** 남녀 모두 우리 사회의 평등 수준을 낮게 평가하고 있어, 사회적 개선이 필요하다는 공통된 인식을 보여줍니다.

            **2. 성별에 따른 인식 격차** 남성(5.43점)과 여성(4.00점) 사이의 **1.43점** 격차는 동일한 환경에서도 여성이 느끼는 차별적 요소가 더 큼을 의미합니다.
            """)
        
        with st.expander("💾 사용한 SQL 보기"):
            st.code(sql1, language='sql')
except Exception as e:
    st.error(f"차트 1 로드 중 오류 발생: {e}")

# --- 차트 2: 젠더갈등원인 ---
st.markdown("---")
st.header("2. 젠더갈등원인 (응답 점수별 분포)")

sql2 = """
SELECT 
    Q5 AS 응답_점수, 
    COUNT(*) AS 응답자_수
FROM kor_data
WHERE Q5 BETWEEN 1 AND 5
GROUP BY Q5
ORDER BY Q5 ASC;
"""

try:
    df2 = run_query(sql2)
    col2_1, col2_2 = st.columns([2, 1])
    with col2_1:
        fig2 = px.bar(df2, x='응답자_수', y='응답_점수', orientation='h',
                      title="젠더갈등 원인 응답 분포 (가로 막대)",
                      labels={'응답_점수': '응답 점수 (1: 전혀 그렇지 않다 ~ 5: 매우 그렇다)'},
                      color='응답자_수', color_continuous_scale='Viridis')
        fig2.update_layout(yaxis={'type': 'category'})
        st.plotly_chart(fig2, use_container_width=True)
    with col2_2:
        st.subheader("📝 인사이트")
        st.info("갈등 원인에 대한 응답자들의 공감 분포를 나타냅니다.")
        # [복구] SQL 보기 칸 추가
        with st.expander("💾 사용한 SQL 보기"):
            st.code(sql2, language='sql')
except Exception as e:
    st.error(f"차트 2 로드 중 오류 발생: {e}")

# --- 차트 3: 임금 및 소득수준 불평등 평가 ---
st.markdown("---")
st
