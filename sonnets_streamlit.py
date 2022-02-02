import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt

st.title("Sonnet subsets")

df_counts = pd.read_csv('features/counts_df.csv',index_col="Unnamed: 0")
df_embedding = pd.read_csv('features/embeddings_df.csv',index_col="Unnamed: 0")

vector = "counts" # counts or "embedding"
vector = st.radio("Features based on:", ("Phoneme counts","Sound similarity"))

if vector == "Phoneme counts":
    df = df_counts
elif vector == "Sound similarity":
    df = df_embedding

subset_name = st.radio(
     "Subset to highlight",
    ("None","Marriage", "Dark Lady", "Rival Poet", "Love Triangle"))


# Subsets of interest
marriage = np.arange(0,17) #1-17
#Dark Lady: #127-52
dark_lady = np.arange(126,152)
#Rival poet: #78-80, 82-86
rival_poet = [77, 78, 79, 81, 82, 83, 84, 85]
#Love Triangle: #40-42, 133-4, 144
love_triangle = [39,40,41,132,133,143]
subset_names = ["Marriage", "Dark Lady", "Rival Poet", "Love Triangle"]

if subset_name == "Marriage":
    subset = marriage
elif subset_name =="Dark Lady":
    subset = dark_lady
elif subset_name == "Rival Poet":
    subset = rival_poet
elif subset_name == "Love Triangle":
    subset = love_triangle
else:
    subset = []
    
fig, ax = plt.subplots()
X = df.iloc[:,:-1].copy()
X = X.loc[0:154,:]
X = StandardScaler().fit_transform(X)
pca =  PCA(n_components=2).fit(X)
sonnets_embedded_pca = pca.transform(X)
sns.scatterplot(x = sonnets_embedded_pca[0:154,0],y=sonnets_embedded_pca[0:154,1],alpha=0.5,ax=ax)
sns.scatterplot(x = sonnets_embedded_pca[subset,0], y=sonnets_embedded_pca[subset,1],label=subset_name,ax=ax)
plt.xlabel("PC 1")
plt.ylabel("PC 2")
plt.axis("off")
plt.title(f'{vector}')
#plt.show()
st.pyplot(fig)
