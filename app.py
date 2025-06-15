import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="Prediksi Dropout Mahasiswa", layout="wide")

@st.cache_resource
def load_model():
    with open("rf_model.pkl", "rb") as f:
        model, feature_names = pickle.load(f)
    return model, feature_names

model, feature_names = load_model()

def build_selectbox(label, options_dict):
    return st.selectbox(label, options=list(options_dict.keys()), format_func=lambda x: options_dict[x])

def preprocess_input_raw(raw):

    # Mapping kategori
    edu_map = {'Basic': 0, 'Secondary': 1, 'Higher': 2, 'Other': 3}
    grade_map = {'Very Low': 0, 'Low': 1, 'High': 2, 'Very High': 3}
    age_map = {'<18': 0, '18-21': 1, '22-25': 2, '>25': 3}
    binary_map = {'Local': 0, 'Foreign': 1, 'Officer': 0, 'Labor': 1, 'Other': 2}
    course_map = {
        'Engineering/Tech': 0, 'Arts/Design': 1, 'Health': 2,
        'Social Sciences': 3, 'Business': 4, 'Other': 5
    }
    app_mode_map = {
        'Regular': 0, 'Special': 1, 'International': 2,
        'Transfer': 3, 'Other': 4, 'Unknown': 5
    }

    def simplify_application_mode(mode):
        if mode in [1, 17, 18]:
            return 'Regular'
        elif mode in [2, 5, 10, 16]:
            return 'Special'
        elif mode in [15, 57]:
            return 'International'
        elif mode in [42, 43, 51, 53]:
            return 'Transfer'
        elif mode in [26, 27, 39, 44]:
            return 'Other'
        return 'Unknown'

    def simplify_edu(code):
        if code in [19, 37, 38, 35, 36]:
            return 'Basic'
        elif code in [1, 9, 10, 12, 14, 15, 22, 26, 27, 29, 30]:
            return 'Secondary'
        elif code in [2, 3, 4, 5, 6, 40, 41, 42, 43, 44]:
            return 'Higher'
        return 'Other'

    def simplify_nacionality(code):
        return 'Local' if code == 1 else 'Foreign'

    def simplify_admission_grade(g):
        if g <= 117.9:
            return 'Very Low'
        elif g <= 126.1:
            return 'Low'
        elif g <= 134.8:
            return 'High'
        else:
            return 'Very High'
        
    def simplify_sem1_grade(val):
        if val <= 11.0:
            return 'Very Low'
        elif val <= 12.29:
            return 'Low'
        elif val <= 13.4:
            return 'High'
        else:
            return 'Very High'

    def simplify_sem2_grade(val):
        if val <= 10.75:
            return 'Very Low'
        elif val <= 12.2:
            return 'Low'
        elif val <= 13.33:
            return 'High'
        else:
            return 'Very High'

    def simplify_prev_qual_grade(val):
        if val <= 125:
            return 'Very Low'
        elif val <= 133.1:
            return 'Low'
        elif val <= 140:
            return 'High'
        else:
            return 'Very High'

    def simplify_age(age):
        if age < 18:
            return '<18'
        elif age <= 21:
            return '18-21'
        elif age <= 25:
            return '22-25'
        else:
            return '>25'

    def occupation_group(code):
        officer = {1, 2, 3, 4, 112, 114, 121, 122, 123, 124, 131, 132, 134, 135, 141, 143, 144}
        labor = {5, 6, 7, 8, 9, 10, 151, 152, 153, 154, 161, 163, 171, 172, 174, 175, 181, 182, 183, 191, 192, 193, 194, 195}
        if code in officer:
            return 'Officer'
        elif code in labor:
            return 'Labor'
        return 'Other'

    def simplify_course(code):
        if code in [33, 9119, 9130]:
            return 'Engineering/Tech'
        elif code in [171, 9070, 9773]:
            return 'Arts/Design'
        elif code in [9500, 9556, 9085]:
            return 'Health'
        elif code in [8014, 9238, 9853]:
            return 'Social Sciences'
        elif code in [9147, 9991, 9254]:
            return 'Business'
        return 'Other'

    def encode(val, mapping):
        return mapping.get(val, 0)

    return {
        'Previous_qualification': encode(simplify_edu(raw['Previous_qualification']), edu_map),
        'Mothers_qualification': encode(simplify_edu(raw['Mothers_qualification']), edu_map),
        'Fathers_qualification': encode(simplify_edu(raw['Fathers_qualification']), edu_map),
        'Admission_grade': encode(simplify_admission_grade(raw['Admission_grade']), grade_map),
        'Curricular_units_1st_sem_grade': encode(simplify_sem1_grade(raw['Curricular_units_1st_sem_grade']), grade_map),
        'Curricular_units_2nd_sem_grade': encode(simplify_sem2_grade(raw['Curricular_units_2nd_sem_grade']), grade_map),
        'Previous_qualification_grade': encode(simplify_prev_qual_grade(raw['Previous_qualification_grade']), grade_map),
        'Age_at_enrollment': encode(simplify_age(raw['Age_at_enrollment']), age_map),
        'Nacionality': encode(simplify_nacionality(raw['Nacionality']), binary_map),
        'Fathers_occupation': encode(occupation_group(raw['Fathers_occupation']), binary_map),
        'Mothers_occupation': encode(occupation_group(raw['Mothers_occupation']), binary_map),
        'Course': encode(simplify_course(raw['Course']), course_map),
        'Application_mode': encode(simplify_application_mode(raw['Application_mode']), app_mode_map)
    }

