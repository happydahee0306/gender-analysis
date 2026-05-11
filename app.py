import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="젠더갈등 인식 분석 대시보드", layout="wide")
st.title("📊 젠더갈등 인식 분석 대시보드")
st.markdown("---")

# 2. 데이터 연결 설정 (CSV 파일을 가상 DB로 사용)
csv_file = "kor_data.csv"

# 파일이 있는지 먼저 확인 (변수 이름 통일: csv_file)
if not os.path.exists(csv_file):
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다. GitHub 저장소에 CSV 파일이 업로드되어 있는지 확인해주세요.")
    st.stop()

def run_query(query):
    """CSV를 읽어 가상 DB를 만들고 SQL을 실행하는 함수"""
    # 메모리에 임시 데이터베이스 생성
    conn = sqlite3.connect(':memory:')
    
    # CSV 읽기 (인코딩 에러 방지를 위해 try-except 추가)
    try:
        df_from_csv = pd.read_csv(csv_file)
    except UnicodeDecodeError:
        df_from_csv = pd.read_csv(csv_file, encoding='cp949')
    
    # 데이터를 'kor_data' 테이블로 저장
    df_from_csv.to_sql('kor_data', conn, index=False, if_exists='replace')
    
    # 쿼리 실행 및 결과 반환
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

try:
    df1 = run_query(sql1)
    col1_1, col1_2 = st.columns([2, 1])

    with col1_1:
        fig1 = px.bar(df1, x='성별', y='Q2_합계_평균', color='성별', 
                      title="성별에 따른 남녀평등수준 평균 점수 (세로 막대)",
                      text_auto='.2f', color_discrete_sequence=['#ff9999','#66b3ff'])
        st.plotly_chart(fig1, use_container_width=True)

    with col1_2:
        st.subheader("📝 인사이트")
        st.info("남성과 여성 간의 평등 수준에 대한 인식 차이를 한눈에 확인할 수 있습니다.")
        with st.expander("사용한 SQL 보기"):
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
        st.info("높은 점수(4~5점)에 응답자가 몰려 있다면 갈등 원인에 대한 공감도가 높음을 의미합니다.")
        with st.expander("사용한 SQL 보기"):
            st.code(sql2, language='sql')
except Exception as e:
    st.error(f"차트 2 로드 중 오류 발생: {e}")


# --- 차트 3: 임금 및 소득수준 불평등 평가 ---
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

try:
    df3 = run_query(sql3)
    col3_1, col3_2 = st.columns([2, 1])

    with col3_1:
        fig3 = px.bar(df3, x='성별', y='Q13_5_평균', color='성별',
                      title="성별에 따른 임금/소득 불평등 인식 평균",
                      text_auto=True, color_discrete_sequence=['#ffcc99','#99ff99'])
        st.plotly_chart(fig3, use_container_width=True)

    with col3_2:
        st.subheader("📝 인사이트")
        st.info("특정 성별에서 평균 점수가 높다면 해당 집단이 경제적 불평등을 더 크게 체감하고 있음을 나타냅니다.")
        with st.expander("사용한 SQL 보기"):
            st.code(sql3, language='sql')
except Exception as e:
    st.error(f"차트 3 로드 중 오류 발생: {e}")

st.markdown("---")
st.caption("데이터 출처: 공공데이터포털 기반 분석 데이터 | 제작: 성별 및 사회 갈등 인식 분석 대시보드")
