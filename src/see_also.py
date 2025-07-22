import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer, util
import torch
import os
import json

load_dotenv()
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
DBNAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"
engine = create_engine(DATABASE_URL)

HEADINGS_TABLE = "subjects"
TOP_K = 20

#Load headings
df = pd.read_sql(f"SELECT id, main_heading, subheading, sub_subheading FROM {HEADINGS_TABLE}", engine)

#Combine into full heading
def combine(row):
    parts = [row["main_heading"], row["subheading"], row["sub_subheading"]]
    return " -- ".join([p for p in parts if p and p.strip() != ""])

df["full_heading"] = df.apply(combine, axis=1)

#Normalize heading for dupe detection and remove years
def normalize(heading):
    return ''.join([c for c in heading if not c.isdigit()])

df["normalized"] = df["full_heading"].apply(normalize)

#Generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df["full_heading"].tolist(), convert_to_tensor=True)

#Compute semantic see alsos
see_alsos_col = []
for idx, emb in enumerate(embeddings):
    sims = util.pytorch_cos_sim(emb, embeddings)[0]
    top_indices = torch.topk(sims, k=TOP_K + 1).indices

    current_norm = df.iloc[idx]["normalized"]
    current_id = df.iloc[idx]["id"]

    matches = []
    for i in top_indices:
        i = int(i)
        if i == idx:
            continue
        if df.iloc[i]["normalized"] == current_norm:
            continue
        match = df.iloc[i]["full_heading"]
        if match not in matches:
            matches.append(match)
        if len(matches) == 10:
            break

    see_alsos_col.append(matches)

# Add column to DataFrame and write to DB
df["see_alsos"] = see_alsos_col
df_to_write = df[["id", "see_alsos"]].copy()
df_to_write["see_alsos"] = df_to_write["see_alsos"].apply(json.dumps)

# Update the subjects table with this column
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS see_alsos TEXT"))
    for _, row in df_to_write.iterrows():
        conn.execute(
            text(f"""
            UPDATE subjects
            SET see_alsos = :see_alsos
            WHERE id = :id
            """),
            {"see_alsos": row["see_alsos"], "id": row["id"]}
        )

print("see_alsos column added to 'subjects' table.")