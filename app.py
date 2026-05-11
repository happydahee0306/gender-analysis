import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="젠더갈등 인식분석", layout="wide")

# 대제목
st.title("📊 젠더갈등 인식분석  -  부산지역 2030 청년세대")

# [요청 반영] 대제목과 소제목 사이 출처 링크 추가
st.caption("출처: https://kossda.snu.ac.kr/handle/20.500.12236/26268")

# [요청 반영] 소제목 두 줄 추가
st.subheader("2014404 경영학부 최다희")
st.markdown("#### 경영정보처리론 (001) 수시과제2")

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
# [요청 반영 1] 제목 변경
st.header("2. 젠더갈등원인")

# [요청 반영 2] 제목 아래 설명 문구 추가
st.write("다음은 젠더갈등원인을 설문조사한 결과를 순위별로 나열한 것 입니다.")

# (이하 SQL 및 시각화 코드는 기존과 동일하게 유지)
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
    col2_1, col2_2 = st.columns([1.2, 1])
    
    with col2_1:
        fig2 = px.bar(df2, x='응답자_수', y='갈등_원인_항목', orientation='h',
                      title="주요 젠더갈등 원인 분석",
                      labels={'갈등_원인_항목': '갈등 원인 항목', '응답자_수': '응답자 수'},
                      color='응답자_수', color_continuous_scale='Viridis',
                      text_auto=True)
        
        fig2.update_layout(yaxis={'categoryorder':'array', 'categoryarray': [
            '남성에게 주어지는 특혜와 차별', 
            '여성에게 주어지는 특혜와 차별', 
            '가부장적 사회문화', 
            '어려서부터 학습된 성별에 대한 고정관념',
            '언론 및 방송매체의 성별 갈등 조장'
        ]})
        
        st.plotly_chart(fig2, use_container_width=True)
        
    with col2_2:
        # (인사이트 및 SQL 보기 섹션 기존 유지)
        st.subheader("🧐 데이터 분석 인사이트")
        st.info("**요약:** 미디어의 갈등 조장이 가장 큰 원인으로 꼽혔으며, 구조적 관습과 정책적 공정성 논란이 그 뒤를 잇고 있습니다.")
        
        with st.expander("🔍 젠더갈등 원인 상세 분석 보기", expanded=True):
            st.markdown("""
            분석 결과, 갈등의 원인을 바라보는 대중의 시각은 크게 **외부적 요인(매체), 구조적 요인(문화), 직접적 이해관계(특혜)** 세 층위로 나뉩니다.

            **1. 압도적 1위: 언론 및 방송매체의 영향**
            가장 많은 응답자(557명)가 '언론 및 방송매체의 성별 갈등 조장'을 최대 원인으로 꼽았습니다. 미디어가 갈등을 자극적으로 보도하거나 프레임을 씌워 상황을 증폭시키는 것에 대한 강한 경계심을 보여줍니다.

            **2. 뿌리 깊은 구조적 요인**
            * **학습된 성별 고정관념(498명):** 어린 시절부터 내면화된 인식이 갈등의 토대가 됨을 시사합니다.
            * **가부장적 사회문화(488명):** 오래된 사회 구조와 현대적 가치관의 충돌을 의미합니다.

            **3. 직접적 이해관계: 특혜와 차별**
            * 여성이 받는 특혜나 차별을 원인으로 지목한 응답이 **약 1.7배** 더 많으며, 이는 최근의 정책적 지원이나 역차별 담론이 갈등의 한 축임을 보여줍니다.

            **💡 종합 결론**
            젠더갈등의 가장 큰 책임은 '갈등을 소비하고 재생산하는 미디어'에 있다는 인식이 강합니다.
            """)

        with st.expander("💾 사용한 SQL 보기"):
            st.code(sql2, language='sql')
except Exception as e:
    st.error(f"차트 2 로드 중 오류 발생: {e}")


# --- 차트 3: 성별간 임금/소득수준 불평등 평가 ---
st.markdown("---")
st.header("3. 성별간 임금/소득수준 불평등 평가")

# 1. SQL 쿼리 정의 (오류 방지를 위해 실행 직전에 정의)
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
    # 데이터 가져오기
    df3 = run_query(sql3)
    
    # 레이아웃 설정 (차트 1.2 : 인사이트 1 비율)
    col3_1, col3_2 = st.columns([1.2, 1])
    
    with col3_1:
        # 시각화 설정 (y축 범위 0~5 고정 및 성별 색상 적용)
        fig3 = px.bar(df3, x='성별', y='Q13_5_평균', color='성별', 
                      title="성별에 따른 임금/소득 불평등 인식 평균",
                      labels={'Q13_5_평균': '성별 임금/소득 불평등이 어느정도라고 생각하십니까 (0~5점)'},
                      text_auto=True, 
                      color_discrete_sequence=['#ff9999','#66b3ff']) # 핑크, 블루
        
        fig3.update_yaxes(range=[0, 5])
        st.plotly_chart(fig3, use_container_width=True)
        
    with col3_2:
        st.subheader("🧐 데이터 분석 인사이트")
        
        # 항상 보이는 요약 정보
        st.info("**요약:** 남성(2.87점)이 여성(2.31점)보다 임금 불평등 문제를 더 심각하게 인지하는 역전 현상이 보입니다.")
        
        # [수정 포인트] 클릭해야 열리는 상세 분석 버튼
        with st.expander("🔍 성별 임금 및 소득 불평등 상세 분석 보기"):
            st.markdown("""
            **💰 성별 임금 및 소득 불평등 인식 분석** 이 조사는 0점에서 5점 사이 응답 결과이며, 점수가 높을수록 불평등이 심각하다고 느끼는 것을 의미합니다.

            **1. 경제적 불평등에 대한 전반적 인식** 남녀 모두 평균 2점 중후반대를 기록하며, 임금 격차 문제를 '어느 정도 존재하며 무시할 수 없는 수준'으로 인지하고 있습니다.

            **2. 예상외의 결과: 남성이 더 높게 평가하는 심각도** * **남성(2.87점) > 여성(2.31점)** * 실제 통계와는 별개로 '체감도' 측면에서 독특한 결과입니다. 남성들은 기업 내 변화를 '격차가 심각하다는 신호'로 더 강하게 받아들일 수 있습니다.

            **3. 경제적 측면의 불평등 체감 (인사이트)** 성별 임금 격차에 대한 지속적인 사회적 담론이 남성 집단 내에서도 위기의식을 상당 부분 형성했음을 시사합니다.

            **💡 종합 결론 (1~3번 자료 통합)** * **사회 전반 평등:** 여성이 훨씬 부정적으로 평가함.
            * **갈등의 원인:** 남녀 모두 '언론의 조장'을 1위로 꼽음.
            * **임금 불평등:** 오히려 남성이 그 심각성을 더 높게 평가함.

            사람들은 ***"사회 전반은 불평등(여성)하고 미디어가 갈등을 부추기지만, 경제적 격차만큼은 확실히 심각한 문제(남성)"***라고 인식하고 있습니다.
            """)
        
        # SQL 보기 버튼
        with st.expander("💾 사용한 SQL 보기"):
            st.code(sql3, language='sql')

except Exception as e:
    st.error(f"차트 3 로드 중 오류 발생: {e}")








