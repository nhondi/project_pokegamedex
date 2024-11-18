import matplotlib.pyplot as plt
import streamlit as st

def plot_pie_chart(data, title):
    """Render a pie chart using matplotlib."""
    fig, ax = plt.subplots()
    ax.pie(data.values, labels=data.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title(title)
    st.pyplot(fig)
