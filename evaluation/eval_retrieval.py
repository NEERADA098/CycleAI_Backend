"""Does the right knowledge chunk appear in the top 3 results?
Labels are your own judgment; review them before trusting the numbers."""
import chromadb
from chromadb.utils import embedding_functions

QUESTIONS = [
    ("How long should a normal menstrual cycle be?", "menstrual_cycle_normal"),
    ("Is it okay that my periods are irregular a year after starting?", "menarche_normal"),
    ("When do girls usually get their first period?", "menarche_normal"),
    ("My cramps start days before my period. Is that normal?", "dysmenorrhea_types"),
    ("What is the difference between normal and abnormal period pain?", "dysmenorrhea_types"),
    ("How many pads per day counts as heavy bleeding?", "heavy_bleeding"),
    ("I pass big clots, should I worry?", "heavy_bleeding"),
    ("What signs suggest PCOS?", "pcos_indicators"),
    ("I have acne on my jaw and long cycles. What could it be?", "pcos_indicators"),
    ("At what age does menopause usually happen?", "menopause_perimenopause"),
    ("I have hot flashes and irregular periods in my late 40s", "menopause_perimenopause"),
    ("When does ovulation happen in a 30 day cycle?", "ovulation_timing"),
    ("How do I work out my fertile days?", "ovulation_timing"),
    ("Can thyroid problems change my periods?", "thyroid_cycle_connection"),
    ("When should I see a doctor about my period?", "when_to_see_doctor"),
    ("My period has not come for three months", "when_to_see_doctor"),
    ("How can I ease period cramps at home?", "pain_management"),
    ("Is ibuprofen safe for period pain?", "pain_management"),
    ("How often should I change my pad?", "hygiene_basics"),
    ("How do I clean and dry cloth pads?", "hygiene_basics"),
    ("Can I cook or go to school during my period?", "stigma_and_normalcy"),
    ("Is period blood impure?", "stigma_and_normalcy"),
]

col = chromadb.PersistentClient(path="./knowledge_db").get_collection(
    "medical_knowledge", embedding_function=embedding_functions.DefaultEmbeddingFunction())
hit1 = hit3 = 0
rr = 0.0
for q, want in QUESTIONS:
    ids = col.query(query_texts=[q], n_results=3)["ids"][0]
    if ids and ids[0] == want: hit1 += 1
    if want in ids:
        hit3 += 1
        rr += 1 / (ids.index(want) + 1)
    else:
        print("MISS:", q, "| expected", want, "| got", ids)
n = len(QUESTIONS)
print(f"N={n}  hit@1={hit1/n:.2f}  hit@3={hit3/n:.2f}  MRR={rr/n:.2f}")
