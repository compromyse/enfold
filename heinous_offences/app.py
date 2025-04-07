import streamlit as st
from tinydb import TinyDB, Query

db = TinyDB('db.json')

st.title('Heinous Crime Lookup')

section = st.number_input('Section', value=0)

if section > 0:
    offence = db.search(Query().section == str(section))[0]
    st.subheader(offence['severity'])
    st.write(offence['section_text'])

    st.subheader('Minimum Punishment')
    st.write(offence['minimum_punishment'])

    st.subheader('Comments')
    st.write(offence['comment'])
