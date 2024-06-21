import streamlit as st
import nltk
from pyresparser import ResumeParser
from streamlit_tags import st_tags
import time
from recommended_skills import *
import re
import PyPDF2
import os

nltk.download('stopwords')


def get_recommended_skills(job_type):
    if job_type == "Data Science":
        return ds_skills
    elif job_type == "Web Development":
        return web_skills
    elif job_type == "Android Development":
        return android_skills
    elif job_type == "iOS Development":
        return ios_skills
    elif job_type == "UI-UX Development":
        return uiux_skills
    else:
        return []


def extract_lines_with_college(file):
    lines_with_college = []
    pdf_reader = PyPDF2.PdfReader(file)
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text = page_obj.extract_text()
        # Add spaces between words
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        lines = text.split('\n')
        for line in lines:
            if 'university' in line.lower() or 'institute' in line.lower() or 'center' in line.lower():
                lines_with_college.append(line)
    return lines_with_college


def extract_lines_with_degree(file):
    education = []
    pdf_reader = PyPDF2.PdfReader(file)
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text = page_obj.extract_text()
        # Add spaces between words
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        education_keywords = ['Bsc', 'B. Pharmacy', 'B Pharmacy', 'Msc', 'M. Pharmacy', 'Ph.D', 'Bachelor Of Science',
                              'Master']
        for keyword in education_keywords:
            pattern = r"(?i)\b{}\b".format(re.escape(keyword))
            match = re.search(pattern, text)
            if match:
                education.append(match.group())
    return education


def extractdetails(file):
    achievement, hobbies, projects, objec, dec = 0, 0, 0, 0, 0
    pdf_reader = PyPDF2.PdfReader(file)

    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text = page_obj.extract_text()
        lines = text.split('\n')
        for line in lines:
            if 'achievements' in line.lower():
                achievement = 1
            if 'experience' in line.lower():
                hobbies = 1  # Adjusting this to experience instead of hobbies
            if 'projects' in line.lower():
                projects = 1
            if 'career objective' in line.lower():
                objec = 1
            if 'declaration' in line.lower():
                dec = 1
    return achievement, hobbies, projects, objec, dec


def run():
    st.title("Smart Resume Analyser")
    st.markdown('# Upload your resume, and get smart recommendations based on it.')

    if 'resume_uploaded' not in st.session_state:
        job_type = st.selectbox("Select the type of job you are interested in:",
                                ["Data Science", "Web Development", "Android Development",
                                 "iOS Development", "UI-UX Development"])

        # Store the selected job type in session state
        st.session_state.job_type = job_type

    pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])

    if pdf_file is not None:
        st.session_state.resume_uploaded = True
        a, b, c, d, e = extractdetails(pdf_file)
        print(a, b, c, d, e)

        with st.spinner('Analyzing the resume...'):
            resume_data = ResumeParser(pdf_file).get_extracted_data()

        if resume_data:
            st.header("**Resume Analysis**")
            st.subheader("**Your Basic info**")

            # Extract file name without extension
            default_name = os.path.splitext(pdf_file.name)[0]

            try:

                st.text('Name: ' + default_name)

                lines = extract_lines_with_college(pdf_file)
                for line in lines:
                    st.text("College: " + line)

                degrees = extract_lines_with_degree(pdf_file)
                for line in degrees:
                    st.text("Degree: " + line)

                if 'email' in resume_data and resume_data['email'] is not None:
                    st.text('Email: ' + resume_data['email'])
                if 'mobile_number' in resume_data and resume_data['mobile_number'] is not None:
                    st.text('Contact: ' + resume_data['mobile_number'])
                if 'no_of_pages' in resume_data and resume_data['no_of_pages'] is not None:
                    st.text("Total Experience: " + str(resume_data["total_experience"]))
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
            except Exception as e:
                st.error("An error occurred: {}".format(e))

            cand_level = ''
            if 'skills' in resume_data:
                num_skills = len(resume_data['skills'])
                if num_skills < 5:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
                elif 5 <= num_skills < 10:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif num_skills >= 10:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',
                                unsafe_allow_html=True)
            else:
                cand_level = "Unknown"  # Set default level if no skills found
                st.warning("No skills found in the resume.")

            ## Skills Recommendation
            st.subheader("**Skills Recommendation💡**")
            ## Skill shows
            keywords = st_tags(label='### Skills that you have',
                               text='See our skills recommendation',
                               value=resume_data['skills'], key='1')

            recommended_skills = get_recommended_skills(st.session_state.job_type)

            # Display recommended skills
            if recommended_skills:
                recommended_keywords = st_tags(label='### Recommended skills for you',
                                               text='Here are Some Recommended Skills',
                                               value=recommended_skills, key='2')
            else:
                st.error("No recommended skills found for the selected job type.")

            # Calculate percentage of recommended skills mentioned in resume
            total_skills = len(recommended_skills)
            mentioned_skills = len(set(recommended_skills) & set(resume_data['skills']))
            percentage_mentioned = (mentioned_skills / total_skills) * 100

            # Rate the resume based on the percentage of skills mentioned
            st.subheader("**Resume Rating📊**")
            if percentage_mentioned >= 80:
                st.success(
                    "Your resume is highly relevant with a skill mention rate of {:.2f}%.".format(percentage_mentioned))
            elif percentage_mentioned >= 50:
                st.warning("Your resume is moderately relevant with a skill mention rate of {:.2f}%.".format(
                    percentage_mentioned))
            else:
                st.error(
                    "Your resume is less relevant with a skill mention rate of {:.2f}%.".format(percentage_mentioned))

            ### Number of skills mentioned
            st.subheader("**Number of Skills Mentioned🔍**")
            st.text("Number of skills mentioned in your resume: {}".format(len(resume_data['skills'])))

            ### Resume writing recommendation
            st.subheader("**Resume Tips & Ideas💡**")
            resume_score = 0
            if d == 1:
                resume_score += 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intention to the Recruiters.</h4>''',
                    unsafe_allow_html=True)

            if e == 1:
                resume_score += 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Declaration✍</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                    unsafe_allow_html=True)

            if b == 1:
                resume_score += 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                    unsafe_allow_html=True)

            if a == 1:
                resume_score += 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                    unsafe_allow_html=True)

            if c == 1:
                resume_score += 20
                st.markdown(
                    '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻</h4>''',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                    unsafe_allow_html=True)

            st.subheader("**Resume Score📝**")
            st.markdown(
                """
                <style>
                    .stProgress > div > div > div > div {
                        background-color: #d73b5c;
                    }
                </style>""",
                unsafe_allow_html=True,
            )
            my_bar = st.progress(0)
            score = 0
            for percent_complete in range(resume_score):
                score += 1
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1)
            st.success('** Your Resume Writing Score: ' + str(score) + '**')
            st.warning("** Note: This score is calculated based on the content that you have added in your Resume. **")


run()
