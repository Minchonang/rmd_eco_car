import pandas as pd
import pymysql
import streamlit as st

class teamTableSearchClass:
    def __init__(self):
        pass

    # 시작
    def start(self):
        try:
            self.conn = pymysql.connect(host="54.202.87.166",
                                        user="team3",
                                        password="dbdbdb",
                                        db="teamproject3",
                                        charset="utf8",
                                        autocommit=True,
                                        cursorclass=pymysql.cursors.DictCursor)
            print("DB 접속 성공 >>>> ", self.conn)
        except:
            print("DBserver check...")

        self.cur = self.conn.cursor()
        print(f"self.cur : {self.cur}")

    # 조회
    def select(self, sql):
        self.start()
        rs_cnt = self.cur.execute(sql)

        if rs_cnt > 1:
            print(f'{rs_cnt}건 조회')
            read = self.cur.fetchall()
            df = pd.DataFrame(read)
            self.exit()
            return df
        elif rs_cnt == 1:
            print(f'{rs_cnt}건 조회')
            read = self.cur.fetchone()
            df = pd.DataFrame([read])
            self.exit()
            return df
        else:
            print('조회될건이 없습니다.')
            self.exit()

    # 종료
    def exit(self):
        # 접속종료
        try:
            print('접속해제')
            self.cur.close()
            self.conn.close()
        except:
            print("이미 꺼짐")
            self.cur.close()
            self.conn.close()


ts = teamTableSearchClass()


ori_df = ts.select('''
        select * 
        from car_prop_elec_hydro
    ''')

elec_subside = ts.select('''
            select * 
            from elec_subside
            ''')
hydro_subside = ts.select('''
            select * 
            from hydro_subside
            ''')

elec_reg = elec_subside['reg_div']
hydro_reg = hydro_subside['reg_div']
elec_reg_unique = elec_reg.str.strip().unique()
hydro_reg_unique = hydro_reg.str.strip().unique()


ori_df

car_grade = ori_df['car_grade'].str.strip().unique()
print(car_grade)
car_type = ori_df['car_type'].str.strip().unique()
print(car_type)
company = ori_df['company'].str.strip().unique()
print(company)
power = ori_df['power'].str.strip().unique()
print(power)

 md
# # streamlit 영역입니다
# 
# 사용자에게 제공하는 서비스 구현
# 사용자가 입력하는 항목에 따라 적정한 차량 소개
# 연비 , 지역에 따른 보조금  
# 필요한 것 : 차량 별 가격 컬럼 , 해외 전기/수소차 데이터 추가
# Streamlit 사용하여 사용자에게 입력 받아서 출력 가능
# 주소(시군) -> 지역에 따른 보조금
# 하루 평균 이동 거리 -> 연비
# 차량 가격
# 회사 별
# 차종1 (suv , 세단)
# 차종2 (소형 ,준중형 , 중형 , 준대형 ,대형)
# 

st.subheader("당신이 찾는 친환경 차를 찾아드립니다!")

po_input = st.selectbox('원하는 연료을 선택하세요', power, index=None)

if po_input == '수소':
    searchtable="hydro_subside"
    reg_input = st.selectbox('지역을 선택하세요', hydro_reg_unique, index=None)
    ca_gr_input=None
    ca_ty_input=None
    car_input=None
    df_car=ts.select(f'''
        SELECT *
        FROM car_prop_elec_hydro
        WHERE POWER="{po_input}"
        ORDER BY fuel_price_100km asc
        ''')
    df_sub=ts.select(f'''
    SELECT subside_2023
    FROM hydro_subside
    WHERE reg_div="{reg_input}"
    ''')
# elif po_input == '전기':
else:
    searchtable="elec_subside"
    reg_input = st.selectbox('지역을 선택하세요', elec_reg_unique, index=None)

    ca_gr_input = st.selectbox('원하는 차급을 선택하세요', car_grade, index=None)

    ca_ty_input = st.selectbox('원하는 차종을 선택하세요', car_type, index=None)

    car_input = st.selectbox('원하는 회사를 선택하세요', company, index=None)

    df_car=ts.select(f'''
    SELECT *
    FROM car_prop_elec_hydro
    WHERE POWER="{po_input}" AND car_grade="{ca_gr_input}" AND car_type="{ca_ty_input}" AND company="{car_input}"
    ORDER BY fuel_price_100km asc
    ''')
    df_sub=ts.select(f'''
    SELECT subside_2023
    FROM {searchtable}
    WHERE reg_div="{reg_input}"
    ''')
st.write(f'사용자입력값: {reg_input, ca_gr_input, ca_ty_input, car_input, po_input}')

st.subheader('조회 결과')
st.write(df_car)
st.write(df_sub)

