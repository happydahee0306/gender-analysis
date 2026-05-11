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
        # y축 이름과 타이틀 설정
        fig1 = px.bar(df1, x='성별', y='Q2_합계_평균', color='성별', 
                      title="성별에 따른 남녀평등수준 평균 점수",
                      text_auto='.2f', 
                      color_discrete_sequence=['#ff9999','#66b3ff'],
                      # [요청 반영 1] y축 이름 변경
                      labels={'Q2_합계_평균': '남녀평등이 어느정도 이루어지고있다고 생각하는가 (1~10점)'})
        
        # [요청 반영 2] y축 범위 0~10으로 고정
        fig1.update_yaxes(range=[0, 10])
        
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
    CASE 
        WHEN Q5 = 1 THEN '어려서부터 학습된 성별에 대한 고정관념'
        WHEN Q5 = 2 THEN '가부장적 사회문화'
        WHEN Q5 = 3 THEN '여성에게 주어지는 특혜와 차별'
        WHEN Q5 = 4 THEN '남성에게 주어지는 특혜와 차별'
        WHEN Q5 = 5 THEN '언론 및 방송매체의 성별 갈등 조장'
    END AS 갈등_원인_항목,
    COUNT(*) AS 응답자_수
FROM kor_data
WHERE Q5 BETWEEN 1 AND 5
GROUP BY Q5;
"""

try:
    df2 = run_query(sql2)
    col2_1, col2_2 = st.columns([1.2, 1]) # 인사이트 내용이 길어 비율을 조정했습니다.
    
    with col2_1:
        fig2 = px.bar(df2, x='응답자_수', y='갈등_원인_항목', orientation='h',
                      title="주요 젠더갈등 원인 분석",
                      labels={'갈등_원인_항목': '갈등 원인 항목', '응답자_수': '응답자 수'},
                      color='응답자_수', color_continuous_scale='Viridis',
                      text_auto=True)
        
        # 5번이 맨 위, 그 아래로 1-2-3-4 순서 유지
        fig2.update_layout(yaxis={'categoryorder':'array', 'categoryarray': [
            '남성에게 주어지는 특혜와 차별', 
            '여성에게 주어지는 특혜와 차별', 
            '가부장적 사회문화', 
            '어려서부터 학습된 성별에 대한 고정관념',
            '언론 및 방송매체의 성별 갈등 조장'
        ]})
        
        st.plotly_chart(fig2, use_container_width=True)
        
    with col2_2:
        st.subheader("🧐 데이터 분석 인사이트")
        
        # 요약 정보
        st.info("**요약:** 미디어의 갈등 조장이 가장 큰 원인으로 꼽혔으며, 구조적 관습과 정책적 공정성 논란이 그 뒤를 잇고 있습니다.")
        
        # [요청 반영] 상세 분석 내용 (Expander로 깔끔하게 배치)
        with st.expander("🔍 젠더갈등 원인 상세 분석 보기", expanded=True):
            st.markdown("""
            분석 결과, 갈등의 원인을 바라보는 대중의 시각은 크게 **외부적 요인(매체), 구조적 요인(문화), 직접적 이해관계(특혜)** 세 층위로 나뉩니다.

            **1. 압도적 1위: 언론 및 방송매체의 영향**
            가장 많은 응답자(557명)가 '언론 및 방송매체의 성별 갈등 조장'을 최대 원인으로 꼽았습니다. 미디어가 갈등을 자극적으로 보도하거나 프레임을 씌워 상황을 증폭시키는 것에 대한 강한 경계심을 보여줍니다.

            **2. 뿌리 깊은 구조적 요인**
            * **학습된 성별 고정관념(498명):** 어린 시절부터 내면화된 인식이 갈등의 토대가 됨을 시사합니다.
            * **가부장적 사회문화(488명):** 오래된 사회 구조와 현대적 가치관의 충돌을 의미합니다.
            * 두 수치가 비슷하게 높다는 점은 이 문제가 역사적·교육적 맥락이 얽힌 복합적 사안임을 드러냅니다.

            **3. 직접적 이해관계: 특혜와 차별**
            * **여성 특혜/차별(269명)** vs **남성 특혜/차별(157명)**
            * 여성이 받는 특혜나 차별을 원인으로 지목한 응답이 **약 1.7배** 더 많으며, 이는 최근의 정책적 지원이나 역차별 담론이 갈등의 한 축임을 보여줍니다.

            **💡 종합 결론**
            젠더갈등의 가장 큰 책임은 '갈등을 소비하고 재생산하는 미디어'에 있다는 인식이 강합니다. 해결을 위해서는 미디어의 윤리적 보도와 세대·성별을 아우르는 문화적 인식 개선이 병행되어야 합니다.
            """)

        with st.expander("💾 사용한 SQL 보기"):
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
        st.info("경제적 측면에서의 불평등 체감도를 성별로 비교합니다.")
        # [복구] SQL 보기 칸 추가
        with st.expander("💾 사용한 SQL 보기"):
            st.code(sql3, language='sql')
except Exception as e:
    st.error(f"차트 3 로드 중 오류 발생: {e}")

st.markdown("---")
st.caption("데이터 출처: 공공데이터포털 기반 분석 데이터 | 제작: 젠더갈등 인식 분석 대시보드")
