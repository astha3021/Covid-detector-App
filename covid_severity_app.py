import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from streamlit import caching
import SessionState
import requests
from PIL import Image

import sqlite3
conn = sqlite3.connect('feedback.db')
c = conn.cursor()
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS feedback(date_submitted DATE, Q1 TEXT, Q2 INTEGER, Q3 INTEGER, Q4 TEXT)')

def add_feedback(date_submitted, Q1, Q2, Q3, Q4):
    c.execute('INSERT INTO feedback (date_submitted,Q1, Q2, Q3, Q4) VALUES (?,?,?,?,?)',(date_submitted,Q1, Q2, Q3, Q4))
    conn.commit()
session = SessionState.get(run_id=0)

model = pickle.load(open("rf_model.pkl","rb"))

def load_data():
    df = pd.read_csv('Covid Datasets.csv')
    return df

data = load_data()
def predict_severity(prediction_value):
    input = np.array([prediction_value])
    predict = model.predict_proba(input)
    pred = '{0:.{1}f}'.format(predict[0][0], 5)
    return float(pred)
    return predict
   
    
def main():
    st.set_page_config(page_title="Covid 19 App🈸")
    st.title("Coronavirus Severity Self Assesement✅")
    base="light"
    
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.markdown("""
    <style>
    .title{
            font-weight: bold;
            font-size: 25px;
            color: blue;
            margin: 1.5rem 0px 0.5rem;
            padding: 0.5em 0px 0.25em;
            line-height: 1;
            position: relative;
            flex: 1 1 0%;    
     }
    </style>
    """, unsafe_allow_html=True)

    activities = ['Detect Covid','Analytics Dashboard','Give Feedback']
    option = st.sidebar.selectbox('Menu',activities)
    st.write('\n')
    st.sidebar.title("About")
    st.write('\n')
    st.write('\n')
    st.sidebar.info('This app is developed by Astha. Symptoms of COVID-19 can vary from mild to severe and often overlap with other illnesses, which makes it difficult to diagnose people without a test. This app aims to provide self-assessment test that will identify the severity of the symptoms and advise whether you should get tested or not.')
    
    symptoms_list = ['Breathing Problem','Fever','Dry Cough','Sore Throat','Running Nose','Asthma','Chronic Lung Disease','Headache','Heart Disease','Diabetes','Hyper Tension','Fatigue','Gastrointestinal','Abroad travel','Contact with COVID Patient','Attended Large Gathering','Visited Public Exposed Places','Family working inpublic exposed places']
    
    if option == 'Detect Covid':
        
        st.markdown('<p class= "title">\U0001F637 COVID-19 SEVERITY DETECTION MODEL \U0001F637 </p>',unsafe_allow_html=True)
        st.write("\n")
        st.subheader("Are you experiencing any of the following symtoms ?: \u2713 ")
        symptoms = st.multiselect('',[*symptoms_list],key='symptoms')
     
        prediction_value = ['0' for i in range(0,18)]
        
        for i in symptoms:
            index = symptoms_list.index(i)
            prediction_value[index] = '1'
            
        st.write('\n')
        
        columns = st.beta_columns((1,2))
        
        if columns[0].button('Predict 🔮'):
            st.write('\n')
            
            result = predict_severity(prediction_value)
            result = abs(1-result)
            output = '{0:.2f}'.format(result*100)
            
            if (result) > 0.45:
                 st.error('The probability of being COVID positive is {} % \n ⚠️ You are possibily covid positive , please confer with your doctor '.format(output))
            else:
                st.success('The probability of being COVID positive is {} %, It is unlikely that you are covid postive🙃'.format(output))
                st.info('if you still have doubts , please contact your physician')
                
        if columns[1].button('Reset 🔂'):
            session.run_id += 1
            
        st.write('\n\n\n')
        st.markdown('<p class="title">State Helpline Numbers ☎️</p>', unsafe_allow_html=True)
        
        dfhelp = pd.read_excel("helplineNumbers.xlsx")

        helpStates = dfhelp["State/UT"]
        helplineNo = dfhelp["HelplineNo"]

        
        st.write("\n")

        selectedState = st.selectbox("Choose State 🗺️ ", helpStates)
        colh = st.beta_columns(2)
        
        st.write("\n")
        st.write("\n")
        colh[0].subheader("State")
        colh[1].subheader("Helpline Numbers")
        colh[0].write('\n')
        colh[1].write('\n')
        for i,j in zip(helpStates,helplineNo):
            if selectedState == i:
                colh[0].write(f'{i}')
                colh[1].write(f'{j}')


        st.write("\n\n\n\n")
        
    if option == 'Analytics Dashboard':
        st.markdown('<p class= "title">Welcome To Data Visualization 📊</p>',unsafe_allow_html=True)
        st.write("\n")
        st.subheader('Feature Importance built-in the Random Forest algorithm , Bar Graph')
        image_bar = Image.open('feature_imp_sorted_bar.png')
        st.image(image_bar,use_column_width=True)
        
        st.subheader('Feature Importance Computed with SHAP Values')
        image_shap = Image.open('shap_feature_imp.png')
        st.image(image_shap,use_column_width=True)
        
        st.subheader('Permutation Based Feature Importance')
        image_permutation = Image.open('permutation_imp_.png')
        st.image(image_permutation,use_column_width=True)
        
    if option == 'Give Feedback':
        st.title('Feedback Form')
        st.markdown('<p class= "title">Please Provide Your Valuable Feedback 🔆</p>',unsafe_allow_html=True)
        d = st.date_input("Today's date",None, None, None, None)
        question_1 = st.text_input('What is your name?')
        st.write('You selected:', question_1)
    
        question_2 = st.slider('What is your age?', 10,85)
        st.write('You selected:', question_2) 

        question_3 = st.slider('Overall, how happy are you with the app? (5 being very happy and 1 being very dissapointed)',                                     1,5,1)
        st.write('You selected:', question_3)
        
        question_4 = st.text_input('What could have been better?', max_chars=50)

    if st.button("Submit feedback"):
        create_table()
        add_feedback(d, question_1, question_2, question_3, question_4)
        st.success("Feedback submitted")
       
        
 
    
if __name__=='__main__':
    main()
