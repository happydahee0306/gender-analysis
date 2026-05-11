import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="공공데이터 분석 대시보드", layout="wide")
st.title("📊 성별 및 사회 갈등 인식 분석 대시보드")
st.markdown("---")

# 2. 데이터베이스 연결 확인
db_file = "kor_data.csv"

if not os.path.exists(csv_file):
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다. GitHub에 CSV 파일이 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    """CSV를 읽어 가상 DB를 만들고 SQL을 실행하는 함수"""
    # 1. 임시로 메모리에 데이터베이스를 만듭니다
    conn = sqlite3.connect(':memory:')
    
    # 2. CSV 파일을 읽어옵니다
    df_from_csv = pd.read_csv(csv_file)
    
    # 3. 이 데이터를 'kor_data'라는 이름의 테이블로 가상 DB에 저장합니다
    # 이렇게 하면 아래의 SQL 쿼리들이 'FROM kor_data'를 인식할 수 있습니다
    df_from_csv.to_sql('kor_data', conn, index=False, if_exists='replace')
    
    # 4. 쿼리 실행 후 결과 반환
    result = pd.read_sql(query, conn)
    conn.close()
    return result

# --- 차트 1: 성별 남녀평등수준 평가 ---
st.header("1. 성별 남녀평등수준 평가")

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

df1 = run_query(sql1)

col1_1, col1_2 = st.columns([2, 1])

with col1_1:
    fig1 = px.bar(df1, x='성별', y='Q2_합계_평균', color='성별', 
                  title="성별에 따른 남녀평등수준 평균 점수 (세로 막대)",
                  text_auto='.2f', color_discrete_sequence=['#ff9999','#66b3ff'])
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("📝 인사이트")
    st.info("""
    - 남성과 여성 간의 평등 수준에 대한 인식 차이를 한눈에 확인할 수 있습니다.
    - 평균 점수가 높을수록 평등하다고 느끼는 정도가 다를 수 있음을 시사합니다.
    - 성별 그룹 간 약 0.x점의 차이가 발생하는지 주목해 보세요.
    """)
    with st.expander("사용한 SQL 보기"):
        st.code(sql1, language='sql')


# --- 차트 2: 젠더갈등원인 top5 ---
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

df2 = run_query(sql2)

col2_1, col2_2 = st.columns([2, 1])

with col2_1:
    # 가로 막대그래프로 시각화
    fig2 = px.bar(df2, x='응답자_수', y='응답_점수', orientation='h',
                  title="젠더갈등 원인 응답 분포 (가로 막대)",
                  labels={'응답_점수': '응답 점수 (1: 전혀 그렇지 않다 ~ 5: 매우 그렇다)'},
                  color='응답자_수', color_continuous_scale='Viridis')
    fig2.update_layout(yaxis={'type': 'category'}) # 점수를 범주형으로 표시
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("📝 인사이트")
    st.info("""
    - 젠더 갈등의 원인에 대해 응답자들이 매긴 점수의 분포를 보여줍니다.
    - 높은 점수(4~5점)에 응답자가 몰려 있다면 갈등 원인에 대한 공감도가 높음을 의미합니다.
    - 가장 많은 응답자가 선택한 점수를 통해 사회적 분위기를 파악할 수 있습니다.
    """)
    with st.expander("사용한 SQL 보기"):
        st.code(sql2, language='sql')


# --- 차트 3: 성별 남녀간 임금 및 소득수준 불평등 평가 ---
st.markdown("---")
st.header("3. 성별 남녀간 임금 및 소득수준 불평등 평가")

sql3 = """
SELECT 
    CASE 
        WHEN SQ1 = 1 THEN '여자'
        WHEN SQ1 = 2 THEN '남자'
        ELSE '기타' 
    END AS 성별,
    ROUND(AVG(COALESCE(Q13_5, 0)), 2) AS Q13_5_평균
FROM kor_data
GROUP BY SQ1;
"""

df3 = run_query(sql3)

col3_1, col3_2 = st.columns([2, 1])

with col3_1:
    fig3 = px.bar(df3, x='성별', y='Q13_5_평균', color='성별',
                  title="성별에 따른 임금/소득 불평등 인식 평균",
                  text_auto=True, color_discrete_sequence=['#ffcc99','#99ff99'])
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("📝 인사이트")
    st.info("""
    - 경제적 측면(임금/소득)에서의 불평등 인식을 성별로 비교한 지표입니다.
    - 특정 성별에서 평균 점수가 확연히 높다면 해당 집단이 경제적 불평등을 더 크게 체감하고 있음을 나타냅니다.
    - 정책 수립 시 어떤 성별의 경제적 인식 개선이 시급한지 기초 자료로 활용 가능합니다.
    """)
    with st.expander("사용한 SQL 보기"):
        st.code(sql3, language='sql')

st.markdown("---")
st.caption("데이터 출처: 공공데이터포털 기반 분석 데이터 | 제작: 초보 개발자 성장 대시보드")