st.title("🎓 Prediksi Dropout Mahasiswa")
st.write("Silakan masukkan data dengan sesuai.")

with st.form("form_input"):
    col1, col2, col3 = st.columns(3)

    with col1:
        marital_dict = {
            1: "#1 Single", 2: "#2 Married", 3: "#3 Widower", 4: "#4 Divorced",
            5: "#5 Facto Union", 6: "#6 Legally Separated"
        }
        Marital_status = build_selectbox("Status Pernikahan", marital_dict)

        app_mode_dict = {
            1: "#1 1st Phase - General", 2: "#2 Ordinance 612/93", 5: "#5 Special - Azores", 7: "#7 Holders of other higher courses", 10: "#10 Ordinance 854-B/99",
            15: "#15 International Student", 16: "#16 1st phase - special contingent", 17: "#17 2nd Phase", 18: "#18 3rd Phase", 26: "#26 Ordinance No. 533-A/99, item b2",
            27: "#27 Ordinance No. 533-A/99, item b3", 39: "#39 Over 23 years old", 42: "#42 Transfer", 43: "#43 Change of course", 44: "#44 Technological specialization diploma holders",
            51: "#51 Change of institution/course", 53: "#53 Short cycle diploma holders", 57: "#57 Change of institution/course (International)"
        }
        Application_mode = build_selectbox("Application Mode", app_mode_dict)

        Application_order = st.number_input("Urutan Aplikasi", 0, 9, 1)
        course_dict = {
            33: "#33 Biofuel Production Technologies",
            171: "#171 Animation and Multimedia Design",
            8014: "#8014 Social Service (evening attendance)",
            9003: "#9003 Agronomy",
            9070: "#9070 Communication Design",
            9085: "#9085 Veterinary Nursing",
            9119: "#9119 Informatics Engineering",
            9130: "#9130 Equinculture",
            9147: "#9147 Management",
            9238: "#9238 Social Service",
            9254: "#9254 Tourism",
            9500: "#9500 Nursing",
            9556: "#9556 Oral Hygiene",
            9670: "#9670 Advertising and Marketing Management",
            9773: "#9773 Journalism and Communication",
            9853: "#9853 Basic Education",
            9991: "#9991 Management (evening attendance)"
        }
        Course = build_selectbox("Program Studi", course_dict)
        previous_qualification_dict = {
            1: "#1 Secondary education",
            2: "#2 Higher education - bachelor's degree",
            3: "#3 Higher education - degree",
            4: "#4 Higher education - master's",
            5: "#5 Higher education - doctorate",
            6: "#6 Frequency of higher education",
            9: "#9 12th year of schooling - not completed",
            10: "#10 11th year of schooling - not completed",
            12: "#12 Other 11th year of schooling",
            14: "#14 10th year of schooling",
            15: "#15 10th year of schooling - not completed",
            19: "#19 Basic education 3rd cycle (9th/10th/11th year) or equiv.",
            38: "#38 Basic education 2nd cycle (6th/7th/8th year) or equiv.",
            39: "#39 Technological specialization course",
            40: "#40 Higher education - degree (1st cycle)",
            42: "#42 Professional higher technical course",
            43: "#43 Higher education - master (2nd cycle)"
        }
        Previous_qualification = build_selectbox("Kualifikasi Sebelumnya", previous_qualification_dict)
        Previous_qualification_grade = st.number_input("Nilai Kualifikasi Sebelumnya", 95.0, 190.0, 120.0)
        nacionality_dict = {
            1: "#1 Portuguese",
            2: "#2 German",
            6: "#6 Spanish",
            11: "#11 Italian",
            13: "#13 Dutch",
            14: "#14 English",
            17: "#17 Lithuanian",
            21: "#21 Angolan",
            22: "#22 Cape Verdean",
            24: "#24 Guinean",
            25: "#25 Mozambican",
            26: "#26 Santomean",
            32: "#32 Turkish",
            41: "#41 Brazilian",
            62: "#62 Romanian",
            100: "#100 Moldova (Republic of)",
            101: "#101 Mexican",
            103: "#103 Ukrainian",
            105: "#105 Russian",
            108: "#108 Cuban",
            109: "#109 Colombian"
        }
        Nacionality = build_selectbox("Kebangsaan", nacionality_dict)
        parent_qualification_dict = {
            1: "#1 Secondary Education - 12th Year of Schooling or Eq.",
            2: "#2 Higher Education - Bachelor's Degree",
            3: "#3 Higher Education - Degree",
            4: "#4 Higher Education - Master's",
            5: "#5 Higher Education - Doctorate",
            6: "#6 Frequency of Higher Education",
            9: "#9 12th Year of Schooling - Not Completed",
            10: "#10 11th Year of Schooling - Not Completed",
            11: "#11 7th Year (Old)",
            12: "#12 Other - 11th Year of Schooling",
            14: "#14 10th Year of Schooling",
            18: "#18 General commerce course",
            19: "#19 Basic Education 3rd Cycle (9th/10th/11th Year) or Equiv.",
            22: "#22 Technical-professional course",
            26: "#26 7th year of schooling",
            27: "#27 2nd cycle of the general high school course",
            29: "#29 9th Year of Schooling - Not Completed",
            30: "#30 8th year of schooling",
            34: "#34 Unknown",
            35: "#35 Can't read or write",
            36: "#36 Can read without having a 4th year of schooling",
            37: "#37 Basic education 1st cycle (4th/5th year) or equiv.",
            38: "#38 Basic Education 2nd Cycle (6th/7th/8th Year) or Equiv.",
            39: "#39 Technological specialization course",
            40: "#40 Higher education - degree (1st cycle)",
            41: "#41 Specialized higher studies course",
            42: "#42 Professional higher technical course",
            43: "#43 Higher Education - Master (2nd cycle)",
            44: "#44 Higher Education - Doctorate (3rd cycle)"
        }
        Mothers_qualification = build_selectbox("Kualifikasi Ibu", parent_qualification_dict)
        Fathers_qualification = build_selectbox("Kualifikasi Ayah", parent_qualification_dict)
        parent_occupation_dict = {
            0: "#0 Student",
            1: "#1 Representatives of the Legislative Power and Executive Bodies, Directors, Directors and Executive Managers",
            2: "#2 Specialists in Intellectual and Scientific Activities",
            3: "#3 Intermediate Level Technicians and Professions",
            4: "#4 Administrative staff",
            5: "#5 Personal Services, Security and Safety Workers and Sellers",
            6: "#6 Farmers and Skilled Workers in Agriculture, Fisheries and Forestry",
            7: "#7 Skilled Workers in Industry, Construction and Craftsmen",
            8: "#8 Installation and Machine Operators and Assembly Workers",
            9: "#9 Unskilled Workers",
            10: "#10 Armed Forces Professions",
            90: "#90 Other Situation",
            99: "#99 (blank)",
            122: "#122 Health professionals",
            123: "#123 Teachers",
            125: "#125 Specialists in information and communication technologies (ICT)",
            131: "#131 Intermediate level science and engineering technicians and professions",
            132: "#132 Technicians and professionals, of intermediate level of health",
            134: "#134 Intermediate level technicians from legal, social, sports, cultural and similar services",
            141: "#140 Office workers, secretaries in general and data processing operators",
            143: "#143 Data, accounting, statistical, financial services and registry-related operators",
            144: "#144 Other administrative support staff",
            151: "#151 Personal service workers",
            152: "#152 Sellers",
            153: "#153 Personal care workers and the like",
            171: "#171 Skilled construction workers and the like, except electricians",
            173: "#173 Skilled workers in printing, precision instrument manufacturing, jewelers, artisans and the like",
            175: "#175 Workers in food processing, woodworking, clothing and other industries and crafts",
            191: "#191 Cleaning workers",
            192: "#192 Unskilled workers in agriculture, animal production, fisheries and forestry",
            193: "#193 Unskilled workers in extractive industry, construction, manufacturing and transport",
            194: "#194 Meal preparation assistants"
        }
        Mothers_occupation = build_selectbox("Pekerjaan Ibu", parent_occupation_dict)
        Fathers_occupation = build_selectbox("Pekerjaan Ayah", parent_occupation_dict)
        Age_at_enrollment = st.number_input("Usia Saat Masuk", 15, 60, 15)

    with col2:
        # Semester 1
        Curricular_units_1st_sem_credited = st.number_input(
            "Curricular_units_1st_sem_credited", min_value=0, max_value=20, step=1
        )
        Curricular_units_1st_sem_enrolled = st.number_input(
            "Curricular_units_1st_sem_enrolled", min_value=0, max_value=26, step=1
        )
        Curricular_units_1st_sem_evaluations = st.number_input(
            "Curricular_units_1st_sem_evaluations", min_value=0, max_value=45, step=1
        )
        Curricular_units_1st_sem_approved = st.number_input(
            "Curricular_units_1st_sem_approved", min_value=0, max_value=26, step=1
        )
        Curricular_units_1st_sem_grade = st.number_input(
            "Curricular_units_1st_sem_grade", min_value=0.0, max_value=20.0, step=0.1
        )
        Curricular_units_1st_sem_without_evaluations = st.number_input(
            "Curricular_units_1st_sem_without_evaluations", min_value=0, max_value=12, step=1
        )

        # Semester 2
        Curricular_units_2nd_sem_credited = st.number_input(
            "Curricular_units_2nd_sem_credited", min_value=0, max_value=19, step=1
        )
        Curricular_units_2nd_sem_enrolled = st.number_input(
            "Curricular_units_2nd_sem_enrolled", min_value=0, max_value=23, step=1
        )
        Curricular_units_2nd_sem_evaluations = st.number_input(
            "Curricular_units_2nd_sem_evaluations", min_value=0, max_value=33, step=1
        )
        Curricular_units_2nd_sem_approved = st.number_input(
            "Curricular_units_2nd_sem_approved", min_value=0, max_value=20, step=1
        )
        Curricular_units_2nd_sem_grade = st.number_input(
            "Curricular_units_2nd_sem_grade", min_value=0.0, max_value=20.0, step=0.1
        )
        Curricular_units_2nd_sem_without_evaluations = st.number_input(
            "Curricular_units_2nd_sem_without_evaluations", min_value=0, max_value=12, step=1
        )
        
    with col3:
        Admission_grade = st.number_input("Admission Grade", 0.0, 200.0, 130.0)
        Previous_qualification_grade = st.number_input("Nilai Kualifikasi Sebelumnya", 0.0, 200.0, 140.0)
        Unemployment_rate = st.number_input(
            "Unemployment_rate",
            min_value=7.6,
            max_value=16.2,
            value=10.0,
            step=0.1
        )
        Inflation_rate = st.number_input(
            "Inflation_rate",
            min_value=-0.8,
            max_value=3.7,
            value=1.0,
            step=0.1
        )
        GDP = st.number_input(
            "GDP",
            min_value=-4.06,
            max_value=3.51,
            value=0.0,
            step=0.1
        )
        Daytime_evening_attendance = st.radio("Kehadiran", [0, 1], format_func=lambda x: "Daytime" if x == 0 else "Evening", horizontal=True)
        Debtor = st.radio("Memiliki Hutang?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
        Scholarship_holder = st.radio("Penerima Beasiswa?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
        Displaced = st.radio("Mahasiswa Tergusur?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
        Gender = st.radio("Jenis Kelamin", [0, 1], format_func=lambda x: "Female" if x == 0 else "Male", horizontal=True)
        Tuition_fees_up_to_date = st.radio("SPP Terbayar?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
        Educational_special_needs = st.radio("Berkebutuhan Khusus?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)
        International = st.radio("Mahasiswa International?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes", horizontal=True)

    submitted = st.form_submit_button("Prediksi")

if submitted:
    raw_input = {
        'Marital_status': Marital_status, 
        'Application_mode': Application_mode, 
        'Application_order': Application_order, 
        'Course': Course, 
        'Daytime_evening_attendance': Daytime_evening_attendance, 
        'Previous_qualification': Previous_qualification, 
        'Previous_qualification_grade': Previous_qualification_grade, 
        'Nacionality': Nacionality, 
        'Mothers_qualification': Mothers_qualification, 
        'Fathers_qualification': Fathers_qualification, 
        'Mothers_occupation': Mothers_occupation, 
        'Fathers_occupation': Fathers_occupation, 
        'Admission_grade': Admission_grade, 
        'Displaced': Displaced, 
        'Educational_special_needs': Educational_special_needs, 
        'Debtor': Debtor, 
        'Tuition_fees_up_to_date': Tuition_fees_up_to_date, 
        'Gender': Gender, 
        'Scholarship_holder': Scholarship_holder, 
        'Age_at_enrollment': Age_at_enrollment, 
        'International': International, 
        'Curricular_units_1st_sem_credited': Curricular_units_1st_sem_credited, 
        'Curricular_units_1st_sem_enrolled': Curricular_units_1st_sem_enrolled, 
        'Curricular_units_1st_sem_evaluations': Curricular_units_1st_sem_evaluations, 
        'Curricular_units_1st_sem_approved': Curricular_units_1st_sem_approved, 
        'Curricular_units_1st_sem_grade': Curricular_units_1st_sem_grade, 
        'Curricular_units_1st_sem_without_evaluations': Curricular_units_1st_sem_without_evaluations, 
        'Curricular_units_2nd_sem_credited': Curricular_units_2nd_sem_credited, 
        'Curricular_units_2nd_sem_enrolled': Curricular_units_2nd_sem_enrolled, 
        'Curricular_units_2nd_sem_evaluations': Curricular_units_2nd_sem_evaluations, 
        'Curricular_units_2nd_sem_approved': Curricular_units_2nd_sem_approved, 
        'Curricular_units_2nd_sem_grade': Curricular_units_2nd_sem_grade, 
        'Curricular_units_2nd_sem_without_evaluations': Curricular_units_2nd_sem_without_evaluations, 
        'Unemployment_rate': Unemployment_rate, 
        'Inflation_rate': Inflation_rate, 
        'GDP': GDP
    }

    features = preprocess_input_raw(raw_input)

    features.update({
        'Marital_status': Marital_status, 
        'Application_order': Application_order, 
        'Daytime_evening_attendance': Daytime_evening_attendance, 
        'Displaced': Displaced, 
        'Educational_special_needs': Educational_special_needs, 
        'Debtor': Debtor, 
        'Tuition_fees_up_to_date': Tuition_fees_up_to_date, 
        'Gender': Gender, 
        'Scholarship_holder': Scholarship_holder, 
        'International': International, 
        'Curricular_units_1st_sem_credited': Curricular_units_1st_sem_credited, 
        'Curricular_units_1st_sem_enrolled': Curricular_units_1st_sem_enrolled, 
        'Curricular_units_1st_sem_evaluations': Curricular_units_1st_sem_evaluations, 
        'Curricular_units_1st_sem_approved': Curricular_units_1st_sem_approved, 
        'Curricular_units_1st_sem_without_evaluations': Curricular_units_1st_sem_without_evaluations, 
        'Curricular_units_2nd_sem_credited': Curricular_units_2nd_sem_credited, 
        'Curricular_units_2nd_sem_enrolled': Curricular_units_2nd_sem_enrolled, 
        'Curricular_units_2nd_sem_evaluations': Curricular_units_2nd_sem_evaluations, 
        'Curricular_units_2nd_sem_approved': Curricular_units_2nd_sem_approved, 
        'Curricular_units_2nd_sem_without_evaluations': Curricular_units_2nd_sem_without_evaluations, 
        'Unemployment_rate': Unemployment_rate, 
        'Inflation_rate': Inflation_rate, 
        'GDP': GDP
    })

    input_df = pd.DataFrame([features])[feature_names]

    prediction = model.predict(input_df)[0]

    st.success(f"🎯 Hasil Prediksi: {'🔴 Dropout' if prediction == 1 else '🟢 Lulus'}")