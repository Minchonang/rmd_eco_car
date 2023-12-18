import pandas as pd
import pymysql
import streamlit as st


class teamTableSerarchClass:
    def __init__(self):
        pass

    # 시작
    def start(self):
        try:
            self.conn = pymysql.connect(
                host="54.202.87.166",
                user="team3",
                password="dbdbdb",
                db="teamproject3",
                charset="utf8",
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("DB 접속 성공", self.conn)
        except:
            print("DBserver check...")
        self.cur = self.conn.cursor()

    # 조회
    def select(self, sql):
        self.start()
        rs_cnt = self.cur.execute(sql)

        if rs_cnt > 1:
            print(f"{rs_cnt}건 조회")
            read = self.cur.fetchall()
            df = pd.DataFrame(read)
            self.exit()
            return df
        elif rs_cnt == 1:
            print(f"{rs_cnt}건 조회")
            read = (
                self.cur.fetchall()
            )  # list(self.cur.fetchone())+  list(self.cur.fetchone().values())
            print(read)
            df = pd.DataFrame(read)
            self.exit()
            return df
        else:
            print("조회될 차량이 없습니다.")
        self.exit()

    # 종료
    def exit(self):
        # 접속종료
        try:
            print("접속 해제")
            self.cur.close()
            self.conn.close()
        except:
            print("이미 꺼짐")


### 클래스 사용
ts = teamTableSerarchClass()

### 자동차 제원 테이블 전체 받아오기
ori_df = ts.select(
    """
        select * from car_prop_elec_hydro;
    """
)


### 제원 테이블 띄어쓰기 삭제한 데이터프레임 생성
# ori_df['car_grade']=ori_df.loc[:,'car_grade'].strip()
ori_df2 = ori_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

### 전기차 보조금, 수소차 보조금 데이터 프레임 받아오기
elec_subside = ts.select(
    """
            select * from elec_subside;
            """
)
hydro_subside = ts.select(
    """
            select * from hydro_subside;
            """
)

### 각 보조금 테이블의 지역명 추출
elec_reg = elec_subside["reg_div"]
hydro_reg = hydro_subside["reg_div"]
elec_reg_unique = elec_reg.str.strip().unique()
hydro_reg_unique = hydro_reg.str.strip().unique()


## 전체 제원 출력해서 보여주기
ori_df2.rename(
    columns={
        "company": "회사",
        "car_grade": "차급",
        "car_type": "차종",
        "power": "동력",
        "name": "차이름",
        "fuel_effi": "연비",
        "car_price": "차 가격",
        "fuel_price_100km": "100km연료비",
    },
    inplace=True,
)
ori_df2

car_grade = ori_df2["차급"].str.strip().unique()
car_type = ori_df2["차종"].str.strip().unique()
company = ori_df2["회사"].str.strip().unique()
power = ori_df2["회사"].str.strip().unique()


st.subheader("당신에게 맞는 친환경 자동차를 찾아드립니다!")

po_input = st.selectbox("원하는 연료를 선택하세요", power, index=None)

if po_input == "수소":
    searchtable = "hydro_subside"
    reg_input = st.selectbox("지역을 선택하세요", hydro_reg_unique, index=None)
    ca_gr_input = None
    ca_ty_input = None
    car_input = None
    df_car = ts.select(
        f"""
        SELECT name as '이름',
            company as '회사',
            car_grade as '차급',
            car_type as '차종',
            fuel_effi as '연비',
            car_price as '가격',
            fuel_price_100km as '100km당연료비'
        FROM car_prop_elec_hydro
        WHERE POWER="{po_input}"
        ORDER BY fuel_price_100km asc
        """
    )
    df_sub = ts.select(
        f"""
    SELECT subside_2023 as '해당지역보조금'
    FROM hydro_subside
    WHERE reg_div="{reg_input}"
    """
    )
# elif po_input == '전기':
else:
    searchtable = "elec_subside"
    reg_input = st.selectbox("지역을 선택하세요", elec_reg_unique, index=None)

    ca_gr_input = st.selectbox("원하는 차급을 선택하세요", car_grade, index=None)

    ca_ty_input = st.selectbox("원하는 차종을 선택하세요", car_type, index=None)

    car_input = st.selectbox("원하는 브랜드를 선택하세요", company, index=None)
    # name,company, car_grade,car_type, fuel_effi, car_price, fuel_price_100km
    df_car = ts.select(
        f"""
    SELECT name as '이름',
            company as '회사',
            car_grade as '차급',
            car_type as '차종',
            fuel_effi as '연비',
            car_price as '가격',
            fuel_price_100km as '100km당연료비'
    FROM car_prop_elec_hydro
    WHERE POWER="{po_input}" AND car_grade="{ca_gr_input}" AND car_type="{ca_ty_input}" AND company="{car_input}"
    ORDER BY fuel_price_100km asc
    """
    )
    df_sub = ts.select(
        f"""
    SELECT subside_2023 as '해당지역보조금'
    FROM {searchtable}
    WHERE reg_div="{reg_input}"
    """
    )
# st.write(f'사용자입력값: {reg_input, ca_gr_input, ca_ty_input, car_input, po_input}')

st.subheader("조회 결과")
st.write(df_car)
st.write(df_sub)
