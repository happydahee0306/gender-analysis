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

st.markdown("""
아래 막대그래프는 성별에 따라 다음 주제에 대해 각각 남녀평등수준을 1~10점 사이로 평가한 것을 집계하여 평균을 낸 것입니다.  
**주제:** 우리사회전반, 취업, 직장 내 승진, 임금, 가족 내 의사결정, 가사노동 및 돌봄, 연애관계, 정치참여, 범죄나 폭력으로부터의 안전, 성차별관련 언론보도
""")

# (SQL 및 데이터 호출 부분은 동일하므로 생략, 아래 시각화 레이아웃 부분만 교체하세요)
try:
    df1 = run_query(sql1)
    col1_1, col1_2 = st.columns([1.5, 1]) # 가독성을 위해 비율을 조정했습니다.

    with col1_1:
        fig1 = px.bar(df1, x='성별', y='Q2_합계_평균', color='성별', 
                      title="성별에 따른 남녀평등수준 평균 점수",
                      text_auto='.2f', 
                      color_discrete_sequence=['#ff9999','#66b3ff'])
        st.plotly_chart(fig1, use_container_width=True)

    with col1_2:
        st.subheader("🧐 데이터 분석 인사이트")
        
        # 1. 요약 정보
        st.info("**요약:** 남녀 모두 평등 수준이 높지 않다고 보나, 여성(4.00점)이 남성(5.43점)보다 훨씬 더 불평등을 크게 체감하고 있습니다.")
        
        # 2. 상세 분석 (Expander 사용으로 깔끔하게 정리)
        with st.expander("🔍 상세 분석 내용 보기", expanded=True):
            st.markdown(f"""
            이 자료는 주요 11가지 주제에 대해 1점(매우 불평등)에서 10점(매우 평등) 사이로 평가한 결과입니다.

            **1. 전반적인 평등 수준 점수**
            여성과 남성 모두 우리 사회의 남녀평등 수준을 중간 점수(5.5점)보다 낮거나 비슷하게 평가하고 있습니다. 이는 우리 사회가 완벽한 평등 단계에 도달하지 못했다는 공통된 인식을 보여줍니다.

            **2. 성별에 따른 뚜렷한 인식 차이**
            * **남성(5.43점):** 상대적으로 우리 사회가 어느 정도 평등에 근접해 가고 있다고 느끼는 편입니다.
            * **여성(4.00점):** 남성에 비해 우리 사회가 훨씬 더 불평등하다고 체감하고 있습니다.
            * **격차 분석:** **1.43점**의 유의미한 격차는 여성이 차별적 요소를 더 민감하고 직접적으로 경험하고 있음을 시사합니다.

            **3. 데이터가 주는 시사점**
            * **사회적 합의의 필요성:** 여성이 느끼는 불평등 체감도가 높으므로, 정책적 개선 시 이러한 인식의 간극을 줄이는 것이 우선 과제입니다.
            * **구조적 문제의 반영:** 4.00점이라는 점수는 가사노동, 안전 등 실생활 영역에서 여성이 느끼는 부담이나 불안이 여전히 크다는 점을 방증합니다.
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
