import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import numpy as np

def plot_pie_chart(data, title):
    """Render a pie chart using matplotlib."""
    fig, ax = plt.subplots()
    ax.pie(data.values, labels=data.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title(title)
    st.pyplot(fig)

def plot_scatter(data, x_col, y_col, title, x_label, y_label):
    """Render a scatter plot using matplotlib."""
    fig, ax = plt.subplots()
    ax.scatter(data[x_col], data[y_col], alpha=0.7, edgecolors='w')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    st.pyplot(fig)

def plot_histogram(data, column, title, x_label, bins=20):
    """Render a histogram using matplotlib."""
    fig, ax = plt.subplots()
    ax.hist(data[column], bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

def plot_bar(data, title, x_label, y_label):
    """Render a bar chart using matplotlib."""
    fig, ax = plt.subplots()
    ax.bar(data.index, data.values, color='lightgreen', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

def plot_box(data, column, title, y_label):
    """Render a box plot using matplotlib."""
    fig, ax = plt.subplots()
    ax.boxplot(data[column], vert=True, patch_artist=True, boxprops=dict(facecolor='skyblue', color='black'))
    ax.set_title(title)
    ax.set_ylabel(y_label)
    st.pyplot(fig)

def plot_grouped_bar(data, category_col, title, x_label, y_label):
    """Render a grouped bar chart."""
    grouped_counts = data[category_col].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped_counts.plot(kind="bar", ax=ax, color="lightcoral", edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    st.pyplot(fig)

def plot_radar(stats, labels, title):
    """Render a radar chart for base stats."""
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]  # Complete the circle
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color="blue", alpha=0.25)
    ax.plot(angles, stats, color="blue", linewidth=1)
    ax.set_yticks([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(title)
    st.pyplot(fig)

def plot_kde(data, column, title, x_label):
    """Render a KDE plot using seaborn."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.kdeplot(data[column], ax=ax, shade=True, color="skyblue")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Density")
    st.pyplot(fig)

def plot_average_bar(stats, title="Average Stats"):
    fig, ax = plt.subplots(figsize=(8,6))
    ax.bar(stats.index, stats.values, color='skyblue', edgecolor='black')
    ax.set_title(title)
    ax.set_ylabel("Average Value")
    ax.set_xlabel("Stat")
    st.pyplot(fig)

